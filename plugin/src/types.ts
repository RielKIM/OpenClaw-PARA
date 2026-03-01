// OpenClaw-PARA 플러그인 공유 타입 정의

export type PARACategory = 'projects' | 'areas' | 'resources' | 'archive';

export type IntentType = 'project' | 'area' | 'resource' | 'unknown';

export interface ItemMetadata {
  id:            string;
  title:         string;
  category:      PARACategory;
  status:        'active' | 'archived';
  created_at:    string;   // YYYY-MM-DD
  last_accessed: string;   // YYYY-MM-DD
  deadline?:     string;   // YYYY-MM-DD
  keywords:      string[];
  hub_content_ids: string[];
}

export interface ClassificationResult {
  intent:      IntentType;
  confidence:  number;     // 0.0 ~ 1.0
  entities: {
    type?:     string;     // travel | parenting | tech | ...
    target?:   string;
    keywords:  string[];
  };
  fallbackUsed: boolean;
}

export interface SearchResult {
  projectId:      string;
  projectTitle:   string;
  filePath:       string;
  nodeId:         string;   // 트리 노드 ID ("1.2.3")
  section:        string;
  content:        string;
  relevanceScore: number;
  reasoning:      string;   // LLM 선택 근거
}

export interface TransitionRecommendation {
  id:        string;
  title:     string;
  type:      'archive' | 'archive_or_extend' | 'reactivate';
  reason:    string;
  daysSince?: number;
}

export interface PluginConfig {
  memoryPath?:          string;
  hubEnabled?:          boolean;
  hubApiUrl?:           string;
  openaiApiKey?:        string;
  flEnabled?:           boolean;
  pageIndexServerUrl?:  string;   // 기본값: "http://localhost:37779"
  pageIndexEnabled?:    boolean;  // 기본값: true (서버 실행 중이면 자동 활성화)
}
