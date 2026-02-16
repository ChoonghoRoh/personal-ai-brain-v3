"""FastAPI 메인 애플리케이션"""
import logging
import os
import sys
import subprocess
import threading
import time
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException

from fastapi.middleware.cors import CORSMiddleware

from backend.routers.search import search, documents
from backend.routers.system import system, backup, integrity, logs, error_logs, statistics
from backend.routers.system.backup import legacy_router as backup_legacy_router
from backend.routers.ai import ai, conversations
from backend.routers.knowledge import knowledge, labels, relations, approval, suggestions, knowledge_integration, folder_management
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
    EXTERNAL_PORT,
)
from backend.middleware.security import SecurityHeadersMiddleware
from backend.middleware.request_id import RequestIDMiddleware  # Phase 12-2-4
from backend.middleware.rate_limit import setup_rate_limiting
from backend.middleware.error_handler import setup_error_handlers  # Phase 12-2-4
from backend.middleware.page_access_log import PageAccessLogMiddleware  # Phase 13-4
from backend.models.database import init_db

# ============================================
# OpenAPI 태그 정의 (Phase 14-2)
# ============================================
openapi_tags = [
    # Authentication
    {"name": "Authentication", "description": "JWT 토큰 발급 및 API Key 인증"},
    # User Features
    {"name": "Search", "description": "문서 및 청크 검색 (의미·키워드·하이브리드)"},
    {"name": "Documents", "description": "문서 관리 및 조회"},
    {"name": "AI", "description": "AI 질의응답 (RAG 기반)"},
    {"name": "Conversations", "description": "대화 기록 저장 및 검색"},
    # Knowledge
    {"name": "Knowledge", "description": "지식 청크 CRUD 및 조회"},
    {"name": "Labels", "description": "라벨 및 키워드 그룹 관리"},
    {"name": "Relations", "description": "청크 간 관계 관리"},
    {"name": "Approval", "description": "청크 승인 워크플로우"},
    {"name": "Suggestions", "description": "AI 기반 라벨/관계 추천"},
    {"name": "Knowledge Integration", "description": "지식 통합 및 모순 해결"},
    # Reasoning
    {"name": "Reasoning", "description": "추론 엔진 (기본 질의)"},
    {"name": "Reasoning Stream", "description": "스트리밍 추론 (SSE)"},
    {"name": "Reasoning Store", "description": "추론 결과 공유 및 저장"},
    {"name": "Reasoning Chain", "description": "다단계 추론 체인"},
    {"name": "Reasoning Results", "description": "추론 결과 조회"},
    {"name": "Recommendations", "description": "추론 기반 추천"},
    # Cognitive
    {"name": "Memory", "description": "장기/단기/작업 기억 시스템"},
    {"name": "Context", "description": "맥락 이해 및 연결"},
    {"name": "Learning", "description": "사용자 패턴 학습"},
    {"name": "Personality", "description": "인격 프로필 관리"},
    {"name": "Metacognition", "description": "신뢰도 및 불확실성 분석"},
    # System
    {"name": "System", "description": "시스템 상태 및 정보"},
    {"name": "Logs", "description": "작업 로그 조회"},
    {"name": "Backup", "description": "데이터 백업 및 복원"},
    {"name": "Integrity", "description": "데이터 무결성 검증"},
    {"name": "Error Logs", "description": "에러 로그 및 통계"},
    {"name": "Statistics", "description": "시스템 통계 및 분석"},
    # Automation
    {"name": "Automation", "description": "자동화 작업 (라벨링 등)"},
    {"name": "Workflow", "description": "워크플로우 실행 (n8n 연동)"},
    {"name": "File Parser", "description": "파일 파싱 및 변환"},
    # Admin Settings (require admin_system)
    {"name": "Admin - Schemas", "description": "스키마 관리 (admin_system 권한)"},
    {"name": "Admin - Templates", "description": "템플릿 관리 (admin_system 권한)"},
    {"name": "Admin - Presets", "description": "프롬프트 프리셋 (admin_system 권한)"},
    {"name": "Admin - RAG Profiles", "description": "RAG 프로필 (admin_system 권한)"},
    {"name": "Admin - Policy Sets", "description": "정책 세트 (admin_system 권한)"},
    {"name": "Admin - Audit Logs", "description": "변경 이력 (admin_system 권한)"},
    {"name": "Admin - Page Access Logs", "description": "페이지 접근 로그 (admin_system 권한)"},
    {"name": "Admin - Users", "description": "사용자 관리 (admin_system 권한)"},
]

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

    ## 역할 기반 접근 제어 (Phase 14-1)

    - **user**: 기본 사용자 (검색, AI 질의 등)
    - **admin_knowledge**: 지식 관리 권한 (청크, 라벨, 관계 등)
    - **admin_system**: 시스템 관리 권한 (설정, 스키마, 감사 로그 등)
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
            "url": f"http://localhost:{EXTERNAL_PORT}",
            "description": "로컬 개발 서버"
        },
    ],
    openapi_tags=openapi_tags,
)


