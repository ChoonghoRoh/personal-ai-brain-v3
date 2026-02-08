"""FastAPI 메인 애플리케이션"""
import logging
import os
import sys
import subprocess
import threading
import time
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request

from fastapi.middleware.cors import CORSMiddleware

from backend.routers.search import search, documents
from backend.routers.system import system, backup, integrity, logs, error_logs, statistics
from backend.routers.system.backup import legacy_router as backup_legacy_router
from backend.routers.ai import ai, conversations
from backend.routers.knowledge import knowledge, labels, relations, approval, suggestions, knowledge_integration
from backend.routers.reasoning import reason, reasoning_chain, reasoning_results, recommendations, reason_stream, reason_store
from backend.routers.cognitive import memory, context, learning, personality, metacognition
from backend.routers.automation import automation, workflow
from backend.routers.ingest import file_parser
from backend.routers.auth import auth
from backend.routers import admin  # Phase 11-2: Admin 설정 관리 API
from backend.config import (
    PROJECT_ROOT,
    OLLAMA_BASE_URL,
    CORS_ORIGINS,
    CORS_ALLOW_CREDENTIALS,
    CORS_ALLOW_METHODS,
    CORS_ALLOW_HEADERS,
    ENVIRONMENT,
    AUTH_ENABLED,
)
from backend.middleware.security import SecurityHeadersMiddleware
from backend.middleware.rate_limit import setup_rate_limiting
from backend.models.database import init_db

app = FastAPI(
    title="Personal AI Brain API",
    description="""
    개인 AI 브레인 시스템 API
    
    ## 주요 기능
    
    * **검색**: 문서 검색 및 고급 검색
    * **지식 관리**: 청크, 라벨, 관계 관리
    * **AI 질의**: AI 기반 질의응답
    * **Reasoning**: 추론 체인 실행
    * **맥락 이해**: 문서 간 맥락 연결
    * **기억 시스템**: 장기/단기/작업 기억
    * **백업/복원**: 데이터 백업 및 복원
    * **대화 기록**: 대화 기록 저장 및 검색
    
    ## 인증 (Phase 9-1)

    - **JWT Bearer 토큰**: `Authorization: Bearer <token>`
    - **API Key**: `X-API-Key: <api_key>`
    - 개발 환경에서는 인증이 비활성화되어 있습니다 (AUTH_ENABLED=false)
    """,
    version="1.0.0",
    contact={
        "name": "Personal AI Brain",
        "url": "https://github.com/ChoonghoRoh/personal-ai-brain",
    },
    license_info={
        "name": "MIT",
    },
    servers=[
        {
            "url": "http://localhost:8000",
            "description": "로컬 개발 서버"
        },
    ]
)

# ============================================
# CORS 미들웨어 설정 (Phase 9-1-3)
# ============================================
# CORS는 가장 먼저 등록해야 프리플라이트 요청이 올바르게 처리됨
if ENVIRONMENT == "development":
    # 개발 환경: 모든 오리진 허용 (편의를 위해)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,  # * 사용 시 credentials=False 필요
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    # 프로덕션 환경: 지정된 오리진만 허용
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=CORS_ALLOW_CREDENTIALS,
        allow_methods=CORS_ALLOW_METHODS if CORS_ALLOW_METHODS != ["*"] else ["*"],
        allow_headers=CORS_ALLOW_HEADERS if CORS_ALLOW_HEADERS != ["*"] else ["*"],
        expose_headers=["X-Request-ID", "X-RateLimit-Remaining", "X-RateLimit-Limit"],
        max_age=600,
    )

# 보안 헤더 미들웨어 추가
app.add_middleware(SecurityHeadersMiddleware)

# ============================================
# Rate Limiting 설정 (Phase 9-1-4)
# ============================================
setup_rate_limiting(app)

# ============================================
# 라우터 등록
# ============================================

# 인증 라우터 (먼저 등록)
app.include_router(auth.router)

