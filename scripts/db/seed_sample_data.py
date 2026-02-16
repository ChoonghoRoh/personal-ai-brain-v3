"""Phase 14-6: DB 샘플 데이터 시드 스크립트

사용법:
    docker compose exec backend python scripts/db/seed_sample_data.py

기준 문서: docs/planning/260210-1400-db-sample-data-and-high-level-strategy.md
"""
import os
import sys
import random
import hashlib
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

# 프로젝트 루트를 path에 추가
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy.orm import Session
from sqlalchemy import text

from backend.models.database import SessionLocal, engine
from backend.models.models import (
    Project, Document, KnowledgeChunk, Label, KnowledgeLabel, KnowledgeRelation,
    Memory, Conversation, ReasoningResult,
)
from backend.models.admin_models import (
    AdminSchema, AdminTemplate, AdminPromptPreset,
    AdminRagProfile, AdminContextRule, AdminPolicySet, AdminAuditLog,
)


def log(msg: str):
    print(f"[SEED] {msg}")


# ============================================
# 1. Projects 시드
# ============================================
PROJECTS_DATA = [
    ("personal-ai-brain", str(PROJECT_ROOT), "메인 프로젝트: 개인 AI 브레인 시스템"),
    ("docs", str(PROJECT_ROOT / "docs"), "프로젝트 문서 (phases, planning, rules)"),
    ("backend", str(PROJECT_ROOT / "backend"), "FastAPI 백엔드 서비스"),
    ("web", str(PROJECT_ROOT / "web"), "프론트엔드 웹 애플리케이션"),
    ("scripts", str(PROJECT_ROOT / "scripts"), "유틸리티·데이터베이스·개발 스크립트"),
    ("brain", str(PROJECT_ROOT / "brain"), "AI 브레인 코어 모듈"),
    ("collector", str(PROJECT_ROOT / "collector"), "데이터 수집·파싱 모듈"),
    ("e2e-tests", str(PROJECT_ROOT / "e2e"), "E2E 테스트 스위트"),
]


def seed_projects(db: Session) -> dict:
    existing = {p.name for p in db.query(Project).all()}
    created = 0
    project_map = {}
    for name, path, desc in PROJECTS_DATA:
        if name not in existing:
            p = Project(name=name, path=path, description=desc)
            db.add(p)
            db.flush()
            project_map[name] = p.id
            created += 1
        else:
            proj = db.query(Project).filter(Project.name == name).first()
            project_map[name] = proj.id
    db.commit()
    log(f"Projects: {created} created, total mapped={len(project_map)}")
    return project_map


# ============================================
# 2. Labels 시드 (목표 100+, 현재 202)
# ============================================
EXTRA_LABELS = [
    # keyword 타입 추가
    ("python", "keyword"), ("javascript", "keyword"), ("fastapi", "keyword"),
    ("react", "keyword"), ("postgresql", "keyword"), ("docker", "keyword"),
    ("qdrant", "keyword"), ("ollama", "keyword"), ("jwt", "keyword"),
    ("bcrypt", "keyword"), ("swagger", "keyword"), ("openapi", "keyword"),
    ("embedding", "keyword"), ("vector-search", "keyword"), ("rag", "keyword"),
    ("reasoning", "keyword"), ("memory", "keyword"), ("conversation", "keyword"),
    ("backup", "keyword"), ("migration", "keyword"),
    # domain 타입 추가
    ("backend-api", "domain"), ("frontend-ui", "domain"), ("database", "domain"),
    ("security", "domain"), ("testing", "domain"), ("devops", "domain"),
    ("ai-ml", "domain"), ("documentation", "domain"), ("architecture", "domain"),
    ("performance", "domain"),
]