# ============================================
# OpenAPI securitySchemes 커스터마이징 (Phase 14-2)
# ============================================
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=openapi_tags,
        servers=app.servers,
        contact=app.contact,
        license_info=app.license_info,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "BearerToken": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT Bearer 토큰. /api/auth/token에서 발급받은 토큰을 사용합니다.",
        },
        "APIKey": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "API Key 헤더. 환경변수 API_SECRET_KEY에 설정된 키를 사용합니다.",
        },
    }

    # 전역 보안 적용 (모든 엔드포인트에 기본 적용, 개별 제외 가능)
    openapi_schema["security"] = [
        {"BearerToken": []},
        {"APIKey": []},
    ]

    # 인증 불필요 경로에 security: [] 설정 (전역 security 제외)
    auth_excluded_prefixes = ("/api/auth/token", "/api/auth/login", "/health")
    for path, methods in openapi_schema.get("paths", {}).items():
        if path.startswith(auth_excluded_prefixes):
            for method_detail in methods.values():
                if isinstance(method_detail, dict):
                    method_detail["security"] = []

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

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

# Request ID 미들웨어 (Phase 12-2-4)
app.add_middleware(RequestIDMiddleware)

# 페이지 접근 로그 미들웨어 (Phase 13-4)
app.add_middleware(PageAccessLogMiddleware)

# ============================================
# Rate Limiting 설정 (Phase 9-1-4)
# ============================================
setup_rate_limiting(app)

# ============================================
# 전역 에러 핸들러 (Phase 12-2-4)
# ============================================
setup_error_handlers(app)

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
app.include_router(folder_management.router)  # Phase 15-1-1: 지정 폴더 경로 설정
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


def _seed_admin_user() -> None:
    """Phase 14-5-2: 초기 관리자 계정이 없으면 생성"""
    from backend.config import ADMIN_DEFAULT_USERNAME, ADMIN_DEFAULT_PASSWORD
    from backend.models.database import SessionLocal
    from backend.models.user_models import User
    from passlib.context import CryptContext

    log = logging.getLogger(__name__)
    pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == ADMIN_DEFAULT_USERNAME).first()
        if not existing:
            admin_user = User(
                username=ADMIN_DEFAULT_USERNAME,
                hashed_password=pwd_ctx.hash(ADMIN_DEFAULT_PASSWORD),
                display_name="System Administrator",
                role="admin_system",
                is_active=True,
            )
            db.add(admin_user)
            db.commit()
            log.info("초기 관리자 계정 생성: %s (role=admin_system)", ADMIN_DEFAULT_USERNAME)
        else:
            log.debug("관리자 계정 이미 존재: %s", ADMIN_DEFAULT_USERNAME)
    except Exception as e:
        db.rollback()
        log.warning("초기 관리자 시드 실패: %s", e)
    finally:
        db.close()


@app.on_event("startup")
async def on_startup():
    """앱 기동 시 DB 테이블이 없으면 생성 (labels 등). /knowledge 등 페이지 500 방지."""
    try:
        init_db()
    except Exception as e:
        logging.getLogger(__name__).warning("DB 초기화 실패 (테이블이 이미 있거나 DB 연결 문제): %s", e)

    # Phase 14-5-2: 초기 관리자 계정 시드
    try:
        _seed_admin_user()
    except Exception as e:
        logging.getLogger(__name__).warning("초기 관리자 시드 중 오류: %s", e)

    threading.Thread(target=_llm_check_after_startup, daemon=True).start()

    # Phase 12-3-4: 만료 기억 자동 정리 스케줄러
    from backend.services.cognitive.memory_scheduler import start_memory_cleanup
    await start_memory_cleanup()


@app.on_event("shutdown")
async def on_shutdown():
    """앱 종료 시 스케줄러 정리 (Phase 12-3-4)"""
    from backend.services.cognitive.memory_scheduler import stop_memory_cleanup
    await stop_memory_cleanup()


