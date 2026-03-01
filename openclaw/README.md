# openclaw/ — OpenClaw 소스 참조 디렉토리

이 디렉토리에 OpenClaw 원본 소스를 클론합니다.
플러그인 개발 시 타입 참조와 SDK API 확인에 사용합니다.

## 클론 방법

```bash
# 이 디렉토리 안에서 실행
git clone https://github.com/openclaw/openclaw .
```

또는 상위 디렉토리에서:

```bash
git clone https://github.com/openclaw/openclaw openclaw/openclaw
```

## tsconfig 경로 별칭

`plugin/tsconfig.json`의 `paths` 설정으로 SDK 타입을 직접 참조합니다:

```json
{
  "compilerOptions": {
    "paths": {
      "@openclaw/plugin-sdk": ["../openclaw/openclaw/src/plugin-sdk/index.ts"]
    }
  }
}
```

## 주요 참조 경로

| 항목 | 경로 |
|------|------|
| Plugin SDK 타입 | `openclaw/src/plugin-sdk/index.ts` |
| `OpenClawPluginDefinition` | `openclaw/src/plugins/types.ts` |
| 플러그인 API (`registerTool` 등) | `openclaw/src/plugins/types.ts:240-284` |
| 플러그인 예시 | `openclaw/extensions/memory-lancedb/` |

## 주의사항

- `openclaw/openclaw/` 디렉토리 내부 파일은 **직접 수정 금지**
- SDK API 변경 시 `plugin/src/index.ts` 호환성 확인 필요
- 이 디렉토리는 `.gitignore`에 추가 권장 (별도 저장소)