def seed_labels(db: Session) -> dict:
    existing = {(l.name, l.label_type) for l in db.query(Label).all()}
    created = 0
    for name, ltype in EXTRA_LABELS:
        if (name, ltype) not in existing:
            db.add(Label(name=name, label_type=ltype))
            created += 1
    db.commit()
    label_map = {(l.name, l.label_type): l.id for l in db.query(Label).all()}
    log(f"Labels: {created} created, total={len(label_map)}")
    return label_map


# ============================================
# 3. Documents 시드 (목표 100+)
# ============================================
def seed_documents(db: Session, project_map: dict, label_map: dict) -> dict:
    existing_paths = {d.file_path for d in db.query(Document).all()}

    # docs/ 하위 .md 파일 스캔
    docs_dir = PROJECT_ROOT / "docs"
    md_files = sorted(docs_dir.rglob("*.md"))

    # 카테고리 분류
    def classify(path_str: str) -> str:
        if "phase" in path_str and ("task" in path_str or "plan" in path_str):
            return "development"
        if "planning" in path_str or "master-plan" in path_str or "roadmap" in path_str:
            return "planning"
        if "qc" in path_str or "verification" in path_str or "test-report" in path_str:
            return "review"
        if "rules" in path_str or "SSOT" in path_str or "ssot" in path_str:
            return "rules"
        if "llm" in path_str or "reasoning" in path_str or "prompt" in path_str or "ai" in path_str:
            return "ai"
        return "general"

    # 프로젝트 매핑
    def get_project_id(rel_path: str) -> int:
        if rel_path.startswith("docs/"):
            return project_map.get("docs", project_map.get("personal-ai-brain"))
        return project_map.get("personal-ai-brain", 1)

    created = 0
    doc_map = {}

    for md_file in md_files[:150]:  # 최대 150개
        rel_path = str(md_file.relative_to(PROJECT_ROOT))
        if rel_path in existing_paths:
            doc = db.query(Document).filter(Document.file_path == rel_path).first()
            if doc:
                doc_map[rel_path] = doc.id
            continue

        try:
            file_size = md_file.stat().st_size
        except OSError:
            file_size = 0

        category = classify(rel_path)
        cat_label_id = label_map.get((category, "category"))

        doc = Document(
            project_id=get_project_id(rel_path),
            file_path=rel_path,
            file_name=md_file.name,
            file_type="md",
            size=file_size,
            category_label_id=cat_label_id,
        )
        db.add(doc)
        db.flush()
        doc_map[rel_path] = doc.id
        created += 1

    db.commit()
    # 기존 문서도 매핑
    for doc in db.query(Document).all():
        doc_map[doc.file_path] = doc.id

    log(f"Documents: {created} created, total mapped={len(doc_map)}")
    return doc_map


# ============================================
# 4. Knowledge Chunks 시드 (목표 300+)
# ============================================
def seed_chunks(db: Session, doc_map: dict) -> list:
    existing_doc_ids = {c.document_id for c in db.query(KnowledgeChunk.document_id).distinct().all()}
    existing_count = db.query(KnowledgeChunk).count()
    target = max(0, 300 - existing_count)

    if target <= 0:
        log(f"Chunks: already {existing_count} (target 300), skip")
        return [c.id for c in db.query(KnowledgeChunk).all()]

    created = 0
    for rel_path, doc_id in doc_map.items():
        if created >= target:
            break
        if doc_id in existing_doc_ids:
            continue

        md_file = PROJECT_ROOT / rel_path
        if not md_file.exists():
            continue

        try:
            content = md_file.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue

        if len(content) < 50:
            continue

        # heading 기반 분할
        sections = []
        current = []
        for line in content.split("\n"):
            if line.startswith("## ") and current:
                sections.append("\n".join(current))
                current = [line]
            else:
                current.append(line)
        if current:
            sections.append("\n".join(current))

        # 각 섹션을 청크로
        for idx, section in enumerate(sections[:5]):  # 문서당 최대 5청크
            if len(section.strip()) < 30:
                continue
            chunk_content = section[:2000]  # 최대 2000자
            # 제목 추출
            title = None
            for line in section.split("\n"):
                if line.startswith("#"):
                    title = line.lstrip("#").strip()[:200]
                    break

            chunk = KnowledgeChunk(
                document_id=doc_id,
                chunk_index=idx,
                content=chunk_content,
                status="approved",
                source="human_created",
                version=1,
                title=title,
            )
            db.add(chunk)
            created += 1
            if created >= target:
                break

    db.commit()
    all_ids = [c.id for c in db.query(KnowledgeChunk).all()]
    log(f"Chunks: {created} created, total={len(all_ids)}")
    return all_ids


