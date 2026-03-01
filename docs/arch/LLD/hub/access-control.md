# Access Control Service — 상세 설계

**컴포넌트**: PARA Hub
**관련 요구사항**: FR-4.2
**날짜**: 2026-03-01
**상태**: Draft (사용자 합의 전)

---

## 1. 책임

사용자 평판 등급에 따라 콘텐츠 접근 권한을 결정하고, 모든 접근 시도를 감사 로그에 기록한다.

---

## 2. 인터페이스

```python
@dataclass
class AccessDecision:
    allowed:        bool
    grade:          ReputationGrade | None = None
    score:          int | None = None
    reason:         str | None = None
    required_grade: ReputationGrade | None = None
    upgrade_hint:   str | None = None

class AccessControlService:
    async def check_access(
        self,
        user_id:     str,
        content:     SharedContent,
        access_type: str            # 'view' | 'download' | 'federated'
    ) -> AccessDecision
```

---

## 3. 등급별 권한 정의

```python
GRADE_PERMISSIONS: dict[ReputationGrade, list[str]] = {
    ReputationGrade.NEWBIE: [
        'public_summaries',
        'basic_search',
    ],
    ReputationGrade.CONTRIBUTOR: [
        'basic_shared_content',
        'community_insights',
        'federated_learning',
    ],
    ReputationGrade.TRUSTED: [
        'premium_content',
        'custom_template_requests',
        'early_feature_access',
        'higher_matching_priority',
    ],
    ReputationGrade.EXPERT: [
        'all_hub_content_free',
        'priority_support',
        'community_spotlight',
        'beta_features',
    ],
    ReputationGrade.MASTER: [
        'moderation_rights',
        'expert_profile_page',
        'roadmap_influence',
        'certified_badge',
    ],
}

# 각 등급은 하위 등급 권한을 모두 포함 (누적)
```

---

## 4. 접근 결정 로직

```python
async def check_access(
    self,
    user_id:     str,
    content:     SharedContent,
    access_type: str
) -> AccessDecision:
    score = await self.reputation_service.calculate_score(user_id)
    grade = self.reputation_service.determine_grade(score.total)
    all_perms = self._get_cumulative_permissions(grade)

    # 1. 콘텐츠 최소 평판 요건 확인
    if score.total < content.min_reputation:
        required_grade = self._grade_for_score(content.min_reputation)
        return AccessDecision(
            allowed=False,
            reason=f"평판 {content.min_reputation}점 필요 (현재 {score.total}점)",
            required_grade=required_grade,
            upgrade_hint=self._get_upgrade_hint(score.total, content.min_reputation),
        )

    # 2. 프리미엄 콘텐츠 등급 확인
    if content.access_level == 'premium' and 'premium_content' not in all_perms:
        return AccessDecision(
            allowed=False,
            reason="Trusted 등급(300점) 이상 필요",
            required_grade=ReputationGrade.TRUSTED,
        )

    # 3. 접근 허용 + 감사 로그
    await self._log_access(user_id, content.id, access_type)

    return AccessDecision(allowed=True, grade=grade, score=score.total)
```

---

## 5. 누적 권한 계산

```python
GRADE_ORDER = [
    ReputationGrade.NEWBIE,
    ReputationGrade.CONTRIBUTOR,
    ReputationGrade.TRUSTED,
    ReputationGrade.EXPERT,
    ReputationGrade.MASTER,
]

def _get_cumulative_permissions(
    self,
    grade: ReputationGrade
) -> set[str]:
    perms = set()
    for g in GRADE_ORDER:
        perms |= set(GRADE_PERMISSIONS[g])
        if g == grade:
            break
    return perms
```

---

## 6. 감사 로그

```python
async def _log_access(
    self,
    user_id:     str,
    content_id:  str,
    access_type: str
) -> None:
    await self.db.insert_access_log({
        'user_id':     user_id,
        'content_id':  content_id,
        'access_type': access_type,
        'accessed_at': datetime.now(UTC),
    })
```

로그 보존: 90일 후 롤링 삭제.

---

## 7. 업그레이드 힌트 메시지

```python
def _get_upgrade_hint(self, current: int, required: int) -> str:
    gap = required - current
    return (
        f"{gap}점 더 필요합니다. "
        f"프로젝트 공유(+100점) 또는 "
        f"영역 워크플로우 공유(+200점)로 평판을 올려보세요."
    )
```

---

## 8. 테스트 계획

| 테스트 | 방법 |
|--------|------|
| 등급별 접근 허용/거부 | 단위 (5개 등급 × 콘텐츠 레벨) |
| 누적 권한 계산 | 단위 |
| 감사 로그 기록 | 통합 |
| 업그레이드 힌트 메시지 | 단위 |
