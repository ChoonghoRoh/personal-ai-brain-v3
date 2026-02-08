#!/usr/bin/env python3
"""
Keyword Group Management 기능 테스트 스크립트
Phase 7.7 - 1차 코드 테스트
"""
import sys
import requests
import json
from pathlib import Path
from typing import Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.models.database import SessionLocal
from backend.models.models import Label
from sqlalchemy import text

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/labels"

# 테스트 결과 저장
test_results = {
    "backend_api": [],
    "db_schema": [],
    "keyword_suggestion": [],
    "frontend_ui": [],
    "errors": []
}


def log_test(category: str, test_name: str, passed: bool, details: str = ""):
    """테스트 결과 로깅"""
    result = {
        "test": test_name,
        "passed": passed,
        "details": details
    }
    test_results[category].append(result)
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} [{category}] {test_name}")
    if details:
        print(f"   {details}")


def test_backend_api():
    """Backend API 엔드포인트 테스트"""
    print("\n" + "="*60)
    print("1차 코드 테스트: Backend API")
    print("="*60)
    
    # 1. 키워드 그룹 목록 조회
    try:
        response = requests.get(f"{API_BASE}/groups")
        passed = response.status_code == 200
        log_test("backend_api", "GET /api/labels/groups", passed, 
                f"Status: {response.status_code}, Count: {len(response.json())}")
    except Exception as e:
        log_test("backend_api", "GET /api/labels/groups", False, str(e))
    
    # 2. 키워드 그룹 생성
    import time
    test_group_name = f"테스트 그룹_{int(time.time())}"  # 고유한 이름 생성
    test_group_id = None
    try:
        payload = {
            "name": test_group_name,
            "description": "테스트용 키워드 그룹입니다",
            "color": "#4F46E5"
        }
        response = requests.post(f"{API_BASE}/groups", json=payload)
        passed = response.status_code == 200
        if passed:
            test_group_id = response.json()["id"]
            log_test("backend_api", "POST /api/labels/groups", passed,
                    f"Status: {response.status_code}, ID: {test_group_id}, Name: {test_group_name}")
        else:
            error_detail = response.json().get("detail", response.text) if response.content else response.text
            log_test("backend_api", "POST /api/labels/groups", False,
                    f"Status: {response.status_code}, Error: {error_detail}")
    except Exception as e:
        log_test("backend_api", "POST /api/labels/groups", False, str(e))
    
    # 3. 키워드 그룹 조회
    if test_group_id:
        try:
            response = requests.get(f"{API_BASE}/groups/{test_group_id}")
            passed = response.status_code == 200
            log_test("backend_api", "GET /api/labels/groups/{group_id}", passed,
                    f"Status: {response.status_code}")
        except Exception as e:
            log_test("backend_api", "GET /api/labels/groups/{group_id}", False, str(e))
    
    # 4. 키워드 그룹 수정
    if test_group_id:
        try:
            payload = {
                "name": f"{test_group_name} (수정됨)",
                "description": "수정된 설명"
            }
            response = requests.patch(f"{API_BASE}/groups/{test_group_id}", json=payload)
            passed = response.status_code == 200
            log_test("backend_api", "PATCH /api/labels/groups/{group_id}", passed,
                    f"Status: {response.status_code}")
        except Exception as e:
            log_test("backend_api", "PATCH /api/labels/groups/{group_id}", False, str(e))
    
    # 5. 키워드 추천 API
    try:
        payload = {"description": "인공지능 시스템 구축을 위한 인프라 및 도구"}
        response = requests.post(f"{API_BASE}/groups/suggest-keywords", json=payload)
        passed = response.status_code == 200
        if passed:
            data = response.json()
            keyword_count = len(data.get("keywords", []))
            llm_count = len(data.get("llm_keywords", []))
            similar_count = len(data.get("similar_keywords", []))
            log_test("backend_api", "POST /api/labels/groups/suggest-keywords", passed,
                    f"Status: {response.status_code}, Total: {keyword_count}, LLM: {llm_count}, Similar: {similar_count}")
        else:
            log_test("backend_api", "POST /api/labels/groups/suggest-keywords", False,
                    f"Status: {response.status_code}, Response: {response.text}")
    except Exception as e:
        log_test("backend_api", "POST /api/labels/groups/suggest-keywords", False, str(e))
    
    # 6. 그룹에 키워드 추가
    if test_group_id:
        try:
            # 먼저 기존 키워드 조회
            keywords_response = requests.get(f"{API_BASE}?label_type=keyword")
            if keywords_response.status_code == 200:
                keywords = keywords_response.json()
                if keywords:
                    keyword_id = keywords[0]["id"]
                    payload = {"keyword_ids": [keyword_id]}
                    response = requests.post(f"{API_BASE}/groups/{test_group_id}/keywords", json=payload)
                    passed = response.status_code == 200
                    log_test("backend_api", "POST /api/labels/groups/{group_id}/keywords", passed,
                            f"Status: {response.status_code}")
                else:
                    log_test("backend_api", "POST /api/labels/groups/{group_id}/keywords", False,
                            "키워드가 없어서 테스트 불가")
            else:
                log_test("backend_api", "POST /api/labels/groups/{group_id}/keywords", False,
                        "키워드 조회 실패")
        except Exception as e:
            log_test("backend_api", "POST /api/labels/groups/{group_id}/keywords", False, str(e))
    
    # 7. 그룹 내 키워드 목록 조회
    if test_group_id:
        try:
            response = requests.get(f"{API_BASE}/groups/{test_group_id}/keywords")
            passed = response.status_code == 200
            keyword_count = len(response.json()) if passed else 0
            log_test("backend_api", "GET /api/labels/groups/{group_id}/keywords", passed,
                    f"Status: {response.status_code}, Keywords: {keyword_count}")
        except Exception as e:
            log_test("backend_api", "GET /api/labels/groups/{group_id}/keywords", False, str(e))
    
    # 8. 키워드 그룹 삭제
    if test_group_id:
        try:
            response = requests.delete(f"{API_BASE}/groups/{test_group_id}")
            passed = response.status_code == 200
            log_test("backend_api", "DELETE /api/labels/groups/{group_id}", passed,
                    f"Status: {response.status_code}")
        except Exception as e:
            log_test("backend_api", "DELETE /api/labels/groups/{group_id}", False, str(e))
    
    return test_group_id