# ============================================
# 5. Knowledge Labels 시드 (목표 500+)
# ============================================
def seed_knowledge_labels(db: Session, label_map: dict, chunk_ids: list):
    existing_count = db.query(KnowledgeLabel).count()
    target = max(0, 500 - existing_count)
    if target <= 0:
        log(f"KnowledgeLabels: already {existing_count} (target 500), skip")
        return

    existing_pairs = set(
        db.query(KnowledgeLabel.chunk_id, KnowledgeLabel.label_id).all()
    )

    keyword_labels = [lid for (name, lt), lid in label_map.items() if lt == "keyword"]
    if not keyword_labels:
        log("KnowledgeLabels: no keyword labels found, skip")
        return

    created = 0
    for chunk_id in chunk_ids:
        if created >= target:
            break
        # 각 청크에 1~3개 라벨 연결
        n_labels = random.randint(1, 3)
        selected = random.sample(keyword_labels, min(n_labels, len(keyword_labels)))
        for label_id in selected:
            if (chunk_id, label_id) not in existing_pairs:
                db.add(KnowledgeLabel(chunk_id=chunk_id, label_id=label_id))
                existing_pairs.add((chunk_id, label_id))
                created += 1
                if created >= target:
                    break

    db.commit()
    total = db.query(KnowledgeLabel).count()
    log(f"KnowledgeLabels: {created} created, total={total}")


# ============================================
# 6. Knowledge Relations 시드 (목표 50~200)
# ============================================
def seed_relations(db: Session, chunk_ids: list):
    existing_count = db.query(KnowledgeRelation).count()
    target = max(0, 50 - existing_count)
    if target <= 0:
        log(f"Relations: already {existing_count} (target 50), skip")
        return

    relation_types = ["references", "similar", "parent_child", "related", "extends"]
    existing = set(
        (r.source_chunk_id, r.target_chunk_id)
        for r in db.query(KnowledgeRelation).all()
    )
    created = 0
    for _ in range(target * 2):
        if created >= target:
            break
        src = random.choice(chunk_ids)
        tgt = random.choice(chunk_ids)
        if src != tgt and (src, tgt) not in existing:
            db.add(KnowledgeRelation(
                source_chunk_id=src,
                target_chunk_id=tgt,
                relation_type=random.choice(relation_types),
                confidence=round(random.uniform(0.5, 1.0), 2),
            ))
            existing.add((src, tgt))
            created += 1

    db.commit()
    log(f"Relations: {created} created, total={db.query(KnowledgeRelation).count()}")


# ============================================
# 7. Memories 시드 (목표 100+)
# ============================================
MEMORY_CATEGORIES = ["learning", "interaction", "knowledge", "system", "preference"]
MEMORY_TYPES = ["long_term", "short_term", "working"]

MEMORY_TEMPLATES = [
    "사용자가 {topic}에 대해 질문함",
    "{topic} 관련 문서를 검색하여 참조함",
    "{topic} 프로젝트의 구조를 학습함",
    "반복 패턴 감지: {topic} 관련 질의가 자주 발생",
    "{topic} 설정을 변경함",
    "새로운 {topic} 문서가 추가됨",
    "{topic} 검색 결과의 품질이 개선됨",
    "{topic} 관련 추론 결과를 저장함",
]
TOPICS = [
    "RAG 파이프라인", "벡터 검색", "PostgreSQL", "FastAPI", "JWT 인증",
    "Ollama LLM", "문서 청크화", "라벨 관리", "추론 체인", "기억 시스템",
    "백업 복원", "Admin 설정", "E2E 테스트", "Docker 배포", "프롬프트 엔지니어링",
]


