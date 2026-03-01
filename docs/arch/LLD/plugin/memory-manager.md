# Memory Manager — 상세 설계

**컴포넌트**: OpenClaw PARA Memory Plugin
**관련 요구사항**: FR-1.1, FR-1.2
**날짜**: 2026-03-01
**상태**: Draft (사용자 합의 전)

---

## 1. 책임

- PARA 폴더 구조(`projects/`, `areas/`, `resources/`, `archive/`) 초기화 및 유지보수
- 프로젝트/영역/리소스 생성 시 `index.md` + 일일 로그 자동 생성
- PageIndex 서버 인덱싱 위임 (`PageIndexSearchEngine` HTTP 클라이언트 경유)
- 파일 시스템 CRUD 추상화 (다른 컴포넌트의 스토리지 인터페이스 제공)

---

## 2. 인터페이스

```typescript
class MemoryManager {
  private basePath: string;              // ~/.openclaw/workspace/memory
  private searchEngine: PageIndexSearchEngine; // HTTP 클라이언트 (localhost:37779)

  // PARA 폴더 구조 초기화
  async initialize(): Promise<void>

  // 항목 생성
  async createProject(options: CreateProjectOptions): Promise<Project>
  async createArea(options: CreateAreaOptions): Promise<Area>
  async createResource(options: CreateResourceOptions): Promise<Resource>

  // 이동
  async archive(id: string, category: PARACategory): Promise<void>
  async restore(id: string): Promise<void>

  // 조회
  async readMetadata(id: string): Promise<ItemMetadata>
  async readAllFiles(id: string): Promise<FileContent[]>
  async listByCategory(category: PARACategory): Promise<ItemMetadata[]>

  // 인덱스
  async updateIndex(itemPath: string): Promise<void>
  async rebuildIndex(id?: string): Promise<void>
}

type PARACategory = 'projects' | 'areas' | 'resources' | 'archive';

interface CreateProjectOptions {
  title: string;
  keywords: string[];
  deadline?: Date;
  hubContentIds?: string[];
}
```

---

## 3. PARA 폴더 초기화 (FR-1.1)

```typescript
async initialize(): Promise<void> {
  const categories: PARACategory[] = ['projects', 'areas', 'resources', 'archive'];
  for (const cat of categories) {
    await fs.mkdir(path.join(this.basePath, cat), { recursive: true });
  }
  // PageIndex 서버 상태 확인은 MemoryManager 책임이 아님.
  // 세션 시작 시 Plugin.onLoad() 에서 PageIndexSearchEngine.checkHealth() 로 처리.
}
```

기존 `memory/` 폴더가 있을 경우 하위 호환 유지 — 기존 파일 건드리지 않고 PARA 폴더만 추가 생성.

---

## 4. 프로젝트 생성 (FR-1.2)

```typescript
async createProject(options: CreateProjectOptions): Promise<Project> {
  const id = generateUUID();
  const dir = path.join(this.basePath, 'projects', id);
  await fs.mkdir(dir, { recursive: true });

  const today = toISODate(new Date());
  const meta = {
    id,
    title: options.title,
    category: 'project',
    status: 'active',
    created_at: today,
    deadline: toISODate(options.deadline) ?? null,
    last_accessed: today,
    keywords: options.keywords,
    hub_content_ids: options.hubContentIds ?? [],
  };

  // index.md (YAML frontmatter + 빈 본문)
  await writeMarkdownWithFrontmatter(path.join(dir, 'index.md'), meta, '');

  // 첫 번째 일일 로그
  await fs.writeFile(path.join(dir, `${today}.md`), `# ${today}\n\n`);

  await this.updateIndex(dir);
  return { ...meta };
}
```

**Area / Resource** 생성도 동일 패턴 — `deadline` 없음, `category` 값만 다름.

---

## 5. 아카이브 / 복원

```typescript
async archive(id: string, category: PARACategory): Promise<void> {
  const src  = path.join(this.basePath, category, id);
  const dest = path.join(this.basePath, 'archive', category, id);
  await fs.mkdir(path.dirname(dest), { recursive: true });
  await fs.rename(src, dest);

  // index.md status 업데이트
  await updateFrontmatterField(path.join(dest, 'index.md'), 'status', 'archived');
  await this.searchEngine.deleteIndex(src);  // 이전 경로 인덱스 제거 (searchAll은 archive 제외이나 명시적 삭제)
}

async restore(id: string): Promise<void> {
  // archive/projects/{id} → projects/{id}
  const archivePath = await this.findInArchive(id);
  const meta = await readFrontmatter(path.join(archivePath, 'index.md'));
  const dest = path.join(this.basePath, meta.original_category, id);
  await fs.rename(archivePath, dest);
  await updateFrontmatterField(path.join(dest, 'index.md'), 'status', 'active');
  await this.searchEngine.reindexItem(dest); // 복원 후 재인덱싱
}
```

---

## 6. PageIndex 서버 인덱싱

### 책임 분리

| 역할 | 담당 |
|------|------|
| 항목(UUID) 레벨 조회 | MemoryManager (`listByCategory`, `readMetadata`) — 파일시스템 기반 |
| 섹션 레벨 검색 인덱스 | PageIndex 서버 (`PageIndexSearchEngine` HTTP 클라이언트) |

로컬 DB(SQLite/LanceDB)를 사용하지 않는다. 항목 목록은 파일시스템 디렉토리 순회로 충분하다.

### 인덱스 갱신 로직

```typescript
async updateIndex(itemPath: string): Promise<void> {
  const meta = await readFrontmatter(path.join(itemPath, 'index.md'));
  // PageIndex 서버에 HTTP 요청 — 서버 미실행 시 PageIndexSearchEngine이 조용히 무시
  await this.searchEngine.indexFile(itemPath, meta.id, meta.category as PARACategory);
}

async rebuildIndex(id?: string): Promise<void> {
  if (id) {
    const meta = await this.readMetadata(id);
    const itemPath = path.join(this.basePath, meta.category, id);
    await this.searchEngine.reindexItem(itemPath);
  } else {
    // archive 제외 — searchAll()이 이미 archive 카테고리를 필터링하므로 인덱스 불필요
    for (const cat of ['projects', 'areas', 'resources'] as PARACategory[]) {
      const items = await this.listByCategory(cat);
      for (const item of items) {
        await this.searchEngine.reindexItem(path.join(this.basePath, cat, item.id));
      }
    }
  }
}
```

---

## 7. 슬래시 명령

| 명령 | 동작 |
|------|------|
| `/new-project {title}` | 프로젝트 생성 |
| `/new-area {title}` | 영역 생성 |
| `/archive {id}` | 수동 아카이브 |
| `/restore {id}` | 복원 |
| `/rebuild-index` | 전체 인덱스 재구축 |

---

## 8. 테스트 계획

| 테스트 | 방법 |
|--------|------|
| 폴더 초기화 | 단위 (tmpdir) |
| index.md YAML 파싱 | 단위 |
| 아카이브 / 복원 경로 | 단위 |
| PageIndex 서버 인덱싱 (indexFile, reindexItem) | 통합 (서버 실행 필요) |
| 서버 미실행 시 graceful degradation | 단위 (healthy=false mock) |
| 기존 memory/ 하위 호환 | 통합 |