# 기능 라우터
app.include_router(search.router)
app.include_router(system.router)
app.include_router(documents.router)
app.include_router(ai.router)
app.include_router(logs.router)
app.include_router(labels.router)
app.include_router(relations.router)
app.include_router(recommendations.router)
app.include_router(reason.router)
app.include_router(reason_stream.router)  # Phase 10-1: Reasoning 스트리밍 (진행 상태, 취소, ETA)
app.include_router(reason_store.router)  # Phase 10-4-2/3: 결과 공유·의사결정 문서
# approval.router를 knowledge.router보다 먼저 등록 (경로 충돌 방지)
app.include_router(approval.router)
app.include_router(knowledge.router)
app.include_router(suggestions.router)
app.include_router(context.router)
app.include_router(memory.router)
app.include_router(backup.router)
app.include_router(integrity.router)
app.include_router(conversations.router)
app.include_router(error_logs.router)
app.include_router(reasoning_results.router)
app.include_router(automation.router)
app.include_router(learning.router)
app.include_router(personality.router)
app.include_router(metacognition.router)
app.include_router(reasoning_chain.router)
app.include_router(knowledge_integration.router)
app.include_router(file_parser.router)
app.include_router(workflow.router)
app.include_router(statistics.router)  # Phase 9-4-2: 통계 대시보드
app.include_router(backup_legacy_router)  # Phase 9-4-3: 백업 레거시 API 호환
app.include_router(admin.router)  # Phase 11-2: Admin 설정 관리 API

# 정적 파일 및 템플릿
web_dir = PROJECT_ROOT / "web"
templates_dir = web_dir / "src" / "pages"

if templates_dir.exists():
    templates = Jinja2Templates(directory=str(templates_dir))
    if (web_dir / "public").exists():
        app.mount("/static", StaticFiles(directory=str(web_dir / "public")), name="static")
else:
    templates = None


