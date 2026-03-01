# Reputation Service — 상세 설계

**컴포넌트**: PARA Hub
**관련 요구사항**: FR-4.1, FR-4.3, FR-4.4, FR-4.5
**날짜**: 2026-03-01
**상태**: Draft (사용자 합의 전)

---

## 1. 책임

사용자 기여 이벤트를 수신하여 평판 점수를 계산·갱신하고, 등급 전환 및 배지를 관리한다. 6개월 미활동 사용자에게 패널티를 적용한다.

---

## 2. 인터페이스

```python
class ReputationService:
    async def calculate_score(self, user_id: str) -> ReputationScore
    async def process_event(self, event: ReputationEvent) -> ScoreDelta
    def   determine_grade(self, score: int) -> ReputationGrade
    async def check_and_award_badges(self, user_id: str) -> list[Badge]
    async def apply_inactivity_penalty(self) -> None   # 배치 처리

@dataclass
class ReputationScore:
    total:     int
    breakdown: dict[str, int]

@dataclass
class ScoreDelta:
    delta:      int
    new_score:  int
    new_grade:  ReputationGrade
    new_badges: list[Badge]
```

---

## 3. 점수 계산

```python
async def calculate_score(self, user_id: str) -> ReputationScore:
    u = await self.db.get_user_stats(user_id)

    quality     = u.average_rating * u.rated_shares_count
    quantity    = math.log(1 + u.shared_projects_count) * 100
    engagement  = (u.helpful_votes + u.comments_received) * 0.5
    consistency = max(0, min(30, u.current_streak_days)) * 3.33
    helpfulness = (u.resolved_issues + u.accepted_bug_reports) * 5

    total = (quality     * 0.40 +
             quantity    * 0.25 +
             engagement  * 0.20 +
             consistency * 0.10 +
             helpfulness * 0.05)

    return ReputationScore(
        total=min(1000, round(total)),
        breakdown={
            'quality':     round(quality     * 0.40),
            'quantity':    round(quantity    * 0.25),
            'engagement':  round(engagement  * 0.20),
            'consistency': round(consistency * 0.10),
            'helpfulness': round(helpfulness * 0.05),
        }
    )
```

---

## 4. 이벤트 처리

### 이벤트 타입 및 기본 점수

| event_type | 점수 | 중복 제한 |
|------------|------|-----------|
| `project_shared` | +100 | — |
| `area_workflow_shared` | +200 | — |
| `content_used_by_10` | +50 | 콘텐츠당 1회 |
| `rating_4plus_received` | +100 | 콘텐츠당 1회 |
| `bug_report_accepted` | +20 | 일 5회 |
| `suggestion_accepted` | +30 | 일 3회 |
| `streak_weekly` | +50 | 주 1회 |

```python
async def process_event(self, event: ReputationEvent) -> ScoreDelta:
    if await self._is_duplicate(event):
        return ScoreDelta(delta=0, ...)

    delta = REPUTATION_EVENTS[event.event_type]['base']
    await self.db.create_reputation_event(event, delta)
    await self.db.increment_reputation(event.user_id, delta)
    await self.redis.delete(f"reputation:{event.user_id}")

    new_score = await self.calculate_score(event.user_id)
    new_grade = self.determine_grade(new_score.total)

    # 등급 변경 시 알림
    if new_grade != await self.db.get_user_grade(event.user_id):
        await self.db.update_user_grade(event.user_id, new_grade)
        await self._notify_grade_change(event.user_id, new_grade)

    new_badges = await self.check_and_award_badges(event.user_id)
    return ScoreDelta(delta=delta, new_score=new_score.total,
                      new_grade=new_grade, new_badges=new_badges)
```

---

## 5. 등급 정의

| 등급 | 범위 |
|------|------|
| Newbie | 0 ~ 99 |
| Contributor | 100 ~ 299 |
| Trusted | 300 ~ 499 |
| Expert | 500 ~ 699 |
| Master | 700 ~ 1000 |

등급별 접근 권한은 `access-control.md` 참조.

---

## 6. 미활동 패널티 (배치, 매일 자정)

```python
async def apply_inactivity_penalty(self) -> None:
    cutoff = datetime.now() - timedelta(days=180)
    users  = await self.db.get_inactive_users_since(cutoff)

    for u in users:
        grade_min = GRADE_THRESHOLDS[u.reputation_grade][0]
        new_score = max(grade_min, round(u.reputation_score * 0.95))
        await self.db.update_reputation(u.id, new_score)
```

---

## 7. 배지 시스템

```python
BADGE_CONDITIONS = {
    '🌱 Seedling':  lambda u: u.shared_projects_count >= 1,
    '📚 Librarian': lambda u: u.shared_projects_count >= 10,
    '🏆 Expert':    lambda u: u.shared_projects_count >= 50 and u.average_rating >= 4.5,
    '🌟 Star':      lambda u: u.shared_projects_count >= 100 and u.total_uses >= 500,
    '🔥 Streak':    lambda u: u.max_streak_days >= 30,
    '🎯 Helpful':   lambda u: u.total_helpful_votes >= 100,
}

async def check_and_award_badges(self, user_id: str) -> list[Badge]:
    u = await self.db.get_user_stats(user_id)
    current = set(u.badges)
    new_badges = []
    for name, cond in BADGE_CONDITIONS.items():
        if name not in current and cond(u):
            await self.db.award_badge(user_id, name)
            new_badges.append(Badge(name=name, awarded_at=datetime.now()))
    return new_badges
```

---

## 8. WebSocket 알림 페이로드

```json
{
  "event": "reputation_update",
  "data": {
    "delta":              100,
    "new_score":          350,
    "new_grade":          "Trusted",
    "new_badges":         ["🌱 Seedling"],
    "unlocked_features":  ["premium_content"]
  }
}
```

---

## 9. 테스트 계획

| 테스트 | 방법 |
|--------|------|
| 점수 계산 정확도 | 단위 (고정 입력) |
| 중복 이벤트 방지 | 단위 |
| 등급 전환 알림 | 통합 |
| 미활동 패널티 적용 | 배치 테스트 (날짜 목킹) |
| 배지 수여 조건 | 단위 |
