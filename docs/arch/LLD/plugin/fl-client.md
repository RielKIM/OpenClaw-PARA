# FL Client — 상세 설계

**컴포넌트**: OpenClaw PARA Memory Plugin
**관련 요구사항**: FR-5 (Plugin 측)
**날짜**: 2026-03-01
**상태**: Draft (사용자 합의 전)

---

## 1. 책임

로컬 PARA 메모리에서 패턴을 학습하고, **원본 데이터를 디바이스 밖으로 내보내지 않고** 암호화된 그래디언트만 Hub로 전송한다. Hub에서 배포된 글로벌 모델을 수신하여 로컬 추론에 활용한다.

---

## 2. 인터페이스

```typescript
class FederatedLearningClient {
  // 로컬 훈련 + 그래디언트 제출 (백그라운드 실행)
  async runLocalTraining(category: string): Promise<TrainingResult>

  // Hub에서 최신 글로벌 모델 동기화
  async syncGlobalModel(): Promise<void>

  // 집계 통찰 쿼리 (Hub FL API 호출)
  async queryInsights(
    category:    string,
    subcategory: string
  ): Promise<CategoryInsights>
}

interface TrainingResult {
  skipped:     boolean;
  reason?:     string;          // 스킵 사유 (데이터 부족 등)
  sampleSize?: number;
}
```

---

## 3. 로컬 훈련 흐름

```
runLocalTraining(category)
  │
  ▼
1. 로컬 데이터 수집
   → 해당 카테고리 PARA 항목 읽기
   → 최소 3개 미만 → skip (원본 데이터 유출 위험)
  │
  ▼
2. 패턴 추출 (로컬, 원본 텍스트 사용)
   → 체크리스트 패턴, 타임라인, 예산 범위, 공통 실수
   → 원본 텍스트는 이 단계에서만 사용, 이후 메모리 해제
  │
  ▼
3. 그래디언트 계산
   → 글로벌 모델 기준 delta 계산
   → Gaussian 노이즈 추가 (역추적 방지)
  │
  ▼
4. 그래디언트 암호화 (Hub 공개키 RSA-4096)
  │
  ▼
5. Hub POST /api/v1/fl/gradients
   → { model_version, encrypted_gradients, sample_size }
   → 원본 데이터 절대 포함 안 함
```

---

## 4. 로컬 패턴 모델 구조

```typescript
interface LocalPatternModel {
  version:  string;
  patterns: Array<{
    category:          string;
    success_factors:   string[];
    common_mistakes:   string[];
    timeline_patterns: Array<{ event: string; timing: string }>;
    resource_patterns: Array<{ type: string; range: [number, number] }>;
  }>;
}
```

로컬 저장 경로: `~/.openclaw/workspace/.fl-model.json`

---

## 5. 글로벌 모델 동기화

```typescript
async syncGlobalModel(): Promise<void> {
  const latest = await hubClient.get('/api/v1/fl/model/latest');
  if (latest.version === this.localModel.version) return; // 이미 최신

  this.localModel = latest;
  await fs.writeFile(FL_MODEL_PATH, JSON.stringify(latest));
}
```

동기화 시점: 세션 시작 시 백그라운드, 훈련 제출 완료 직후.

---

## 6. 집계 통찰 쿼리

```typescript
async queryInsights(
  category:    string,
  subcategory: string
): Promise<CategoryInsights> {
  // Hub FL 집계 통찰 조회
  // n < 10 시 Hub에서 거부 → "데이터 부족" 반환
  return await hubClient.get(
    `/api/v1/fl/insights/${category}/${subcategory}`
  );
}
```

---

## 7. 프라이버시 보장

| 보장 항목 | 구현 방법 |
|-----------|-----------|
| 원본 데이터 유출 방지 | 그래디언트만 전송, 텍스트 포함 금지 |
| 소규모 보호 | 로컬 항목 < 3개 시 훈련 스킵 |
| 역추적 방지 | Gaussian 노이즈 추가 |
| 암호화 | Hub RSA-4096 공개키로 그래디언트 암호화 |

---

## 8. 실행 조건

- 사용자가 FL 참여에 동의한 경우에만 동작 (옵트인)
- 배터리 충전 중 + Wi-Fi 연결 시에만 훈련 실행 (선택 설정)
- Phase 3에서 구현 예정

---

## 9. 테스트 계획

| 테스트 | 방법 |
|--------|------|
| 원본 텍스트 미포함 검증 | 단위 (페이로드 검사) |
| 항목 3개 미만 시 스킵 | 단위 |
| 그래디언트 암호화/복호화 왕복 | 단위 |
| 글로벌 모델 동기화 | 통합 |
