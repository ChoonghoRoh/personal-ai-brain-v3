# Route-Menu Mapping (Phase 13-2-1)

**작성일**: 2026-02-16
**검증 결과**: 17개 메뉴 path 모두 HTTP 200 OK

---

## 메뉴 Path ↔ Backend Route 1:1 대응표

### USER_MENU (6개)

| # | Menu Path | Label | Route Handler | Template | HTTP |
|---|-----------|-------|---------------|----------|------|
| 1 | `/dashboard` | 대시보드 | `dashboard_page` | dashboard.html | 200 |
| 2 | `/search` | 검색 | `search_page` | search.html | 200 |
| 3 | `/knowledge` | 지식 구조 | `knowledge_page` | knowledge/knowledge.html | 200 |
| 4 | `/reason` | Reasoning | `reason_page` | reason.html | 200 |
| 5 | `/ask` | AI 질의 | `ask_page` | ask.html | 200 |
| 6 | `/logs` | 로그 | `logs_page` | logs.html | 200 |

### ADMIN_MENU (6개)

| # | Menu Path | Label | Route Handler | Template | HTTP |
|---|-----------|-------|---------------|----------|------|
| 7 | `/admin/groups` | 키워드 관리 | `admin_groups_page` | admin/groups.html | 200 |
| 8 | `/admin/labels` | 라벨 관리 | `admin_labels_page` | admin/labels.html | 200 |
| 9 | `/admin/chunk-create` | 청크 생성 | `admin_chunk_create_page` | admin/chunk-create.html | 200 |
| 10 | `/admin/approval` | 청크 승인 | `admin_approval_page` | admin/approval.html | 200 |
| 11 | `/admin/chunk-labels` | 청크 관리 | `admin_chunk_labels_page` | admin/chunk-labels.html | 200 |
| 12 | `/admin/statistics` | 통계 | `admin_statistics_page` | admin/statistics.html | 200 |

### SETTINGS_MENU (5개)

| # | Menu Path | Label | Route Handler | Template | HTTP |
|---|-----------|-------|---------------|----------|------|
| 13 | `/admin/settings/templates` | 템플릿 | `admin_settings_templates_page` | admin/settings/templates.html | 200 |
| 14 | `/admin/settings/presets` | 프리셋 | `admin_settings_presets_page` | admin/settings/presets.html | 200 |
| 15 | `/admin/settings/rag-profiles` | RAG 프로필 | `admin_settings_rag_profiles_page` | admin/settings/rag-profiles.html | 200 |
| 16 | `/admin/settings/policy-sets` | 정책 | `admin_settings_policy_sets_page` | admin/settings/policy-sets.html | 200 |
| 17 | `/admin/settings/audit-logs` | 변경 이력 | `admin_settings_audit_logs_page` | admin/settings/audit-logs.html | 200 |

---

## 메뉴 외 추가 라우트

| Path | Handler | Template | 비고 |
|------|---------|----------|------|
| `/` | `root_page` | dashboard.html | 메인 진입점 (대시보드 리다이렉트) |
| `/document/{id}` | `document_page` | document.html | 문서 상세 (동적 라우트) |
| `/knowledge-detail` | `knowledge_detail_page` | knowledge/knowledge-detail.html | 청크 상세 |
| `/knowledge-label-matching` | `knowledge_label_matching_page` | knowledge/knowledge-label-matching.html | 라벨 매칭 |
| `/knowledge-relation-matching` | `knowledge_relation_matching_page` | knowledge/knowledge-relation-matching.html | 관계 매칭 |
| `/knowledge-admin` | `knowledge_admin_page` | knowledge/knowledge-admin.html | Legacy (구 지식 관리) |

---

## 검증 방법

```bash
# 17개 메뉴 path HTTP 200 확인
for path in /dashboard /search /knowledge /reason /ask /logs \
  /admin/groups /admin/labels /admin/chunk-create /admin/approval \
  /admin/chunk-labels /admin/statistics \
  /admin/settings/templates /admin/settings/presets \
  /admin/settings/rag-profiles /admin/settings/policy-sets \
  /admin/settings/audit-logs; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8001${path}")
  printf "%s %s\n" "$code" "$path"
done
```
