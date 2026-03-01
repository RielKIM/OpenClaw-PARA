# OPERATIONS — Hub (PARA Hub)

**버전**: 4.0 | **날짜**: 2026-03-01 | **상태**: Design Phase

> Plugin 운영/배포: `docs/arch/HLD/plugin/OPERATIONS.md`

---

## 1. Hub 배포

> **Phase 1 (현재)**: Docker Compose — 단일 서버 배포
> **Phase 2+**: Kubernetes (EKS) — 수평 확장 시 마이그레이션

---

### 1.1 Phase 1 — Docker Compose 배포

#### docker-compose.yml

```yaml
version: "3.9"

services:
  nginx:
    image: nginx:1.25-alpine
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on: [gateway]
    networks: [hub_network]

  gateway:
    build: ./services/gateway
    environment:
      - JWT_SECRET=${JWT_SECRET}
      - POSTGRES_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/para_hub
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379
    depends_on: [postgres, redis]
    networks: [hub_network]

  matching:
    build: ./services/matching
    environment:
      - POSTGRES_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/para_hub
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379
    depends_on: [postgres, redis]
    networks: [hub_network]

  anonymizer:
    build: ./services/anonymizer
    networks: [hub_network]

  reputation:
    build: ./services/reputation
    environment:
      - POSTGRES_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/para_hub
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379
    depends_on: [postgres, redis]
    networks: [hub_network]

  content-store:
    build: ./services/content-store
    environment:
      - POSTGRES_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/para_hub
      - MINIO_ENDPOINT=minio:9000
      - MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY}
      - MINIO_SECRET_KEY=${MINIO_SECRET_KEY}
    depends_on: [postgres, minio]
    networks: [hub_network]

  fl-service:
    build: ./services/fl-service
    environment:
      - POSTGRES_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/para_hub
    depends_on: [postgres]
    networks: [hub_network]

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=para_hub
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-db:/docker-entrypoint-initdb.d
    networks: [hub_network]

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    networks: [hub_network]

  minio:
    image: minio/minio
    command: server /data --console-address ":9001"
    environment:
      - MINIO_ROOT_USER=${MINIO_ACCESS_KEY}
      - MINIO_ROOT_PASSWORD=${MINIO_SECRET_KEY}
    volumes:
      - minio_data:/data
    networks: [hub_network]

volumes:
  postgres_data:
  redis_data:
  minio_data:

networks:
  hub_network:
    driver: bridge
```

#### .env (예시)

```
JWT_SECRET=...
POSTGRES_USER=para_hub
POSTGRES_PASSWORD=...
REDIS_PASSWORD=...
MINIO_ACCESS_KEY=...
MINIO_SECRET_KEY=...
```

#### 실행 명령

```bash
# 빌드 및 실행
docker compose up --build -d

# 서비스 상태 확인
docker compose ps

# 로그 확인
docker compose logs -f gateway

# 중지
docker compose down

# 데이터 포함 완전 초기화
docker compose down -v
```

#### Phase 1 서버 사양 (권장)

| 항목 | 최소 | 권장 |
|------|------|------|
| CPU | 4 vCPU | 8 vCPU |
| RAM | 8 GB | 16 GB |
| 디스크 | 50 GB SSD | 200 GB SSD |
| OS | Ubuntu 22.04+ | Ubuntu 22.04+ |

---

### 1.2 Phase 2+ — Kubernetes 확장 (참조)

> 트래픽 증가 시 docker-compose에서 Kubernetes(EKS)로 마이그레이션.
> docker-compose.yml 서비스 정의를 기반으로 Helm 차트 변환.

```
AWS ALB  →  EKS 클러스터
  ├─ Gateway        (HPA: min 3 / max 20,  CPU 50%)
  ├─ Matching       (HPA: min 5 / max 30,  CPU 60%)
  ├─ Anonymizer     (HPA: min 3 / max 15,  CPU 70%)
  ├─ Reputation     (HPA: min 2 / max 10,  CPU 50%)
  ├─ Content Store  (HPA: min 2 / max 10,  CPU 50%)
  └─ FL Service     (HPA: min 2 / max 10,  MEM 70%)

데이터 계층 (매니지드 서비스로 교체)
  ├─ RDS PostgreSQL  (Multi-AZ)
  ├─ ElastiCache Redis  (클러스터)
  └─ S3  (버킷, MinIO → AWS S3 마이그레이션)
```