def seed_memories(db: Session, chunk_ids: list):
    existing_count = db.query(Memory).count()
    target = max(0, 100 - existing_count)
    if target <= 0:
        log(f"Memories: already {existing_count} (target 100), skip")
        return

    now = datetime.now(timezone.utc)
    for i in range(target):
        topic = random.choice(TOPICS)
        template = random.choice(MEMORY_TEMPLATES)
        mem_type = random.choice(MEMORY_TYPES)
        expires = now + timedelta(days=random.randint(1, 365)) if mem_type != "long_term" else None

        m = Memory(
            content=template.format(topic=topic),
            category=random.choice(MEMORY_CATEGORIES),
            memory_type=mem_type,
            importance_score=round(random.uniform(0.1, 1.0), 2),
            related_chunk_id=random.choice(chunk_ids) if random.random() > 0.5 and chunk_ids else None,
            expires_at=expires,
        )
        db.add(m)

    db.commit()
    log(f"Memories: {target} created, total={db.query(Memory).count()}")


# ============================================
# 8. Conversations 시드 (목표 100+)
# ============================================
CONV_QUESTIONS = [
    "RAG 파이프라인은 어떻게 작동하나요?",
    "PostgreSQL에서 GIN 인덱스란 무엇인가요?",
    "FastAPI에서 JWT 인증을 구현하는 방법은?",
    "벡터 검색과 키워드 검색의 차이점은?",
    "Ollama 모델을 변경하려면 어떻게 하나요?",
    "문서 청크화 전략에 대해 설명해주세요",
    "Admin 설정 API의 구조를 알려주세요",
    "E2E 테스트 작성 가이드라인은?",
    "Docker 컨테이너 관리 방법은?",
    "추론 체인의 동작 원리를 설명해주세요",
    "기억 시스템의 만료 정책은 어떻게 되나요?",
    "백업 및 복원 절차를 알려주세요",
    "프롬프트 프리셋 관리 방법은?",
    "RAG 프로필 설정 최적화 방법은?",
    "지식 관계 그래프의 활용 방법은?",
]


def seed_conversations(db: Session):
    existing_count = db.query(Conversation).count()
    target = max(0, 100 - existing_count)
    if target <= 0:
        log(f"Conversations: already {existing_count} (target 100), skip")
        return

    now = datetime.now(timezone.utc)
    for i in range(target):
        question = random.choice(CONV_QUESTIONS)
        session_id = f"session_{random.randint(1, 20):03d}"
        c = Conversation(
            question=question,
            answer=f"{question}에 대한 답변입니다. 관련 문서를 검색하여 종합적으로 분석한 결과를 제공합니다.",
            session_id=session_id,
            sources=f"doc_{random.randint(1, 50)}, chunk_{random.randint(1, 200)}",
            created_at=now - timedelta(hours=random.randint(1, 720)),
        )
        db.add(c)

    db.commit()
    log(f"Conversations: {target} created, total={db.query(Conversation).count()}")


# ============================================
# 9. Reasoning Results 시드 (목표 100+)
# ============================================
REASONING_MODES = ["deep", "quick", "creative", "analytical"]


