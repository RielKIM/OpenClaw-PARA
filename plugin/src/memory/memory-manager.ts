// LLD 참조: docs/arch/LLD/plugin/memory-manager.md
import fs   from 'node:fs/promises';
import path from 'node:path';
import os   from 'node:os';
import type { PARACategory, ItemMetadata } from '../types.js';

export class MemoryManager {
  readonly basePath: string;

  constructor(customPath?: string) {
    this.basePath = customPath
      ?? path.join(os.homedir(), '.openclaw', 'workspace', 'memory');
  }

  /** FR-1.1: PARA 폴더 구조 초기화 */
  async initialize(): Promise<void> {
    const categories: PARACategory[] = ['projects', 'areas', 'resources', 'archive'];
    for (const cat of categories) {
      await fs.mkdir(path.join(this.basePath, cat), { recursive: true });
    }
    // TODO: SQLite-vec 인덱스 초기화
  }

  /** FR-1.2: 프로젝트 생성 (index.md + 첫 번째 일일 로그) */
  async createProject(options: {
    title:    string;
    keywords: string[];
    deadline?: Date;
  }): Promise<ItemMetadata> {
    // TODO: 구현
    throw new Error('Not implemented');
  }

  async createArea(options: { title: string; keywords: string[] }): Promise<ItemMetadata> {
    // TODO: 구현
    throw new Error('Not implemented');
  }

  async createResource(options: { title: string; keywords: string[] }): Promise<ItemMetadata> {
    // TODO: 구현
    throw new Error('Not implemented');
  }

  /** 아카이브로 이동 */
  async archive(id: string, category: PARACategory): Promise<void> {
    // TODO: 구현
    throw new Error('Not implemented');
  }

  /** 아카이브에서 복원 */
  async restore(id: string): Promise<void> {
    // TODO: 구현
    throw new Error('Not implemented');
  }

  async readMetadata(id: string): Promise<ItemMetadata> {
    // TODO: 구현
    throw new Error('Not implemented');
  }

  async readAllFiles(id: string): Promise<Array<{ path: string; content: string }>> {
    // TODO: 구현
    throw new Error('Not implemented');
  }

  async listByCategory(category: PARACategory): Promise<ItemMetadata[]> {
    // TODO: 구현
    throw new Error('Not implemented');
  }

  async updateIndex(itemPath: string): Promise<void> {
    // TODO: SQLite-vec 인덱스 업데이트
    throw new Error('Not implemented');
  }
}