---

## 2. 보안 운영

### 키 관리

| 항목 | Phase 1 (Docker Compose) | Phase 2+ (Kubernetes) |
|------|--------------------------|----------------------|
| 시크릿 | `.env` 파일 (서버 로컬) | HashiCorp Vault / AWS Secrets Manager |
| RSA-4096 키 페어 | 컨테이너 볼륨 마운트 | Kubernetes Secret |
| TLS 인증서 | Let's Encrypt (certbot) | cert-manager 자동 갱신 |
| JWT 시크릿 | `.env` 환경변수 | Vault 자동 순환 |

### 네트워크 보안

- Nginx: 외부 → 내부 역방향 프록시, HTTPS 강제
- Docker 네트워크(`hub_network`): 컨테이너 간 격리, 외부 직접 접근 차단
- 데이터 서비스(postgres, redis, minio): 외부 포트 미노출 (내부 전용)
- Fail2ban: SSH 및 HTTPS 무차별 대입 차단

### 접근 제어

- OAuth 2.0: OpenClaw 계정 연동
- JWT 토큰 만료: 1시간
- Refresh Token: 30일
- API Rate Limit: 사용자당 100 req/min

---

## 3. 모니터링 및 알림

### 메트릭 목표

| 메트릭 | 경고 임계 | 심각 임계 |
|--------|-----------|-----------|
| Hub API 응답시간 | > 2초 | > 5초 |
| 검색 응답시간 | > 1초 | > 3초 |
| 에러율 | > 1% | > 5% |
| PII 감지율 | < 99% | < 95% |
| Hub 가용성 | < 99.9% | < 99% |

### Phase 1 모니터링 스택 (Docker Compose 추가)

```yaml
# docker-compose.monitoring.yml (선택 추가)
services:
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    networks: [hub_network]

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"   # 로컬 전용
    networks: [hub_network]

  loki:
    image: grafana/loki:latest
    networks: [hub_network]

  promtail:
    image: grafana/promtail:latest
    volumes:
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
    networks: [hub_network]
```

```bash
# 모니터링 스택 포함 실행
docker compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d
```

### 로깅

- 모든 API 요청/응답 로그 (Loki + Promtail → Grafana)
- PII 제거 파이프라인 이벤트
- 평판 점수 변경 이벤트
- 접근 제어 감사 로그
- FL 그래디언트 전송 이벤트

### 알림

- Phase 1: Grafana 알림 → 이메일 / Slack 웹훅
- Phase 2+: PagerDuty 에스컬레이션 추가

---

## 4. 백업 및 복구

### 백업 정책

| 데이터 | Phase 1 방식 | 백업 주기 | 보존 기간 |
|--------|-------------|-----------|-----------|
| PostgreSQL | `pg_dump` 크론잡 | 매일 | 30일 |
| PostgreSQL WAL | `pg_basebackup` | 매시간 | 7일 |
| MinIO (콘텐츠) | `mc mirror` (로컬 → 원격) | 매일 | 90일 |
| Redis | RDB 스냅샷 (`appendonly yes`) | 매시간 | 24시간 |

```bash
# PostgreSQL 일일 백업 크론잡 예시
0 2 * * * docker exec para_hub_postgres pg_dump -U para_hub para_hub | gzip > /backups/para_hub_$(date +%Y%m%d).sql.gz
```

### RTO / RPO

| 항목 | 목표 |
|------|------|
| RTO (Recovery Time Objective) | < 30분 |
| RPO (Recovery Point Objective) | < 1시간 |

---

## 5. 데이터 보존 및 삭제

### 자동 삭제 스케줄 (매일 실행)

```sql
-- 90일 미활동 공유 콘텐츠 삭제
DELETE FROM shared_content WHERE last_accessed < NOW() - INTERVAL '90 days';

-- 90일 초과 접근 로그 삭제
DELETE FROM access_logs WHERE accessed_at < NOW() - INTERVAL '90 days';

-- 6개월 미활동 평판 감소 (5%)
UPDATE users SET reputation_score = reputation_score * 0.95
WHERE last_active < NOW() - INTERVAL '180 days';
```

### 사용자 요청 삭제

- 콘텐츠 회수 요청 → 7일 내 삭제 (소프트 삭제 → 하드 삭제)
- 계정 삭제 요청 → 즉시 소프트 삭제, 30일 내 하드 삭제, 평판 이력 익명화