def seed_reasoning_results(db: Session):
    result = db.execute(text("SELECT COUNT(*) FROM reasoning_results"))
    existing_count = result.scalar()
    target = max(0, 100 - existing_count)
    if target <= 0:
        log(f"ReasoningResults: already {existing_count} (target 100), skip")
        return

    now = datetime.now(timezone.utc)
    for i in range(target):
        question = random.choice(CONV_QUESTIONS)
        mode = random.choice(REASONING_MODES)
        share_id = hashlib.md5(f"{i}_{question}_{random.random()}".encode()).hexdigest()[:12] if random.random() > 0.7 else None
        created_at = now - timedelta(hours=random.randint(1, 720))
        expires_at = now + timedelta(days=random.randint(7, 90)) if random.random() > 0.5 else None

        db.execute(text("""
            INSERT INTO reasoning_results (question, answer, reasoning_steps, mode, session_id, share_id, view_count, is_private, expires_at, created_at)
            VALUES (:q, :a, :steps, :mode, :sid, :share, :vc, :priv, :exp, :cat)
        """), {
            "q": question,
            "a": f"[{mode}] {question}에 대한 추론 결과입니다.",
            "steps": "1단계: 질문 분석\n2단계: 관련 문서 검색\n3단계: 종합 추론\n4단계: 결론 도출",
            "mode": mode,
            "sid": f"reason_{random.randint(1, 30):03d}",
            "share": share_id,
            "vc": random.randint(0, 50),
            "priv": random.random() > 0.3,
            "exp": expires_at,
            "cat": created_at,
        })

    db.commit()
    result2 = db.execute(text("SELECT COUNT(*) FROM reasoning_results"))
    log(f"ReasoningResults: {target} created, total={result2.scalar()}")


# ============================================
# 10. Admin 테이블 시드 (schemas, templates, presets, rag_profiles, context_rules, policy_sets)
# ============================================
SCHEMA_DATA = [
    ("analysis", "분석", "데이터 분석 및 통계"),
    ("summary", "요약", "문서 요약 생성"),
    ("translation", "번역", "다국어 번역"),
    ("extraction", "추출", "정보 추출"),
    ("classification", "분류", "문서/데이터 분류"),
    ("comparison", "비교", "문서 간 비교 분석"),
    ("recommendation", "추천", "콘텐츠 추천"),
    ("validation", "검증", "데이터 유효성 검증"),
    ("generation", "생성", "콘텐츠 생성"),
    ("optimization", "최적화", "파라미터 최적화"),
    ("monitoring", "모니터링", "시스템 모니터링"),
    ("reporting", "리포팅", "보고서 생성"),
    ("debugging", "디버깅", "문제 진단"),
    ("planning", "계획", "프로젝트 계획 수립"),
]

TEMPLATE_TYPES = ["judgment", "summary", "extraction", "analysis", "report", "qa", "instruction"]
PRESET_TASK_TYPES = ["reasoning", "search", "ask", "summarize", "classify", "extract", "translate", "generate"]


def seed_admin_schemas(db: Session) -> list:
    existing = {s.role_key for s in db.query(AdminSchema).all()}
    created = 0
    for role_key, display_name, desc in SCHEMA_DATA:
        if role_key not in existing:
            db.add(AdminSchema(
                role_key=role_key,
                display_name=display_name,
                description=desc,
                is_active=True,
                display_order=len(existing) + created,
            ))
            created += 1
    db.commit()
    all_ids = [str(s.id) for s in db.query(AdminSchema).all()]
    log(f"Schemas: {created} created, total={len(all_ids)}")
    return all_ids


def seed_admin_templates(db: Session):
    existing_count = db.query(AdminTemplate).count()
    target = max(0, 100 - existing_count)
    if target <= 0:
        log(f"Templates: already {existing_count} (target 100), skip")
        return

    for i in range(target):
        ttype = random.choice(TEMPLATE_TYPES)
        db.add(AdminTemplate(
            name=f"{ttype.title()} Template #{existing_count + i + 1}",
            description=f"{ttype} 유형 템플릿 (자동 생성 #{i + 1})",
            template_type=ttype,
            content=f"# {ttype.title()} Template\n\n이 템플릿은 {ttype} 작업에 사용됩니다.\n\n## 입력\n\n{{input}}\n\n## 출력 형식\n\n{{output_format}}",
            output_format="markdown",
            version=1,
            status="active",
        ))

    db.commit()
    log(f"Templates: {target} created, total={db.query(AdminTemplate).count()}")


