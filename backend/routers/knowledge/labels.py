"""라벨 API 라우터"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import ProgrammingError
from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, field_serializer

from backend.models.database import get_db
from backend.models.models import Label, KnowledgeLabel, KnowledgeChunk

router = APIRouter(prefix="/api/labels", tags=["labels"])


class LabelCreate(BaseModel):
    name: str
    label_type: str
    description: str = None
    parent_label_id: int = None  # Phase 7.7
    color: str = None  # Phase 7.7


class LabelResponse(BaseModel):
    id: int
    name: str
    label_type: str
    description: Optional[str] = None
    parent_label_id: Optional[int] = None  # Phase 7.7
    color: Optional[str] = None  # Phase 7.7
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, dt: Optional[datetime], _info) -> Optional[str]:
        """datetime을 ISO 형식 문자열로 변환"""
        if dt is None:
            return None
        return dt.isoformat()

    class Config:
        from_attributes = True


class KeywordGroupCreate(BaseModel):  # Phase 7.7
    name: str
    description: Optional[str] = None
    color: Optional[str] = None


class KeywordGroupUpdate(BaseModel):  # Phase 7.7
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None


class GroupKeywordsAdd(BaseModel):  # Phase 7.7
    keyword_ids: List[int] = None
    keyword_names: List[str] = None


class SuggestKeywordsRequest(BaseModel):  # Phase 7.7 — suggest-keywords 바디 (request 이름 충돌 방지)
    description: str = ""
    model: Optional[str] = None  # 키워드 추천용 Ollama 모델. 없으면 OLLAMA_MODEL 사용


@router.post("", response_model=LabelResponse)
async def create_label(label: LabelCreate, db: Session = Depends(get_db)):
    """라벨 생성"""
    # 중복 체크: (name, label_type) 복합 unique
    existing = db.query(Label).filter(
        Label.name == label.name,
        Label.label_type == label.label_type
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"같은 이름과 타입의 라벨이 이미 존재합니다 (name: {label.name}, type: {label.label_type})")
    
    db_label = Label(**label.dict())
    db.add(db_label)
    db.commit()
    db.refresh(db_label)
    return db_label


@router.get("")
async def list_labels(
    label_type: Optional[str] = None,
    q: Optional[str] = None,
    limit: Optional[int] = None,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """라벨 목록 조회. label_type/q 로 필터, limit 지정 시 페이징 응답 { items, total }, 미지정 시 전체 목록 (하위 호환)."""
    try:
        query = db.query(Label)
        if label_type:
            query = query.filter(Label.label_type == label_type)
        if q and q.strip():
            query = query.filter(Label.name.ilike(f"%{q.strip()}%"))
        if limit is not None:
            total = query.count()
            items = query.order_by(Label.id).offset(offset).limit(limit).all()
            return {"items": items, "total": total}
        return query.order_by(Label.id).all()
    except ProgrammingError as e:
        if "does not exist" in str(e.orig) if hasattr(e, "orig") else "does not exist" in str(e):
            return [] if limit is None else {"items": [], "total": 0}
        raise


# ========== Phase 7.7: 키워드 그룹 관리 API (/{label_id} 라우트보다 먼저 정의) ==========

@router.get("/groups", response_model=List[LabelResponse])
async def list_keyword_groups(
    q: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """키워드 그룹 목록 조회"""
    query = db.query(Label).filter(Label.label_type == "keyword_group")
    
    if q:
        query = query.filter(Label.name.ilike(f"%{q}%"))
    
    return query.offset(offset).limit(limit).all()


@router.get("/groups/{group_id}", response_model=LabelResponse)
async def get_keyword_group(group_id: int, db: Session = Depends(get_db)):
    """키워드 그룹 조회"""
    group = db.query(Label).filter(
        Label.id == group_id,
        Label.label_type == "keyword_group"
    ).first()
    if not group:
        raise HTTPException(status_code=404, detail="키워드 그룹을 찾을 수 없습니다")
    return group


@router.post("/groups", response_model=LabelResponse)
async def create_keyword_group(group: KeywordGroupCreate, db: Session = Depends(get_db)):
    """키워드 그룹 생성"""
    # 중복 체크
    existing = db.query(Label).filter(
        Label.name == group.name,
        Label.label_type == "keyword_group"
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="이미 존재하는 그룹 이름입니다")
    
    db_group = Label(
        name=group.name,
        label_type="keyword_group",
        description=group.description if group.description else None,
        color=group.color if group.color else None
    )
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group


@router.post("/groups/suggest-keywords")
async def suggest_keywords_from_description(
    body: SuggestKeywordsRequest,
    db: Session = Depends(get_db)
):
    """그룹 설명 기반 LLM 키워드 추천 + 기존 키워드 유사도 매칭 (Phase 7.7)"""
    from scripts.backend.extract_keywords_and_labels import extract_keywords_with_gpt4all, extract_keywords_with_regex

    description = (body.description or "").strip()
    if not description:
        raise HTTPException(status_code=400, detail="설명을 입력해주세요")
    
    # 설명 길이 제한 (컨텍스트 윈도우 고려)
    # 프롬프트 템플릿이 약 200자, 설명은 최대 1000자로 제한
    MAX_DESCRIPTION_LENGTH = 1000
    if len(description) > MAX_DESCRIPTION_LENGTH:
        description = description[:MAX_DESCRIPTION_LENGTH] + "..."
    
    llm_keywords = []
    extraction_method = "regex"  # "ollama" | "regex" — 어떤 방식으로 새 키워드가 추출되었는지

    # 1. 로컬 LLM (Ollama)로 새 키워드 추출 시도 → 실패 시 정규식 폴백
    prompt = f"""다음 그룹 설명을 분석하여 관련 키워드를 추출해주세요.

