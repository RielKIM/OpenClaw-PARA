# FL Aggregator — 상세 설계

**컴포넌트**: PARA Hub
**관련 요구사항**: FR-5 (Hub 측)
**날짜**: 2026-03-01
**상태**: Draft (사용자 합의 전)

---

## 1. 책임

각 사용자 디바이스에서 전송된 암호화된 그래디언트를 SMPC(Secure Multi-Party Computation)로 집계하여 글로벌 패턴 모델을 업데이트하고, n ≥ 10 소스에서만 집계 통찰을 제공한다.

---

## 2. 인터페이스

```python
class FederatedLearningAggregator:
    MIN_PARTICIPANTS = 10

    async def receive_gradient(
        self,
        user_id:              str,
        model_version:        str,
        encrypted_gradients:  bytes,
        sample_size:          int
    ) -> None

    async def aggregate_round(
        self,
        model_version: str
    ) -> AggregationResult

    async def get_insights(
        self,
        category:    str,
        subcategory: str
    ) -> CategoryInsights
```

---

## 3. 집계 파이프라인

```
그래디언트 수신 (POST /api/v1/fl/gradients)
  │
  ▼ 암호화된 상태로 임시 저장 (Redis, TTL 24h)
  │
  ▼ [배치 트리거: 참여자 ≥ 10명 또는 6시간마다]
  │
aggregate_round(model_version)
  │
  ├── 참여자 < 10 → 스킵 (개인정보 보호)
  │
  └── 참여자 ≥ 10
        │
        ▼
      SMPC 집계 (복호화 없이 암호화 상태 합산)
        │
        ▼
      글로벌 모델 업데이트 (Model Store)
        │
        ▼
      처리된 그래디언트 즉시 삭제
        │
        ▼
      새 모델 버전 배포 (GET /api/v1/fl/model/latest)
```

---

## 4. SMPC 집계 구현

```python
async def _secure_aggregate(
    self,
    encrypted_gradients: list[EncryptedGradient]
) -> AggregatedGradient:
    """
    암호화된 상태에서 그래디언트 합산.
    각 참여자의 개별 그래디언트를 복호화하지 않음.

    Phase 3-A: FedAvg (단순화)
    Phase 3-B: SMPC (Secret Sharing 기반)
    Phase 3-C: 동형암호 (Homomorphic Encryption)
    """
    # Phase 3-A 구현 (MVP)
    # 각 그래디언트를 Hub 개인키로 복호화 후 평균
    # → Phase 3-B에서 복호화 없는 집계로 교체 예정
    decrypted = [self._decrypt(g) for g in encrypted_gradients]
    averaged  = np.mean(decrypted, axis=0)
    return AggregatedGradient(values=averaged)
```

> **Phase 3-A 주의**: 현재 MVP는 Hub에서 복호화 후 집계. Phase 3-B에서 PySyft 기반 SMPC로 교체 예정.

---

## 5. 집계 통찰 제공

```python
async def get_insights(
    self,
    category:    str,
    subcategory: str
) -> CategoryInsights:
    model   = await self.model_store.get_latest()
    pattern = model.get_pattern(category, subcategory)

    # n < 10: 통찰 제공 거부
    if pattern.sample_size < self.MIN_PARTICIPANTS:
        return CategoryInsights(
            available=False,
            reason=f"데이터 부족 ({pattern.sample_size}/{self.MIN_PARTICIPANTS})"
        )

    return CategoryInsights(
        available=True,
        patterns=[
            {
                'description':        p.description,
                'effectiveness_rate': p.rate,
                'sample_size':        pattern.sample_size,
            }
            for p in pattern.top_patterns
        ],
        warnings=    pattern.common_mistakes,
        disclaimer=  f"{pattern.sample_size}개의 익명화된 경험 기반. 전문 조언 아님.",
    )
```

---

## 6. 프라이버시 보장

| 항목 | 방법 |
|------|------|
| 원본 데이터 유출 방지 | 그래디언트만 수신, 텍스트 수신 금지 |
| 소규모 그룹 식별 방지 | n < 10 통찰 제공 거부 |
| 그래디언트 보존 최소화 | 집계 완료 즉시 삭제 |
| 개별 기여 비식별화 | SMPC 집계 (Phase 3-B부터) |

---

## 7. API 엔드포인트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | `/api/v1/fl/gradients` | 암호화된 그래디언트 제출 |
| GET | `/api/v1/fl/model/latest` | 최신 글로벌 모델 조회 |
| GET | `/api/v1/fl/insights/{category}/{subcategory}` | 집계 통찰 조회 |

---

## 8. 구현 단계

| 단계 | 내용 | 예정 |
|------|------|------|
| Phase 3-A | FedAvg (복호화 후 평균) — MVP | Phase 3 초기 |
| Phase 3-B | SMPC (PySyft) — 복호화 없는 집계 | Phase 3 중반 |
| Phase 3-C | 동형암호 전환 | Phase 3 후반 |

---

## 9. 테스트 계획

| 테스트 | 방법 |
|--------|------|
| n < 10 통찰 거부 | 단위 |
| 그래디언트 집계 후 삭제 | 통합 |
| 집계 모델 정확도 | 시뮬레이션 (오차 < 0.1%) |
| 면책 문구 포함 | 단위 |