def seed_admin_presets(db: Session):
    existing_count = db.query(AdminPromptPreset).count()
    target = max(0, 100 - existing_count)
    if target <= 0:
        log(f"Presets: already {existing_count} (target 100), skip")
        return

    for i in range(target):
        task_type = random.choice(PRESET_TASK_TYPES)
        temp = round(random.uniform(0.1, 1.0), 1)
        db.add(AdminPromptPreset(
            name=f"{task_type.title()} Preset #{existing_count + i + 1}",
            task_type=task_type,
            system_prompt=f"You are a helpful AI assistant specialized in {task_type}. Provide accurate and detailed responses.",
            temperature=temp,
            max_tokens=random.choice([512, 1024, 2048, 4096]),
            status="active",
        ))

    db.commit()
    log(f"Presets: {target} created, total={db.query(AdminPromptPreset).count()}")


def seed_admin_rag_profiles(db: Session) -> list:
    existing_count = db.query(AdminRagProfile).count()
    target = max(0, 20 - existing_count)
    if target <= 0:
        log(f"RAG Profiles: already {existing_count} (target 20), skip")
        return [str(r.id) for r in db.query(AdminRagProfile).all()]

    for i in range(target):
        db.add(AdminRagProfile(
            name=f"RAG Profile #{existing_count + i + 1}",
            description=f"청크 크기·top_k·임계값 조합 #{i + 1}",
            chunk_size=random.choice([256, 512, 1024, 2048]),
            chunk_overlap=random.choice([50, 100, 200]),
            top_k=random.choice([3, 5, 10, 15, 20]),
            score_threshold=round(random.uniform(0.3, 0.8), 2),
            use_rerank=random.choice([True, False]),
            status="active",
        ))

    db.commit()
    all_ids = [str(r.id) for r in db.query(AdminRagProfile).all()]
    log(f"RAG Profiles: {target} created, total={len(all_ids)}")
    return all_ids


def seed_admin_context_rules(db: Session):
    existing_count = db.query(AdminContextRule).count()
    target = max(0, 20 - existing_count)
    if target <= 0:
        log(f"Context Rules: already {existing_count} (target 20), skip")
        return

    doc_types = ["md", "pdf", "docx", "txt", "code", "config"]
    domains = ["development", "planning", "review", "rules", "ai", "general"]

    for i in range(target):
        db.add(AdminContextRule(
            rule_name=f"Context Rule #{existing_count + i + 1}",
            document_type=random.choice(doc_types),
            domain_tags=random.sample(domains, random.randint(1, 3)),
            classification_logic={"rule": f"파일 경로에 '{random.choice(domains)}' 포함 시 해당 도메인으로 분류"},
            priority=random.randint(1, 10),
            is_active=True,
        ))

    db.commit()
    log(f"Context Rules: {target} created, total={db.query(AdminContextRule).count()}")


def seed_admin_policy_sets(db: Session):
    existing_count = db.query(AdminPolicySet).count()
    target = max(0, 20 - existing_count)
    if target <= 0:
        log(f"Policy Sets: already {existing_count} (target 20), skip")
        return

    template_ids = [str(t.id) for t in db.query(AdminTemplate).limit(10).all()]
    preset_ids = [str(p.id) for p in db.query(AdminPromptPreset).limit(10).all()]
    rag_ids = [str(r.id) for r in db.query(AdminRagProfile).limit(10).all()]

    for i in range(target):
        db.add(AdminPolicySet(
            name=f"Policy Set #{existing_count + i + 1}",
            description=f"정책 세트 #{i + 1}",
            template_id=random.choice(template_ids) if template_ids else None,
            prompt_preset_id=random.choice(preset_ids) if preset_ids else None,
            rag_profile_id=random.choice(rag_ids) if rag_ids else None,
            priority=random.randint(1, 10),
            is_active=random.choice([True, True, True, False]),  # 75% active
        ))

    db.commit()
    log(f"Policy Sets: {target} created, total={db.query(AdminPolicySet).count()}")