# ============================================
# HTML Page Routes (Phase 13-2-3: 일괄 등록)
# ============================================
# (path, template_path, fallback_title)
_HTML_ROUTES = [
    ("/", "dashboard.html", "Personal AI Brain"),
    ("/login", "login.html", "로그인"),
    ("/dashboard", "dashboard.html", "대시보드"),
    ("/search", "search.html", "검색"),
    ("/ask", "ask.html", "AI 질의"),
    ("/logs", "logs.html", "로그"),
    ("/knowledge", "knowledge/knowledge.html", "Knowledge Studio"),
    ("/knowledge-detail", "knowledge/knowledge-detail.html", "청크 상세"),
    ("/knowledge-label-matching", "knowledge/knowledge-label-matching.html", "라벨 매칭"),
    ("/knowledge-relation-matching", "knowledge/knowledge-relation-matching.html", "관계 매칭"),
    ("/reason", "reason.html", "Reasoning Lab"),
    ("/knowledge-admin", "knowledge/knowledge-admin.html", "Knowledge Admin"),
    ("/admin/labels", "admin/labels.html", "라벨 관리"),
    ("/admin/groups", "admin/groups.html", "키워드 그룹 관리"),
    ("/admin/approval", "admin/approval.html", "청크 승인 센터"),
    ("/admin/chunk-labels", "admin/chunk-labels.html", "청크 관리"),
    ("/admin/chunk-create", "admin/chunk-create.html", "청크 생성"),
    ("/admin/knowledge-files", "admin/knowledge-files.html", "파일관리"),
    ("/admin/ai-automation", "admin/ai-automation.html", "AI 자동화"),
    ("/admin/statistics", "admin/statistics.html", "통계 대시보드"),
    ("/admin/settings/templates", "admin/settings/templates.html", "템플릿 관리"),
    ("/admin/settings/presets", "admin/settings/presets.html", "프리셋 관리"),
    ("/admin/settings/rag-profiles", "admin/settings/rag-profiles.html", "RAG 프로필 관리"),
    ("/admin/settings/policy-sets", "admin/settings/policy-sets.html", "정책 관리"),
    ("/admin/settings/audit-logs", "admin/settings/audit-logs.html", "변경 이력"),
]


def _register_html_routes(application: FastAPI) -> None:
    """HTML 라우트 일괄 등록"""
    for route_path, tpl_path, title in _HTML_ROUTES:
        def _make_handler(_tp=tpl_path, _tl=title):
            async def _handler(request: Request):
                if templates:
                    return templates.TemplateResponse(_tp, {"request": request})
                fp = templates_dir / _tp
                if fp.exists():
                    with open(fp, "r", encoding="utf-8") as f:
                        return HTMLResponse(content=f.read())
                return HTMLResponse(content=f"<h1>{_tl}</h1>")
            return _handler
        application.get(route_path, response_class=HTMLResponse)(_make_handler())


_register_html_routes(app)


# 동적 경로 라우트 (path parameter)
@app.get("/document/{document_id:path}", response_class=HTMLResponse)
async def document_page(request: Request, document_id: str):
    """문서 뷰어 페이지"""
    if templates:
        return templates.TemplateResponse("document.html", {"request": request, "document_id": document_id})
    doc_file = templates_dir / "document.html"
    if doc_file.exists():
        with open(doc_file, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content=f"<h1>Document</h1><p>문서: {document_id}</p>")


@app.get("/health")
async def health():
    """헬스 체크 (Liveness — 기존 호환)"""
    return {"status": "ok"}


@app.get("/health/live")
async def health_live():
    """Liveness probe — 프로세스 생존 확인"""
    return {"status": "ok"}


@app.get("/health/ready")
async def health_ready():
    """Readiness probe — 의존 서비스 연결 확인 (Phase 12-3-5)"""
    checks = {}
    all_ok = True

    # PostgreSQL 연결 확인
    try:
        from backend.models.database import SessionLocal
        from sqlalchemy import text
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        checks["postgres"] = "ok"
    except Exception as e:
        checks["postgres"] = f"error: {type(e).__name__}"
        all_ok = False

    # Qdrant 연결 확인
    try:
        from qdrant_client import QdrantClient
        from backend.config import QDRANT_HOST, QDRANT_PORT
        qc = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT, timeout=5)
        qc.get_collections()
        checks["qdrant"] = "ok"
    except Exception as e:
        checks["qdrant"] = f"error: {type(e).__name__}"
        all_ok = False

    # Redis 연결 확인 (선택적 — REDIS_URL 미설정 시 skip)
    try:
        from backend.config import REDIS_URL
        if REDIS_URL:
            import redis
            r = redis.from_url(REDIS_URL, socket_timeout=3)
            r.ping()
            checks["redis"] = "ok"
        else:
            checks["redis"] = "skipped (not configured)"
    except Exception as e:
        checks["redis"] = f"error: {type(e).__name__}"
        all_ok = False

    from fastapi.responses import JSONResponse
    status_code = 200 if all_ok else 503
    return JSONResponse(
        status_code=status_code,
        content={"status": "ok" if all_ok else "degraded", "checks": checks},
    )


# ============================================
# HTML 404 핸들러 (Phase 13-2-2)
# ============================================

@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Accept: text/html 요청 시 404.html 반환, 그 외 JSON 404 유지"""
    if exc.status_code == 404:
        accept = request.headers.get("accept", "")
        if "text/html" in accept:
            not_found_file = templates_dir / "404.html" if templates_dir else None
            if not_found_file and not_found_file.exists():
                with open(not_found_file, "r", encoding="utf-8") as f:
                    return HTMLResponse(content=f.read(), status_code=404)
            return HTMLResponse(
                content="<h1>404</h1><p>페이지를 찾을 수 없습니다.</p>",
                status_code=404,
            )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail or "Not Found"},
    )

