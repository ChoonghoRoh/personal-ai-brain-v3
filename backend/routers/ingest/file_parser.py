"""파일 파서 API 라우터"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import List
from pathlib import Path
import tempfile
import os

from backend.services.ingest.file_parser_service import get_file_parser_service

router = APIRouter(prefix="/api/file-parser", tags=["File Parser"])


@router.post("/parse")
async def parse_file(file: UploadFile = File(...)):
    """파일 파싱"""
    service = get_file_parser_service()
    
    # 임시 파일로 저장
    suffix = Path(file.filename).suffix.lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_path = Path(tmp_file.name)
    
    try:
        # 파일 파싱
        text = service.parse_file(tmp_path)
        
        if text is None:
            raise HTTPException(status_code=400, detail="파일을 파싱할 수 없습니다.")
        
        return {
            "filename": file.filename,
            "file_type": suffix,
            "text": text,
            "length": len(text)
        }
    finally:
        # 임시 파일 삭제
        if tmp_path.exists():
            os.unlink(tmp_path)


@router.get("/supported-formats")
async def get_supported_formats():
    """지원하는 파일 형식 목록"""
    service = get_file_parser_service()
    formats = service.get_supported_formats()
    return {
        "supported_formats": formats,
        "count": len(formats)
    }
