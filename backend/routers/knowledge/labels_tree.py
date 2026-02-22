"""라벨 트리 관리 핸들러

트리 조회, 노드 이동, Breadcrumb 등의 트리 구조 관련 로직.
labels_handlers.py에서 분리됨 (Phase 17-8).
"""
import logging
from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import Any, Dict, List, Optional

from backend.models.models import Label

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 트리 조회 (Phase 17-8)
# ---------------------------------------------------------------------------


def _build_tree_node(
    label: Label,
    db: Session,
    current_depth: int,
    max_depth: int,
) -> Dict[str, Any]:
    """라벨 노드를 재귀적으로 트리 구조 dict로 변환한다."""
    keyword_count = (
        db.query(Label)
        .filter(
            Label.parent_label_id == label.id,
            Label.label_type == "keyword",
        )
        .count()
    )
    node: Dict[str, Any] = {
        "id": label.id,
        "name": label.name,
        "label_type": label.label_type,
        "description": label.description,
        "color": label.color,
        "depth": current_depth,
        "keyword_count": keyword_count,
        "children": [],
    }
    if current_depth < max_depth:
        children = (
            db.query(Label)
            .filter(Label.parent_label_id == label.id)
            .order_by(Label.name)
            .all()
        )
        node["children"] = [
            _build_tree_node(c, db, current_depth + 1, max_depth)
            for c in children
        ]
    return node


async def handle_get_label_tree(
    max_depth: int, db: Session
) -> List[Dict[str, Any]]:
    """전체 트리 조회 — keyword_group 루트 노드 + 재귀 하위 노드."""
    roots = (
        db.query(Label)
        .filter(
            Label.parent_label_id.is_(None),
            Label.label_type == "keyword_group",
        )
        .order_by(Label.name)
        .all()
    )
    return [_build_tree_node(r, db, 0, max_depth) for r in roots]


async def handle_get_group_tree(
    group_id: int, max_depth: int, db: Session
) -> Dict[str, Any]:
    """특정 그룹의 하위 트리 조회."""
    group = (
        db.query(Label)
        .filter(Label.id == group_id, Label.label_type == "keyword_group")
        .first()
    )
    if not group:
        raise HTTPException(status_code=404, detail="키워드 그룹을 찾을 수 없습니다")
    return _build_tree_node(group, db, 0, max_depth)


# ---------------------------------------------------------------------------
# 노드 이동 + Breadcrumb (Phase 17-8)
# ---------------------------------------------------------------------------


async def handle_move_label(
    label_id: int, new_parent_id: Optional[int], db: Session
) -> Dict[str, Any]:
    """라벨의 부모를 변경(이동)한다. 순환 참조를 검증한다."""
    label = db.query(Label).filter(Label.id == label_id).first()
    if not label:
        raise HTTPException(status_code=404, detail="라벨을 찾을 수 없습니다")

    if new_parent_id is not None:
        if new_parent_id == label_id:
            raise HTTPException(status_code=400, detail="자기 자신을 부모로 설정할 수 없습니다")

        parent = db.query(Label).filter(Label.id == new_parent_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="부모 라벨을 찾을 수 없습니다")

        # 순환 참조 검증: new_parent_id 부터 ancestor를 타고 올라가며 label_id 확인
        visited: set[int] = set()
        current = parent
        while current.parent_label_id is not None:
            if current.parent_label_id == label_id:
                raise HTTPException(
                    status_code=400,
                    detail="순환 참조가 발생합니다. 하위 노드를 부모로 설정할 수 없습니다",
                )
            if current.parent_label_id in visited:
                break  # 기존 데이터의 순환 방지
            visited.add(current.parent_label_id)
            current = db.query(Label).filter(Label.id == current.parent_label_id).first()
            if not current:
                break

    label.parent_label_id = new_parent_id
    db.commit()
    db.refresh(label)
    return {"message": "라벨이 이동되었습니다", "id": label.id, "new_parent_id": new_parent_id}


async def handle_get_breadcrumb(
    label_id: int, db: Session
) -> List[Dict[str, Any]]:
    """루트부터 현재 노드까지의 경로(breadcrumb)를 반환한다."""
    label = db.query(Label).filter(Label.id == label_id).first()
    if not label:
        raise HTTPException(status_code=404, detail="라벨을 찾을 수 없습니다")

    path: List[Dict[str, Any]] = []
    visited: set[int] = set()
    current: Optional[Label] = label

    while current is not None:
        if current.id in visited:
            break
        visited.add(current.id)
        path.append({
            "id": current.id,
            "name": current.name,
            "label_type": current.label_type,
        })
        if current.parent_label_id is not None:
            current = db.query(Label).filter(Label.id == current.parent_label_id).first()
        else:
            break

    path.reverse()
    return path