def _llm_check_after_startup() -> None:
    """Backend 기동 완료 후 LLM 서버 확인. localhost면 미실행 시 ollama serve 기동, 이후 모델 작동 확인."""
    time.sleep(3)
    log = logging.getLogger(__name__)
    base = (OLLAMA_BASE_URL or "").strip().lower()
    script_path = PROJECT_ROOT / "scripts" / "llm_server_check.py"
    if "localhost" in base or "127.0.0.1" in base:
        if script_path.exists():
            try:
                env = {**os.environ, "OLLAMA_BASE_URL": OLLAMA_BASE_URL or "http://localhost:11434"}
                r = subprocess.run(
                    [sys.executable, str(script_path), "--start-if-missing", "--check-model"],
                    env=env,
                    cwd=str(PROJECT_ROOT),
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
                if r.returncode == 0:
                    log.info("LLM 서버 확인 완료 (자동 기동·모델 검증): %s", r.stdout or "")
                else:
                    log.warning("LLM 서버 확인 실패 (exit %s): %s", r.returncode, (r.stderr or r.stdout or "").strip())
            except subprocess.TimeoutExpired:
                log.warning("LLM 서버 확인 타임아웃 (120초)")
            except Exception as e:
                log.warning("LLM 서버 확인 예외: %s", e)
        else:
            log.debug("scripts/llm_server_check.py 없음, LLM 확인 생략")
    else:
        try:
            from backend.services.ai.ollama_client import ollama_available, ollama_generate
            from backend.config import OLLAMA_MODEL
            if ollama_available():
                out = ollama_generate("한 줄로 자기소개해주세요.", max_tokens=20, temperature=0.3, timeout=30.0)
                if out and out.strip():
                    log.info("LLM 서버 연결·모델 작동 확인: %s", OLLAMA_MODEL)
                else:
                    log.warning("LLM 서버 연결됐으나 모델 응답 없음: %s", OLLAMA_MODEL)
            else:
                log.warning("LLM 서버 미연결 (호스트에서 ollama serve 또는 scripts/llm_server_check.py --start-if-missing 권장)")
        except Exception as e:
            log.debug("LLM 확인 중 예외: %s", e)


@app.on_event("startup")
def on_startup():
    """앱 기동 시 DB 테이블이 없으면 생성 (labels 등). /knowledge 등 페이지 500 방지."""
    try:
        init_db()
    except Exception as e:
        logging.getLogger(__name__).warning("DB 초기화 실패 (테이블이 이미 있거나 DB 연결 문제): %s", e)
    threading.Thread(target=_llm_check_after_startup, daemon=True).start()


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """루트 페이지 - 대시보드로 리다이렉트"""
    if templates:
        return templates.TemplateResponse("dashboard.html", {"request": request})
    # 템플릿이 없으면 직접 HTML 파일 읽기
    dashboard_file = templates_dir / "dashboard.html"
    if dashboard_file.exists():
        with open(dashboard_file, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Personal AI Brain</h1><p>웹 UI가 아직 구축되지 않았습니다.</p>")


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """대시보드 페이지"""
    if templates:
        return templates.TemplateResponse("dashboard.html", {"request": request})
    # 템플릿이 없으면 직접 HTML 파일 읽기
    dashboard_file = templates_dir / "dashboard.html"
    if dashboard_file.exists():
        with open(dashboard_file, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Dashboard</h1><p>대시보드 페이지</p>")


@app.get("/search", response_class=HTMLResponse)
async def search_page(request: Request):
    """검색 페이지"""
    if templates:
        return templates.TemplateResponse("search.html", {"request": request})
    # 템플릿이 없으면 직접 HTML 파일 읽기
    search_file = templates_dir / "search.html"
    if search_file.exists():
        with open(search_file, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Search</h1><p>검색 페이지</p>")


@app.get("/document/{document_id:path}", response_class=HTMLResponse)
async def document_page(request: Request, document_id: str):
    """문서 뷰어 페이지"""
    if templates:
        return templates.TemplateResponse("document.html", {"request": request, "document_id": document_id})
    # 템플릿이 없으면 직접 HTML 파일 읽기
    doc_file = templates_dir / "document.html"
    if doc_file.exists():
        with open(doc_file, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content=f"<h1>Document</h1><p>문서: {document_id}</p>")


@app.get("/ask", response_class=HTMLResponse)
async def ask_page(request: Request):
    """AI 질의 페이지"""
    if templates:
        return templates.TemplateResponse("ask.html", {"request": request})
    # 템플릿이 없으면 직접 HTML 파일 읽기
    ask_file = templates_dir / "ask.html"
    if ask_file.exists():
        with open(ask_file, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Ask</h1><p>AI 질의 페이지</p>")


@app.get("/logs", response_class=HTMLResponse)
async def logs_page(request: Request):
    """로그 뷰어 페이지"""
    if templates:
        return templates.TemplateResponse("logs.html", {"request": request})
    # 템플릿이 없으면 직접 HTML 파일 읽기
    logs_file = templates_dir / "logs.html"
    if logs_file.exists():
        with open(logs_file, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Logs</h1><p>로그 뷰어 페이지</p>")


@app.get("/knowledge", response_class=HTMLResponse)
async def knowledge_page(request: Request):
    """Knowledge Studio 페이지"""
    if templates:
        return templates.TemplateResponse("knowledge/knowledge.html", {"request": request})
    # 템플릿이 없으면 직접 HTML 파일 읽기
    knowledge_file = templates_dir / "knowledge" / "knowledge.html"
    if knowledge_file.exists():
        with open(knowledge_file, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Knowledge Studio</h1><p>지식 구조 탐색 페이지</p>")


@app.get("/knowledge-detail", response_class=HTMLResponse)
async def knowledge_detail_page(request: Request):
    """청크 상세 페이지"""
    if templates:
        return templates.TemplateResponse("knowledge/knowledge-detail.html", {"request": request})
    # 템플릿이 없으면 직접 HTML 파일 읽기
    detail_file = templates_dir / "knowledge" / "knowledge-detail.html"
    if detail_file.exists():
        with open(detail_file, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>청크 상세</h1><p>청크 상세 정보 페이지</p>")


@app.get("/knowledge-label-matching", response_class=HTMLResponse)
async def knowledge_label_matching_page(request: Request):
    """라벨 매칭 페이지"""
    if templates:
        return templates.TemplateResponse("knowledge/knowledge-label-matching.html", {"request": request})
    # 템플릿이 없으면 직접 HTML 파일 읽기
    label_matching_file = templates_dir / "knowledge" / "knowledge-label-matching.html"
    if label_matching_file.exists():
        with open(label_matching_file, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>라벨 매칭</h1><p>라벨 매칭 페이지</p>")


@app.get("/knowledge-relation-matching", response_class=HTMLResponse)
async def knowledge_relation_matching_page(request: Request):
    """관계 매칭 페이지"""
    if templates:
        return templates.TemplateResponse("knowledge/knowledge-relation-matching.html", {"request": request})
    # 템플릿이 없으면 직접 HTML 파일 읽기
    relation_matching_file = templates_dir / "knowledge" / "knowledge-relation-matching.html"
    if relation_matching_file.exists():
        with open(relation_matching_file, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>관계 매칭</h1><p>관계 매칭 페이지</p>")


@app.get("/reason", response_class=HTMLResponse)
async def reason_page(request: Request):
    """Reasoning Lab 페이지"""
    if templates:
        return templates.TemplateResponse("reason.html", {"request": request})
    # 템플릿이 없으면 직접 HTML 파일 읽기
    reason_file = templates_dir / "reason.html"
    if reason_file.exists():
        with open(reason_file, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Reasoning Lab</h1><p>Reasoning 실행 페이지</p>")


@app.get("/knowledge-admin", response_class=HTMLResponse)
async def knowledge_admin_page(request: Request):
    """[DEPRECATED] Knowledge Admin 페이지 - 개별 관리자 페이지로 분리됨"""
    if templates:
        return templates.TemplateResponse("knowledge/knowledge-admin.html", {"request": request})
    # 템플릿이 없으면 직접 HTML 파일 읽기
    admin_file = templates_dir / "knowledge" / "knowledge-admin.html"
    if admin_file.exists():
        with open(admin_file, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Knowledge Admin</h1><p>지식 구조 관리 페이지</p>")


@app.get("/admin/labels", response_class=HTMLResponse)
async def admin_labels_page(request: Request):
    """라벨 관리 페이지"""
    if templates:
        return templates.TemplateResponse("admin/labels.html", {"request": request})
    # 템플릿이 없으면 직접 HTML 파일 읽기
    labels_file = templates_dir / "admin" / "labels.html"
    if labels_file.exists():
        with open(labels_file, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>라벨 관리</h1><p>라벨 관리 페이지</p>")


@app.get("/admin/groups", response_class=HTMLResponse)
async def admin_groups_page(request: Request):
    """키워드 그룹 관리 페이지"""
    if templates:
        return templates.TemplateResponse("admin/groups.html", {"request": request})
    # 템플릿이 없으면 직접 HTML 파일 읽기
    groups_file = templates_dir / "admin" / "groups.html"
    if groups_file.exists():
        with open(groups_file, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>키워드 그룹 관리</h1><p>키워드 그룹 관리 페이지</p>")


@app.get("/admin/approval", response_class=HTMLResponse)
async def admin_approval_page(request: Request):
    """청크 승인 센터 페이지"""
    if templates:
        return templates.TemplateResponse("admin/approval.html", {"request": request})
    # 템플릿이 없으면 직접 HTML 파일 읽기
    approval_file = templates_dir / "admin" / "approval.html"
    if approval_file.exists():
        with open(approval_file, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>청크 승인 센터</h1><p>청크 승인 센터 페이지</p>")


@app.get("/admin/chunk-labels", response_class=HTMLResponse)
async def admin_chunk_labels_page(request: Request):
    """청크 라벨 관리 페이지"""
    if templates:
        return templates.TemplateResponse("admin/chunk-labels.html", {"request": request})
    chunk_labels_file = templates_dir / "admin" / "chunk-labels.html"
    if chunk_labels_file.exists():
        with open(chunk_labels_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>청크 관리</h1><p>청크 라벨 관리 페이지</p>")


@app.get("/admin/chunk-create", response_class=HTMLResponse)
async def admin_chunk_create_page(request: Request):
    """청크 생성 페이지"""
    if templates:
        return templates.TemplateResponse("admin/chunk-create.html", {"request": request})
    chunk_create_file = templates_dir / "admin" / "chunk-create.html"
    if chunk_create_file.exists():
        with open(chunk_create_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>청크 생성</h1><p>청크 생성 페이지</p>")


@app.get("/admin/statistics", response_class=HTMLResponse)
async def admin_statistics_page(request: Request):
    """통계 대시보드 페이지 (Phase 9-4-2)"""
    if templates:
        return templates.TemplateResponse("admin/statistics.html", {"request": request})
    statistics_file = templates_dir / "admin" / "statistics.html"
    if statistics_file.exists():
        with open(statistics_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Statistics</h1><p>통계 대시보드 페이지</p>")


# ============================================
# Phase 11-3: Admin Settings Management Pages
# ============================================

@app.get("/admin/settings/templates", response_class=HTMLResponse)
async def admin_settings_templates_page(request: Request):
    """Admin Template 관리 페이지 (Phase 11-3)"""
    if templates:
        return templates.TemplateResponse("admin/settings/templates.html", {"request": request})
    template_file = templates_dir / "admin" / "settings" / "templates.html"
    if template_file.exists():
        with open(template_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Templates</h1><p>Admin Template 관리 페이지</p>")


@app.get("/admin/settings/presets", response_class=HTMLResponse)
async def admin_settings_presets_page(request: Request):
    """Admin Prompt Preset 관리 페이지 (Phase 11-3)"""
    if templates:
        return templates.TemplateResponse("admin/settings/presets.html", {"request": request})
    preset_file = templates_dir / "admin" / "settings" / "presets.html"
    if preset_file.exists():
        with open(preset_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Presets</h1><p>Admin Prompt Preset 관리 페이지</p>")


@app.get("/admin/settings/rag-profiles", response_class=HTMLResponse)
async def admin_settings_rag_profiles_page(request: Request):
    """Admin RAG Profile 관리 페이지 (Phase 11-3)"""
    if templates:
        return templates.TemplateResponse("admin/settings/rag-profiles.html", {"request": request})
    rag_file = templates_dir / "admin" / "settings" / "rag-profiles.html"
    if rag_file.exists():
        with open(rag_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>RAG Profiles</h1><p>Admin RAG Profile 관리 페이지</p>")


@app.get("/admin/settings/policy-sets", response_class=HTMLResponse)
async def admin_settings_policy_sets_page(request: Request):
    """Admin Policy Set 관리 페이지 (Phase 11-3)"""
    if templates:
        return templates.TemplateResponse("admin/settings/policy-sets.html", {"request": request})
    policy_file = templates_dir / "admin" / "settings" / "policy-sets.html"
    if policy_file.exists():
        with open(policy_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Policy Sets</h1><p>Admin Policy Set 관리 페이지</p>")


@app.get("/admin/settings/audit-logs", response_class=HTMLResponse)
async def admin_settings_audit_logs_page(request: Request):
    """Admin Audit Log 뷰어 페이지 (Phase 11-3)"""
    if templates:
        return templates.TemplateResponse("admin/settings/audit-logs.html", {"request": request})
    audit_file = templates_dir / "admin" / "settings" / "audit-logs.html"
    if audit_file.exists():
        with open(audit_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Audit Logs</h1><p>Admin Audit Log 뷰어 페이지</p>")


@app.get("/health")
async def health():
    """헬스 체크"""
    return {"status": "ok"}

