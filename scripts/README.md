# Scripts 사용 가이드 (용도별 분류)

스크립트는 **용도별 하위 폴더**로 구분되어 있습니다. 실행 시 프로젝트 루트에서 `python scripts/<폴더>/<파일>` 또는 `./scripts/<폴더>/<파일>.sh` 형태로 호출합니다.

---

## 폴더 구조

| 폴더 | 용도 | 주요 스크립트 |
|------|------|----------------|
| **backend/** | API·서버, 임베딩·검색·키워드 등 핵심 백엔드 로직 | start_server.py, embed_and_store.py, search_and_query.py, extract_keywords_and_labels.py, generate_chunk_titles.py, check_gpt4all_model.py, check_model_download.py |
| **db/** | DB 초기화, 마이그레이션, 스키마, 분석 | init_db.py, migrate_phase7_upgrade.py, migrate_postgres_volume.sh, insert_test_tasks_to_db.py, insert_test_tasks.sql, analyze_slow_queries.py, add_phase7_columns.py, fix_label_unique_constraint.py |
| **n8n/** | n8n 워크플로우·Phase 8-2 연동 (현재 상태·Gap·Plan·Task 실행) | run_task_execution.py, run-claude-analysis.sh, run-gap-analysis.sh, generate-plan.sh, run-phase-8-2-all.sh, save_current_state_to_db.py, save_gap_analysis_to_db.py, save_plan_to_db.py |
| **web/** | 웹/프론트 전용 (예정) | — |
| **devtool/** | 개발 도구 (백업, 보안, 동기화, 감시, 로그, 테스트 등) | backup_system.py, security_scan.py, benchmark_search.py, check_data_sync.py, sync_data.py, watcher.py, auto_commit.py, work_logger.py, collector.py, system_agent.py, update_work_log_from_md.py, phase_complete.py, test_phase7.py |

---

## 실행 예시 (프로젝트 루트 기준)

```bash
# 백엔드
python scripts/backend/embed_and_store.py
python scripts/backend/search_and_query.py "검색어"
python scripts/backend/start_server.py

# DB
python scripts/db/init_db.py
docker exec -i pab-postgres psql -U brain -d knowledge < scripts/db/insert_test_tasks.sql

# n8n / Phase 8-2
./scripts/n8n/run-phase-8-2-all.sh
python scripts/n8n/run_task_execution.py --task-id 1

# 개발 도구
python scripts/devtool/backup_system.py backup
python scripts/devtool/check_data_sync.py
python scripts/devtool/watcher.py
```

---

## embed_and_store.py (backend)

Markdown 파일을 읽어 임베딩을 생성하고 Qdrant에 저장합니다.

```bash
python scripts/backend/embed_and_store.py
python scripts/backend/embed_and_store.py --recreate
```

---

## search_and_query.py (backend)

Qdrant에서 문서를 검색하고 (옵션) GPT4All로 응답을 생성합니다.

```bash
python scripts/backend/search_and_query.py "검색어"
python scripts/backend/search_and_query.py "검색어" --gpt4all
```

---

**문서 버전**: 2.0 (용도별 폴더 분류 반영)
