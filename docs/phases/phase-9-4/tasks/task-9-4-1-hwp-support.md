# Task 9-4-1: HWP 파일 지원

**상태**: 대기 (Pending)
**우선순위**: 9-4 내 1순위
**예상 작업량**: 2일
**의존성**: 없음

---

## 1. 목표

한글(HWP) 파일 형식을 지원하여 기존 문서 Ingest 파이프라인에 통합

---

## 2. 배경

- 현재 지원 형식: PDF, DOCX, XLSX, PPTX, TXT, MD
- HWP는 한국에서 널리 사용되는 문서 형식
- HWP5 (hwpx) 형식도 고려 필요

---

## 3. 구현 범위

### 3.1 HWP 파서 구현

| 항목 | 설명 |
|------|------|
| 라이브러리 | pyhwpx 또는 olefile 활용 |
| 텍스트 추출 | 본문, 표, 각주 등 |
| 메타데이터 | 제목, 작성자, 생성일 등 |
| 이미지 | 텍스트 우선, 이미지는 선택적 |

### 3.2 통합 대상

- `backend/services/ingest/ingest_service.py` - 파일 유형 분기
- `backend/services/ingest/chunker.py` - 청크 분할
- `backend/routers/search/documents.py` - 업로드 API

---

## 4. 기술 스택

### 4.1 라이브러리 옵션

| 라이브러리 | 장점 | 단점 |
|------------|------|------|
| pyhwpx | HWP5(hwpx) 지원, 순수 Python | HWP(ole) 미지원 |
| olefile | HWP(ole) 구조 접근 | 저수준, 직접 파싱 필요 |
| python-hwp | 간단한 텍스트 추출 | 기능 제한적 |

### 4.2 선택 전략

1. **HWPX (HWP5)**: pyhwpx 사용
2. **HWP (OLE)**: olefile + 직접 파싱 또는 외부 도구

---

## 5. 구현 상세

### 5.1 파일 구조

```
backend/services/ingest/
├── hwp_parser.py          # 신규: HWP 파싱
├── ingest_service.py      # 수정: HWP 지원 추가
└── chunker.py             # 기존 활용
```

### 5.2 HWP Parser 인터페이스

```python
class HWPParser:
    def parse(self, file_path: str) -> ParseResult:
        """HWP 파일 파싱"""
        pass

    def extract_text(self, file_path: str) -> str:
        """텍스트만 추출"""
        pass

    def get_metadata(self, file_path: str) -> dict:
        """메타데이터 추출"""
        pass
```

### 5.3 ParseResult 구조

```python
@dataclass
class ParseResult:
    text: str                    # 전체 텍스트
    metadata: dict               # 메타데이터
    sections: List[str]          # 섹션별 텍스트
    tables: List[List[List[str]]] # 표 데이터
    success: bool                # 파싱 성공 여부
    error: Optional[str]         # 에러 메시지
```

---

## 6. 체크리스트

### 6.1 연구 및 설계
- [ ] HWP 파일 구조 분석
- [ ] 라이브러리 테스트
- [ ] 파서 인터페이스 설계

### 6.2 구현
- [ ] `hwp_parser.py` 생성
- [ ] HWPX 파싱 구현
- [ ] HWP (OLE) 파싱 구현 (가능한 경우)
- [ ] 메타데이터 추출
- [ ] 테이블 처리

### 6.3 통합
- [ ] `ingest_service.py` 수정
- [ ] 파일 확장자 판별 로직
- [ ] 청킹 파이프라인 연결
- [ ] Import API 확장

### 6.4 테스트
- [ ] 다양한 HWP 파일 테스트
- [ ] 손상된 파일 처리
- [ ] 대용량 파일 처리
- [ ] 에러 핸들링 검증

---

## 7. API 변경

### 7.1 기존 API 확장

**`POST /api/documents/import`**

변경 없음 - `.hwp`, `.hwpx` 파일 자동 인식

### 7.2 응답 예시

```json
{
  "document_id": 123,
  "file_name": "example.hwp",
  "file_type": "hwp",
  "chunk_count": 15,
  "status": "processed"
}
```

---

## 8. 에러 처리

| 에러 코드 | 상황 | 처리 |
|-----------|------|------|
| `HWP_UNSUPPORTED_VERSION` | 지원하지 않는 HWP 버전 | 사용자에게 안내 |
| `HWP_PARSE_ERROR` | 파싱 실패 | 로그 기록, 사용자 알림 |
| `HWP_ENCRYPTED` | 암호화된 파일 | 지원 불가 안내 |

---

## 9. 의존성

### 9.1 requirements.txt 추가

```
pyhwpx>=0.1.0  # HWPX 파싱
olefile>=0.46  # OLE 구조 접근
```

### 9.2 requirements-docker.txt 추가

동일

---

## 10. 테스트 케이스

| 케이스 | 입력 | 기대 결과 |
|--------|------|-----------|
| 정상 HWPX | valid.hwpx | 텍스트 추출 성공 |
| 정상 HWP | valid.hwp | 텍스트 추출 성공 |
| 표 포함 | with_table.hwp | 표 텍스트 추출 |
| 이미지 포함 | with_image.hwp | 텍스트만 추출 |
| 손상된 파일 | corrupted.hwp | 에러 반환 |
| 암호화 파일 | encrypted.hwp | 지원 불가 안내 |

---

## 11. 참고 자료

- pyhwpx: https://github.com/nicotine-evo/pyhwpx
- olefile: https://github.com/decalage2/olefile
- HWP 파일 구조: https://www.hancom.com/etc/hwpDownload.do
- hwp5 spec: https://github.com/mete0r/pyhwp

---

## 12. 작업 로그

| 날짜 | 작업 내용 | 상태 |
|------|----------|------|
| - | - | - |