# ============================================
# 11. Audit Logs 시드 (목표 100+)
# ============================================
def seed_audit_logs(db: Session):
    existing_count = db.query(AdminAuditLog).count()
    target = max(0, 100 - existing_count)
    if target <= 0:
        log(f"Audit Logs: already {existing_count} (target 100), skip")
        return

    tables = ["schemas", "templates", "prompt_presets", "rag_profiles", "policy_sets", "context_rules", "users"]
    actions = ["create", "update", "delete"]
    users = ["admin", "system", "api_user"]
    now = datetime.now(timezone.utc)

    for i in range(target):
        action = random.choice(actions)
        table = random.choice(tables)
        db.add(AdminAuditLog(
            table_name=table,
            record_id=str(uuid4()),
            action=action,
            changed_by=random.choice(users),
            old_values={"status": "draft"} if action in ("update", "delete") else None,
            new_values={"status": "active"} if action in ("create", "update") else None,
            created_at=now - timedelta(hours=random.randint(1, 720)),
        ))

    db.commit()
    log(f"Audit Logs: {target} created, total={db.query(AdminAuditLog).count()}")


# ============================================
# Main
# ============================================
def main():
    log("=" * 60)
    log("Phase 14-6: 샘플 데이터 시드 시작")
    log("=" * 60)

    db = SessionLocal()
    try:
        # Step 1: Projects
        project_map = seed_projects(db)

        # Step 2: Labels
        label_map = seed_labels(db)

        # Step 3: Documents
        doc_map = seed_documents(db, project_map, label_map)

        # Step 4: Knowledge Chunks
        chunk_ids = seed_chunks(db, doc_map)

        # Step 5: Knowledge Labels
        seed_knowledge_labels(db, label_map, chunk_ids)

        # Step 6: Knowledge Relations
        seed_relations(db, chunk_ids)

        # Step 7: Memories
        seed_memories(db, chunk_ids)

        # Step 8: Conversations
        seed_conversations(db)

        # Step 9: Reasoning Results
        seed_reasoning_results(db)

        # Step 10: Admin tables
        seed_admin_schemas(db)
        seed_admin_templates(db)
        seed_admin_presets(db)
        seed_admin_rag_profiles(db)
        seed_admin_context_rules(db)
        seed_admin_policy_sets(db)

        # Step 11: Audit Logs
        seed_audit_logs(db)

        log("")
        log("=" * 60)
        log("시드 완료! 최종 건수 확인:")
        log("=" * 60)

        # 최종 건수 출력
        tables = [
            ("projects", Project),
            ("documents", Document),
            ("knowledge_chunks", KnowledgeChunk),
            ("labels", Label),
            ("knowledge_labels", KnowledgeLabel),
            ("knowledge_relations", KnowledgeRelation),
            ("memories", Memory),
            ("conversations", Conversation),
            ("reasoning_results", ReasoningResult),
            ("schemas", AdminSchema),
            ("templates", AdminTemplate),
            ("prompt_presets", AdminPromptPreset),
            ("rag_profiles", AdminRagProfile),
            ("context_rules", AdminContextRule),
            ("policy_sets", AdminPolicySet),
            ("audit_logs", AdminAuditLog),
        ]
        for name, model in tables:
            count = db.query(model).count()
            status = "OK" if count >= 100 or name in ("projects", "rag_profiles", "context_rules", "policy_sets", "knowledge_relations") else "LOW"
            log(f"  {name:25s} {count:>6d}  {'[OK]' if status == 'OK' else '[!]'}")

    except Exception as e:
        db.rollback()
        log(f"ERROR: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