그룹 설명:
{description}

요구사항:
1. 설명과 관련된 의미 있는 키워드만 추출
2. 불용어(것, 수, 등, 때 등)는 제외
3. 전문 용어나 개념을 우선
4. 키워드는 한글로, 2글자 이상
5. 상위 10개만 추출

키워드를 쉼표로 구분하여 나열해주세요. 설명 없이 키워드만 출력하세요.
예시: 인프라, 벡터, 데이터베이스, API, 시스템"""

    try:
        llm_keywords = extract_keywords_with_gpt4all(prompt, top_n=10, model=body.model)
        extraction_method = "ollama"
    except Exception as e:
        print(f"⚠️ Ollama 오류: {e}, 정규식 기반으로 대체...")
        llm_keywords = extract_keywords_with_regex(description, top_n=10)
        extraction_method = "regex"
    
    # 2. 기존 키워드 중 유사한 키워드 찾기 (유사도 계산 포함). labels 테이블 없으면 빈 목록
    try:
        existing_keywords = db.query(Label).filter(
            Label.label_type == "keyword"
        ).all()
    except ProgrammingError:
        existing_keywords = []

    similar_keywords = []
    similar_keywords_with_score = []
    description_lower = description.lower()
    
    def calculate_similarity(keyword_name: str, description: str) -> float:
        """간단한 유사도 계산 (0.0 ~ 1.0)"""
        keyword_lower = keyword_name.lower()
        desc_lower = description.lower()
        
        # 완전 일치
        if keyword_lower == desc_lower:
            return 1.0
        
        # 설명에 키워드가 완전히 포함
        if keyword_lower in desc_lower:
            return 0.9
        
        # 키워드가 설명에 완전히 포함
        if desc_lower in keyword_lower:
            return 0.8
        
        # 단어 단위 일치
        keyword_words = set(word for word in keyword_lower.split() if len(word) >= 2)
        desc_words = set(word for word in desc_lower.split() if len(word) >= 2)
        if keyword_words and desc_words:
            common_words = keyword_words.intersection(desc_words)
            if common_words:
                return min(0.7, len(common_words) / max(len(keyword_words), len(desc_words)))
        
        # 부분 일치 (2글자 이상)
        if len(keyword_lower) >= 2 and keyword_lower in desc_lower:
            return 0.6
        
        # 문자 단위 유사도 (간단한 Jaccard 유사도)
        keyword_chars = set(keyword_lower)
        desc_chars = set(desc_lower)
        if keyword_chars and desc_chars:
            intersection = keyword_chars.intersection(desc_chars)
            union = keyword_chars.union(desc_chars)
            if union:
                jaccard = len(intersection) / len(union)
                if jaccard > 0.3:  # 최소 임계값
                    return jaccard * 0.5
        
        return 0.0
    
    for keyword in existing_keywords:
        keyword_name_lower = keyword.name.lower()
        similarity = calculate_similarity(keyword.name, description)
        
        # 유사도가 0.3 이상인 경우만 포함
        if similarity >= 0.3:
            if keyword.name not in similar_keywords:
                similar_keywords.append(keyword.name)
                similar_keywords_with_score.append({
                    "keyword": keyword.name,
                    "score": similarity
                })
    
    # 유사도 점수로 정렬 (높은 순)
    similar_keywords_with_score.sort(key=lambda x: x["score"], reverse=True)
    similar_keywords = [item["keyword"] for item in similar_keywords_with_score]
    
    # 중복 제거 및 정렬
    all_keywords = list(dict.fromkeys(llm_keywords + similar_keywords))  # 순서 유지하면서 중복 제거
    
    return {
        "keywords": all_keywords[:15],  # 최대 15개
        "count": len(all_keywords),
        "llm_keywords": llm_keywords,
        "similar_keywords": similar_keywords[:10],  # 유사 키워드 최대 10개
        "similar_keywords_with_score": similar_keywords_with_score[:10],  # 유사도 점수 포함
        "extraction_method": extraction_method,  # "ollama" | "regex" — 새 키워드 추출에 사용된 방식
    }


@router.patch("/groups/{group_id}", response_model=LabelResponse)
async def update_keyword_group(
    group_id: int,
    group_update: KeywordGroupUpdate,
    db: Session = Depends(get_db)
):
    """키워드 그룹 수정"""
    group = db.query(Label).filter(
        Label.id == group_id,
        Label.label_type == "keyword_group"
    ).first()
    if not group:
        raise HTTPException(status_code=404, detail="키워드 그룹을 찾을 수 없습니다")
    
    if group_update.name is not None:
        group.name = group_update.name
    if group_update.description is not None:
        group.description = group_update.description
    if group_update.color is not None:
        group.color = group_update.color
    
    db.commit()
    db.refresh(group)
    return group


@router.get("/groups/{group_id}/impact")
async def get_group_impact(group_id: int, db: Session = Depends(get_db)):
    """키워드 그룹 삭제 전 영향도 조회"""
    group = db.query(Label).filter(
        Label.id == group_id,
        Label.label_type == "keyword_group"
    ).first()
    if not group:
        raise HTTPException(status_code=404, detail="키워드 그룹을 찾을 수 없습니다")
    
    # 이 그룹에 속한 키워드 수
    keywords_count = db.query(Label).filter(Label.parent_label_id == group_id).count()
    
    # 이 그룹의 키워드들이 붙은 청크 수 (간접 영향)
    group_keywords = db.query(Label).filter(Label.parent_label_id == group_id).all()
    keyword_ids = [kw.id for kw in group_keywords]
    chunks_count = 0
    if keyword_ids:
        chunks_count = db.query(KnowledgeLabel).filter(KnowledgeLabel.label_id.in_(keyword_ids)).distinct(KnowledgeLabel.chunk_id).count()
    
    return {
        "group_id": group_id,
        "group_name": group.name,
        "keywords_count": keywords_count,
        "chunks_count": chunks_count
    }


@router.delete("/groups/{group_id}")
async def delete_keyword_group(group_id: int, db: Session = Depends(get_db)):
    """키워드 그룹 삭제"""
    group = db.query(Label).filter(
        Label.id == group_id,
        Label.label_type == "keyword_group"
    ).first()
    if not group:
        raise HTTPException(status_code=404, detail="키워드 그룹을 찾을 수 없습니다")
    
    # 이 그룹에 속한 키워드의 parent_label_id를 NULL로 변경
    db.query(Label).filter(Label.parent_label_id == group_id).update(
        {"parent_label_id": None}
    )
    
    db.delete(group)
    db.commit()
    return {"message": "키워드 그룹이 삭제되었습니다"}


@router.get("/groups/{group_id}/keywords", response_model=List[LabelResponse])
async def list_group_keywords(group_id: int, db: Session = Depends(get_db)):
    """그룹 내 키워드 목록 조회"""
    group = db.query(Label).filter(
        Label.id == group_id,
        Label.label_type == "keyword_group"
    ).first()
    if not group:
        raise HTTPException(status_code=404, detail="키워드 그룹을 찾을 수 없습니다")
    
    keywords = db.query(Label).filter(
        Label.label_type == "keyword",
        Label.parent_label_id == group_id
    ).all()
    
    return keywords


@router.post("/groups/{group_id}/keywords")
async def add_keywords_to_group(
    group_id: int,
    request: GroupKeywordsAdd,
    db: Session = Depends(get_db)
):
    """그룹에 키워드 추가"""
    group = db.query(Label).filter(
        Label.id == group_id,
        Label.label_type == "keyword_group"
    ).first()
    if not group:
        raise HTTPException(status_code=404, detail="키워드 그룹을 찾을 수 없습니다")
    
    added_count = 0
    errors = []
    skipped_count = 0
    
    # Mode 1: 기존 키워드 ID를 그룹에 연결
    if request.keyword_ids:
        keywords = db.query(Label).filter(
            Label.id.in_(request.keyword_ids),
            Label.label_type == "keyword"
        ).all()
        for keyword in keywords:
            try:
                if keyword.parent_label_id != group_id:
                    keyword.parent_label_id = group_id
                    added_count += 1
                else:
                    skipped_count += 1  # 이미 해당 그룹에 속함
            except Exception as e:
                errors.append(f"키워드 ID {keyword.id} 처리 중 오류: {str(e)}")
    
    # Mode 2: 새 키워드 생성 + 그룹 연결
    if request.keyword_names:
        for keyword_name in request.keyword_names:
            if not keyword_name or not keyword_name.strip():
                continue
                
            keyword_name = keyword_name.strip()
            
            try:
                # 이미 존재하는 키워드인지 확인 (label_type="keyword"만)
                existing = db.query(Label).filter(
                    Label.name == keyword_name,
                    Label.label_type == "keyword"
                ).first()
                
                if existing:
                    # 존재하면 그룹에 연결
                    if existing.parent_label_id != group_id:
                        existing.parent_label_id = group_id
                        added_count += 1
                    else:
                        skipped_count += 1  # 이미 해당 그룹에 속함
                else:
                    # 다른 label_type으로 같은 이름이 있는지 확인 (경고용)
                    name_conflict = db.query(Label).filter(
                        Label.name == keyword_name
                    ).first()
                    
                    if name_conflict:
                        # 이름 충돌: 다른 타입의 라벨이 존재하지만, label_type이 다르므로 생성 가능
                        # 경고만 기록
                        pass
                    
                    # 새로 생성 (label_type이 다르면 같은 이름 허용)
                    new_keyword = Label(
                        name=keyword_name,
                        label_type="keyword",
                        parent_label_id=group_id
                    )
                    db.add(new_keyword)
                    added_count += 1
            except Exception as e:
                error_msg = f"'{keyword_name}' 처리 중 오류: {str(e)}"
                errors.append(error_msg)
                print(f"⚠️ {error_msg}")
                continue
    
    try:
        db.commit()
        result = {
            "message": f"{added_count}개의 키워드가 그룹에 추가되었습니다",
            "added_count": added_count,
            "skipped_count": skipped_count
        }
        if errors:
            result["errors"] = errors
            result["error_count"] = len(errors)
        return result
    except Exception as e:
        db.rollback()
        error_detail = str(e)
        print(f"❌ 키워드 추가 중 DB 오류: {error_detail}")
        raise HTTPException(status_code=500, detail=f"키워드 추가 중 오류: {error_detail}")


@router.delete("/groups/{group_id}/keywords/{keyword_id}")
async def remove_keyword_from_group(
    group_id: int,
    keyword_id: int,
    db: Session = Depends(get_db)
):
    """그룹에서 키워드 제거"""
    keyword = db.query(Label).filter(
        Label.id == keyword_id,
        Label.label_type == "keyword",
        Label.parent_label_id == group_id
    ).first()
    if not keyword:
        raise HTTPException(status_code=404, detail="키워드를 찾을 수 없거나 그룹에 속하지 않습니다")
    
    keyword.parent_label_id = None
    db.commit()
    return {"message": "키워드가 그룹에서 제거되었습니다"}


@router.get("/{label_id}", response_model=LabelResponse)
async def get_label(label_id: int, db: Session = Depends(get_db)):
    """라벨 조회"""
    label = db.query(Label).filter(Label.id == label_id).first()
    if not label:
        raise HTTPException(status_code=404, detail="라벨을 찾을 수 없습니다")
    return label


@router.get("/{label_id}/impact")
async def get_label_impact(label_id: int, db: Session = Depends(get_db)):
    """라벨 삭제 전 영향도 조회"""
    label = db.query(Label).filter(Label.id == label_id).first()
    if not label:
        raise HTTPException(status_code=404, detail="라벨을 찾을 수 없습니다")
    
    # 해당 라벨이 붙은 청크 수
    chunks_count = db.query(KnowledgeLabel).filter(KnowledgeLabel.label_id == label_id).count()
    
    # 해당 라벨이 속한 그룹 정보 (parent_label_id가 있는 경우)
    parent_group = None
    if label.parent_label_id:
        parent_group = db.query(Label).filter(Label.id == label.parent_label_id).first()
    
    # 이 라벨을 부모로 하는 자식 라벨 수 (키워드 그룹인 경우)
    child_labels_count = 0
    if label.label_type == "keyword_group":
        child_labels_count = db.query(Label).filter(Label.parent_label_id == label_id).count()
    
    return {
        "label_id": label_id,
        "label_name": label.name,
        "label_type": label.label_type,
        "chunks_count": chunks_count,
        "child_labels_count": child_labels_count,
        "parent_group": {
            "id": parent_group.id,
            "name": parent_group.name
        } if parent_group else None
    }


@router.delete("/{label_id}")
async def delete_label(label_id: int, db: Session = Depends(get_db)):
    """라벨 삭제"""
    label = db.query(Label).filter(Label.id == label_id).first()
    if not label:
        raise HTTPException(status_code=404, detail="라벨을 찾을 수 없습니다")
    db.delete(label)
    db.commit()
    return {"message": "라벨이 삭제되었습니다"}


@router.post("/chunks/{chunk_id}/labels/{label_id}")
async def add_label_to_chunk(chunk_id: int, label_id: int, confidence: float = 1.0, db: Session = Depends(get_db)):
    """청크에 라벨 추가"""
    chunk = db.query(KnowledgeChunk).filter(KnowledgeChunk.id == chunk_id).first()
    if not chunk:
        raise HTTPException(status_code=404, detail="청크를 찾을 수 없습니다")
    
    label = db.query(Label).filter(Label.id == label_id).first()
    if not label:
        raise HTTPException(status_code=404, detail="라벨을 찾을 수 없습니다")
    
    # 중복 체크
    existing = db.query(KnowledgeLabel).filter(
        KnowledgeLabel.chunk_id == chunk_id,
        KnowledgeLabel.label_id == label_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="이미 라벨이 추가되어 있습니다")
    
    knowledge_label = KnowledgeLabel(chunk_id=chunk_id, label_id=label_id, confidence=confidence)
    db.add(knowledge_label)
    db.commit()
    return {"message": "라벨이 추가되었습니다"}


@router.delete("/chunks/{chunk_id}/labels/{label_id}")
async def remove_label_from_chunk(chunk_id: int, label_id: int, db: Session = Depends(get_db)):
    """청크에서 라벨 제거"""
    knowledge_label = db.query(KnowledgeLabel).filter(
        KnowledgeLabel.chunk_id == chunk_id,
        KnowledgeLabel.label_id == label_id
    ).first()
    if not knowledge_label:
        raise HTTPException(status_code=404, detail="라벨을 찾을 수 없습니다")
    
    db.delete(knowledge_label)
    db.commit()
    return {"message": "라벨이 제거되었습니다"}


@router.get("/chunks/{chunk_id}/labels")
async def get_chunk_labels(chunk_id: int, db: Session = Depends(get_db)):
    """청크의 라벨 목록 조회"""
    chunk = db.query(KnowledgeChunk).filter(KnowledgeChunk.id == chunk_id).first()
    if not chunk:
        raise HTTPException(status_code=404, detail="청크를 찾을 수 없습니다")
    
    labels = db.query(Label).join(KnowledgeLabel).filter(
        KnowledgeLabel.chunk_id == chunk_id
    ).all()
    
    return [{"id": label.id, "name": label.name, "label_type": label.label_type} for label in labels]