def test_db_schema():
    """DB 스키마 확인"""
    print("\n" + "="*60)
    print("1차 코드 테스트: DB 스키마")
    print("="*60)
    
    db = SessionLocal()
    try:
        # 1. labels 테이블 존재 확인
        try:
            result = db.execute(text("SELECT COUNT(*) FROM labels"))
            count = result.scalar()
            log_test("db_schema", "labels 테이블 존재", True, f"레코드 수: {count}")
        except Exception as e:
            log_test("db_schema", "labels 테이블 존재", False, str(e))
        
        # 2. parent_label_id 컬럼 확인
        try:
            result = db.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'labels' AND column_name = 'parent_label_id'
            """))
            row = result.fetchone()
            passed = row is not None
            log_test("db_schema", "parent_label_id 컬럼", passed,
                    f"Type: {row[1]}" if row else "컬럼 없음")
        except Exception as e:
            log_test("db_schema", "parent_label_id 컬럼", False, str(e))
        
        # 3. color 컬럼 확인
        try:
            result = db.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'labels' AND column_name = 'color'
            """))
            row = result.fetchone()
            passed = row is not None
            log_test("db_schema", "color 컬럼", passed,
                    f"Type: {row[1]}" if row else "컬럼 없음")
        except Exception as e:
            log_test("db_schema", "color 컬럼", False, str(e))
        
        # 4. updated_at 컬럼 확인
        try:
            result = db.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'labels' AND column_name = 'updated_at'
            """))
            row = result.fetchone()
            passed = row is not None
            log_test("db_schema", "updated_at 컬럼", passed,
                    f"Type: {row[1]}" if row else "컬럼 없음")
        except Exception as e:
            log_test("db_schema", "updated_at 컬럼", False, str(e))
        
        # 5. keyword_group 타입 레이블 확인
        try:
            groups = db.query(Label).filter(Label.label_type == "keyword_group").all()
            log_test("db_schema", "keyword_group 타입 데이터", True,
                    f"그룹 수: {len(groups)}")
        except Exception as e:
            log_test("db_schema", "keyword_group 타입 데이터", False, str(e))
        
        # 6. parent_label_id 관계 확인
        try:
            keywords_with_parent = db.query(Label).filter(
                Label.label_type == "keyword",
                Label.parent_label_id.isnot(None)
            ).all()
            log_test("db_schema", "parent_label_id 관계", True,
                    f"그룹에 속한 키워드 수: {len(keywords_with_parent)}")
        except Exception as e:
            log_test("db_schema", "parent_label_id 관계", False, str(e))
            
    finally:
        db.close()


def test_keyword_suggestion():
    """키워드 추천 기능 테스트"""
    print("\n" + "="*60)
    print("1차 코드 테스트: 키워드 추천 (LLM 기반)")
    print("="*60)
    
    test_descriptions = [
        "인공지능 시스템 구축을 위한 인프라 및 도구",
        "데이터베이스와 벡터 검색 시스템",
        "웹 개발 프레임워크와 API 설계"
    ]
    
    for desc in test_descriptions:
        try:
            payload = {"description": desc}
            response = requests.post(f"{API_BASE}/groups/suggest-keywords", json=payload)
            passed = response.status_code == 200
            if passed:
                data = response.json()
                keywords = data.get("keywords", [])
                llm_keywords = data.get("llm_keywords", [])
                similar_keywords = data.get("similar_keywords", [])
                log_test("keyword_suggestion", f"추천 테스트: {desc[:30]}...", passed,
                        f"Total: {len(keywords)}, LLM: {len(llm_keywords)}, Similar: {len(similar_keywords)}")
                if llm_keywords:
                    print(f"   LLM 추천: {', '.join(llm_keywords[:5])}")
            else:
                log_test("keyword_suggestion", f"추천 테스트: {desc[:30]}...", False,
                        f"Status: {response.status_code}")
        except Exception as e:
            log_test("keyword_suggestion", f"추천 테스트: {desc[:30]}...", False, str(e))


def test_frontend_ui():
    """Frontend UI 구조 확인"""
    print("\n" + "="*60)
    print("1차 코드 테스트: Frontend UI 구조")
    print("="*60)
    
    ui_file = PROJECT_ROOT / "web" / "src" / "pages" / "knowledge-admin.html"
    
    if not ui_file.exists():
        log_test("frontend_ui", "knowledge-admin.html 파일 존재", False, "파일을 찾을 수 없습니다")
        return
    
    content = ui_file.read_text(encoding="utf-8")
    
    # 1. 키워드 그룹 탭 확인
    checks = [
        ("키워드 그룹 탭", 'id="tab-content-groups"'),
        ("그룹 목록 영역", 'id="groups-list"'),
        ("키워드 목록 영역", 'id="keywords-list"'),
        ("검색 입력창", 'id="group-search-input"'),
        ("매칭 모드 토글", 'id="matching-mode-toggle"'),
        ("선택 요약 바", 'id="matching-summary-bar"'),
        ("그룹 생성 모달", 'id="create-group-modal"'),
        ("키워드 추천 버튼", "설명 기반 키워드 추천"),
        ("추천 키워드 컨테이너", 'id="suggested-keywords-container"'),
    ]
    
    for check_name, pattern in checks:
        passed = pattern in content
        log_test("frontend_ui", check_name, passed,
                "찾음" if passed else "찾을 수 없음")


def generate_test_report():
    """테스트 결과 리포트 생성"""
    print("\n" + "="*60)
    print("테스트 결과 요약")
    print("="*60)
    
    total_tests = 0
    passed_tests = 0
    
    for category, results in test_results.items():
        if category == "errors":
            continue
        category_total = len(results)
        category_passed = sum(1 for r in results if r["passed"])
        total_tests += category_total
        passed_tests += category_passed
        
        print(f"\n[{category}]")
        print(f"  총 {category_total}개 테스트 중 {category_passed}개 통과 ({category_passed/category_total*100:.1f}%)")
    
    print(f"\n전체: {passed_tests}/{total_tests} 테스트 통과 ({passed_tests/total_tests*100:.1f}%)")
    
    # 리포트 파일 저장
    report_file = PROJECT_ROOT / "docs" / "phase7-7-keyword-group-test-results.md"
    report_content = f"""# Phase 7.7 Keyword Group Management 테스트 결과

