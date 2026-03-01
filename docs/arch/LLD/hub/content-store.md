# Content Store — 상세 설계

**컴포넌트**: PARA Hub
**관련 요구사항**: FR-3.2
**날짜**: 2026-03-01
**상태**: Draft (사용자 합의 전)

---

## 1. 책임

익명화된 프로젝트 콘텐츠를 **Agent 전용 암호화 포맷(지식 그래프 JSON)**으로 변환, 저장, 제공한다. 인간 사용자는 암호화된 원문에 접근할 수 없으며, Agent는 메모리 내에서만 복호화 콘텐츠를 사용하고 즉시 폐기한다.

---

## 2. 지식 그래프 JSON 포맷

```json
{
  "schema_version": "1.0",
  "content_id":     "uuid-v4",
  "metadata": {
    "intent_type":    "travel",
    "domain":         "leisure/tourism",
    "complexity":     "moderate",
    "duration_days":  7,
    "resource_level": "medium"
  },
  "nodes": [
    {
      "id":       "n1",
      "type":     "checklist_item",
      "content":  "렌터카 사전 예약 (성수기 매진 빠름)",
      "priority": "high",
      "timing":   "departure_minus_60_days"
    },
    {
      "id":       "n2",
      "type":     "budget_item",
      "category": "accommodation",
      "amount_range": { "min": 8000, "max": 15000 },
      "currency": "JPY",
      "unit":     "per_night"
    }
  ],
  "edges": [
    { "from": "n1", "to": "n3", "relation": "prerequisite" }
  ],
  "patterns": [
    {
      "type":             "success_pattern",
      "description":      "수영장 있는 가족 친화 숙소 선택",
      "effectiveness_rate": 0.73,
      "sample_size":      23
    }
  ],
  "warnings": [
    {
      "type":        "common_mistake",
      "description": "레스토랑 사전 예약 없이 방문",
      "frequency":   0.45
    }
  ]
}
```

---

## 3. 암호화 구현

```python
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os, json

class ContentEncryptor:
    def __init__(self, hub_public_key_pem: bytes):
        self.pub_key = serialization.load_pem_public_key(hub_public_key_pem)

    def encrypt(self, knowledge_graph: dict) -> EncryptedContent:
        plaintext = json.dumps(knowledge_graph).encode('utf-8')

        # AES-256-GCM으로 콘텐츠 암호화
        aes_key  = os.urandom(32)
        nonce    = os.urandom(12)
        ciphertext = AESGCM(aes_key).encrypt(nonce, plaintext, None)

        # AES 키를 Hub RSA-4096 공개키로 래핑
        encrypted_key = self.pub_key.encrypt(
            aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        return EncryptedContent(
            ciphertext=ciphertext,
            encrypted_key=encrypted_key,
            nonce=nonce
        )
```

---

## 4. Agent 전용 접근 프로토콜

```
Agent 콘텐츠 요청
  │
  ▼
1. Hub: 사용자 평판 등급 확인 (Access Control Service)
  │
  ▼
2. Hub: 콘텐츠 최소 평판 요건 충족 여부 확인
  │
  ▼
3. Hub: Hub 개인키로 AES 키 복호화 → 콘텐츠 복호화
  │
  ▼
4. Hub → Agent: 복호화된 JSON을 메모리 내로만 전달
   (HTTPS 응답, 로컬 파일 저장 금지)
  │
  ▼
5. Agent: 추론에 사용 후 즉시 메모리에서 폐기
  │
  ▼
6. Hub: 접근 로그 기록 (agentId, contentId, timestamp)
```

---

## 5. 저장소 구조

```
S3 Bucket: para-hub-content/
└── {content_id}/
    ├── encrypted_content.bin    ← AES-256-GCM 암호화 콘텐츠
    ├── encrypted_key.bin        ← RSA-4096 래핑된 AES 키
    └── nonce.bin                ← 12바이트 nonce
```

PostgreSQL `shared_content` 테이블에는 메타데이터만 저장 (암호문 없음).

---

## 6. 보존 정책

| 조건 | 동작 |
|------|------|
| 90일 미활동 | 자동 삭제 (S3 + DB) |
| 사용자 회수 요청 | 7일 이내 하드 삭제 |
| 집계 콘텐츠 사용 시 | `last_accessed` 갱신 |

---

## 7. 테스트 계획

| 테스트 | 방법 |
|--------|------|
| 암호화/복호화 왕복 | 단위 |
| Agent만 복호화 가능 (Hub 개인키 없이 불가) | 단위 |
| 로컬 저장 안 됨 (응답 헤더 no-cache 등) | 통합 |
| 90일 만료 삭제 | 배치 테스트 |
| 접근 로그 기록 | 통합 |