## 테스트 일시
{Path(__file__).stat().st_mtime}

## 테스트 결과 요약

- 전체: {passed_tests}/{total_tests} 테스트 통과 ({passed_tests/total_tests*100:.1f}%)

## 상세 결과

### 1. Backend API 테스트

"""
    
    for result in test_results["backend_api"]:
        status = "✅ PASS" if result["passed"] else "❌ FAIL"
        report_content += f"- {status} {result['test']}\n"
        if result["details"]:
            report_content += f"  - {result['details']}\n"
    
    report_content += "\n### 2. DB 스키마 테스트\n\n"
    for result in test_results["db_schema"]:
        status = "✅ PASS" if result["passed"] else "❌ FAIL"
        report_content += f"- {status} {result['test']}\n"
        if result["details"]:
            report_content += f"  - {result['details']}\n"
    
    report_content += "\n### 3. 키워드 추천 테스트\n\n"
    for result in test_results["keyword_suggestion"]:
        status = "✅ PASS" if result["passed"] else "❌ FAIL"
        report_content += f"- {status} {result['test']}\n"
        if result["details"]:
            report_content += f"  - {result['details']}\n"
    
    report_content += "\n### 4. Frontend UI 구조 테스트\n\n"
    for result in test_results["frontend_ui"]:
        status = "✅ PASS" if result["passed"] else "❌ FAIL"
        report_content += f"- {status} {result['test']}\n"
        if result["details"]:
            report_content += f"  - {result['details']}\n"
    
    report_file.write_text(report_content, encoding="utf-8")
    print(f"\n테스트 리포트 저장: {report_file}")


def main():
    """메인 테스트 실행"""
    print("="*60)
    print("Phase 7.7 Keyword Group Management 기능 테스트")
    print("="*60)
    
    # 서버 연결 확인
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code != 200:
            print(f"⚠️  서버가 실행 중이지 않습니다. {BASE_URL}에 접근할 수 없습니다.")
            return
    except Exception as e:
        print(f"⚠️  서버 연결 실패: {e}")
        print("서버를 먼저 실행해주세요: python -m uvicorn backend.main:app --reload")
        return
    
    # 테스트 실행
    test_group_id = test_backend_api()
    test_db_schema()
    test_keyword_suggestion()
    test_frontend_ui()
    
    # 리포트 생성
    generate_test_report()


if __name__ == "__main__":
    main()

