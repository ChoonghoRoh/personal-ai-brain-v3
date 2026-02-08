#!/usr/bin/env python3
"""
Phase 7 통합 테스트 스크립트
Reasoning 모드 및 Knowledge Admin 기능 테스트
"""

import sys
import requests
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

# 테스트 결과 저장
test_results = {
    "passed": [],
    "failed": [],
    "warnings": []
}


def log_test(name, passed, message=""):
    """테스트 결과 로깅"""
    if passed:
        test_results["passed"].append(name)
        print(f"✅ {name}: PASSED")
        if message:
            print(f"   {message}")
    else:
        test_results["failed"].append(name)
        print(f"❌ {name}: FAILED")
        if message:
            print(f"   {message}")


def log_warning(name, message):
    """경고 로깅"""
    test_results["warnings"].append(f"{name}: {message}")
    print(f"⚠️  {name}: {message}")


def test_server_health():
    """서버 상태 확인"""
    print("\n🔍 1. 서버 상태 확인")
    print("=" * 60)
    
    try:
        response = requests.get(f"{API_BASE}/system/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            log_test("서버 상태", True, f"서버 정상 작동 중")
            return True
        else:
            log_test("서버 상태", False, f"HTTP {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        log_test("서버 상태", False, "서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
        return False
    except Exception as e:
        log_test("서버 상태", False, str(e))
        return False


def test_labels_api():
    """라벨 API 테스트"""
    print("\n🔍 2. 라벨 API 테스트")
    print("=" * 60)
    
    # 라벨 목록 조회
    try:
        response = requests.get(f"{API_BASE}/labels", timeout=5)
        if response.status_code == 200:
            labels = response.json()
            log_test("라벨 목록 조회", True, f"{len(labels)}개 라벨 발견")
        else:
            log_test("라벨 목록 조회", False, f"HTTP {response.status_code}")
            return False
    except Exception as e:
        log_test("라벨 목록 조회", False, str(e))
        return False
    
    # 테스트 라벨 생성
    test_label_name = "test_phase7_integration"
    try:
        response = requests.post(
            f"{API_BASE}/labels",
            json={
                "name": test_label_name,
                "label_type": "domain",
                "description": "Phase 7 통합 테스트용 라벨"
            },
            timeout=5
        )
        if response.status_code == 200:
            label_data = response.json()
            test_label_id = label_data.get("id")
            log_test("라벨 생성", True, f"라벨 ID: {test_label_id}")
        else:
            error_data = response.json() if response.content else {}
            if "already exists" in str(error_data).lower() or response.status_code == 400:
                # 이미 존재하는 경우 기존 라벨 찾기
                response = requests.get(f"{API_BASE}/labels", timeout=5)
                labels = response.json()
                for label in labels:
                    if label.get("name") == test_label_name:
                        test_label_id = label.get("id")
                        log_warning("라벨 생성", f"라벨이 이미 존재합니다 (ID: {test_label_id})")
                        break
                else:
                    log_test("라벨 생성", False, f"HTTP {response.status_code}: {error_data}")
                    return False
            else:
                log_test("라벨 생성", False, f"HTTP {response.status_code}: {error_data}")
                return False
    except Exception as e:
        log_test("라벨 생성", False, str(e))
        return False
    
    # 테스트 라벨 삭제
    try:
        response = requests.delete(f"{API_BASE}/labels/{test_label_id}", timeout=5)
        if response.status_code == 200:
            log_test("라벨 삭제", True, f"라벨 ID {test_label_id} 삭제 완료")
        else:
            log_test("라벨 삭제", False, f"HTTP {response.status_code}")
    except Exception as e:
        log_test("라벨 삭제", False, str(e))
    
    return True


def test_knowledge_chunks_api():
    """지식 청크 API 테스트"""
    print("\n🔍 3. 지식 청크 API 테스트")
    print("=" * 60)
    
    # 청크 목록 조회
    try:
        response = requests.get(f"{API_BASE}/knowledge/chunks?limit=10", timeout=10)
        if response.status_code == 200:
            chunks = response.json()
            if isinstance(chunks, list):
                log_test("청크 목록 조회", True, f"{len(chunks)}개 청크 발견")
                if len(chunks) > 0:
                    # 첫 번째 청크 상세 조회
                    first_chunk_id = chunks[0].get("id")
                    if first_chunk_id:
                        response2 = requests.get(f"{API_BASE}/knowledge/chunks/{first_chunk_id}", timeout=5)
                        if response2.status_code == 200:
                            log_test("청크 상세 조회", True, f"청크 ID {first_chunk_id} 조회 성공")
                        else:
                            log_test("청크 상세 조회", False, f"HTTP {response2.status_code}")
                else:
                    log_warning("청크 목록 조회", "청크가 없습니다. 문서를 먼저 임베딩하세요.")
            else:
                log_test("청크 목록 조회", False, "응답 형식이 올바르지 않습니다")
        else:
            log_test("청크 목록 조회", False, f"HTTP {response.status_code}")
            return False
    except Exception as e:
        log_test("청크 목록 조회", False, str(e))
        return False
    
    return True


def test_reasoning_modes():
    """Reasoning 모드 테스트"""
    print("\n🔍 4. Reasoning 모드 테스트")
    print("=" * 60)
    
    modes = [
        "design_explain",
        "risk_review",
        "next_steps",
        "history_trace"
    ]
    
    for mode in modes:
        try:
            response = requests.post(
                f"{API_BASE}/reason",
                json={
                    "mode": mode,
                    "inputs": {
                        "projects": [],
                        "labels": []
                    },
                    "question": f"Phase 7 통합 테스트 - {mode} 모드 테스트"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                # 응답 구조 확인
                has_answer = "answer" in result
                has_chunks = "context_chunks" in result
                has_relations = "relations" in result
                has_steps = "reasoning_steps" in result
                
                if has_answer and has_chunks and has_relations and has_steps:
                    chunks_count = len(result.get("context_chunks", []))
                    relations_count = len(result.get("relations", []))
                    steps_count = len(result.get("reasoning_steps", []))
                    
                    log_test(
                        f"Reasoning 모드: {mode}",
                        True,
                        f"청크: {chunks_count}개, 관계: {relations_count}개, 단계: {steps_count}개"
                    )
                else:
                    log_test(
                        f"Reasoning 모드: {mode}",
                        False,
                        f"응답 구조 불완전 (answer: {has_answer}, chunks: {has_chunks}, relations: {has_relations}, steps: {has_steps})"
                    )
            elif response.status_code == 400:
                error_data = response.json() if response.content else {}
                if "수집된 지식이 없습니다" in str(error_data.get("detail", "")):
                    log_warning(
                        f"Reasoning 모드: {mode}",
                        "지식이 없어 테스트를 건너뜁니다. 문서를 먼저 임베딩하세요."
                    )
                else:
                    log_test(f"Reasoning 모드: {mode}", False, f"HTTP {response.status_code}: {error_data}")
            else:
                error_data = response.json() if response.content else {}
                log_test(f"Reasoning 모드: {mode}", False, f"HTTP {response.status_code}: {error_data}")
        except requests.exceptions.Timeout:
            log_test(f"Reasoning 모드: {mode}", False, "요청 시간 초과 (30초)")
        except Exception as e:
            log_test(f"Reasoning 모드: {mode}", False, str(e))


def test_knowledge_admin_workflow():
    """Knowledge Admin 워크플로우 테스트"""
    print("\n🔍 5. Knowledge Admin 워크플로우 테스트")
    print("=" * 60)
    
    # 1. 라벨 생성
    test_label_name = "test_admin_workflow"
    test_label_id = None
    
    try:
        response = requests.post(
            f"{API_BASE}/labels",
            json={
                "name": test_label_name,
                "label_type": "domain",
                "description": "워크플로우 테스트용"
            },
            timeout=5
        )
        if response.status_code == 200:
            label_data = response.json()
            test_label_id = label_data.get("id")
            log_test("워크플로우: 라벨 생성", True, f"라벨 ID: {test_label_id}")
        else:
            error_data = response.json() if response.content else {}
            if "already exists" in str(error_data).lower() or response.status_code == 400:
                # 기존 라벨 찾기
                response = requests.get(f"{API_BASE}/labels", timeout=5)
                labels = response.json()
                for label in labels:
                    if label.get("name") == test_label_name:
                        test_label_id = label.get("id")
                        log_warning("워크플로우: 라벨 생성", f"라벨이 이미 존재합니다 (ID: {test_label_id})")
                        break
                else:
                    log_test("워크플로우: 라벨 생성", False, f"HTTP {response.status_code}")
                    return False
            else:
                log_test("워크플로우: 라벨 생성", False, f"HTTP {response.status_code}")
                return False
    except Exception as e:
        log_test("워크플로우: 라벨 생성", False, str(e))
        return False
    
    # 2. 청크 목록 조회 및 첫 번째 청크 선택
    try:
        response = requests.get(f"{API_BASE}/knowledge/chunks?limit=1", timeout=10)
        if response.status_code == 200:
            chunks = response.json()
            if isinstance(chunks, list) and len(chunks) > 0:
                test_chunk_id = chunks[0].get("id")
                
                # 3. 청크에 라벨 부여
                try:
                    response = requests.post(
                        f"{API_BASE}/labels/chunks/{test_chunk_id}/labels/{test_label_id}",
                        timeout=5
                    )
                    if response.status_code == 200:
                        log_test("워크플로우: 청크에 라벨 부여", True, f"청크 ID {test_chunk_id}에 라벨 부여 완료")
                    else:
                        error_data = response.json() if response.content else {}
                        if "already" in str(error_data).lower():
                            log_warning("워크플로우: 청크에 라벨 부여", "라벨이 이미 부여되어 있습니다")
                        else:
                            log_test("워크플로우: 청크에 라벨 부여", False, f"HTTP {response.status_code}: {error_data}")
                except Exception as e:
                    log_test("워크플로우: 청크에 라벨 부여", False, str(e))
                
                # 4. 청크의 라벨 확인
                try:
                    response = requests.get(f"{API_BASE}/labels/chunks/{test_chunk_id}/labels", timeout=5)
                    if response.status_code == 200:
                        chunk_labels = response.json()
                        label_names = [l.get("name") for l in chunk_labels]
                        if test_label_name in label_names:
                            log_test("워크플로우: 청크 라벨 확인", True, f"라벨 '{test_label_name}' 확인됨")
                        else:
                            log_test("워크플로우: 청크 라벨 확인", False, f"라벨이 확인되지 않습니다. 발견된 라벨: {label_names}")
                    else:
                        log_test("워크플로우: 청크 라벨 확인", False, f"HTTP {response.status_code}")
                except Exception as e:
                    log_test("워크플로우: 청크 라벨 확인", False, str(e))
                
                # 5. 청크에서 라벨 제거
                try:
                    response = requests.delete(
                        f"{API_BASE}/labels/chunks/{test_chunk_id}/labels/{test_label_id}",
                        timeout=5
                    )
                    if response.status_code == 200:
                        log_test("워크플로우: 청크에서 라벨 제거", True, f"청크 ID {test_chunk_id}에서 라벨 제거 완료")
                    else:
                        log_test("워크플로우: 청크에서 라벨 제거", False, f"HTTP {response.status_code}")
                except Exception as e:
                    log_test("워크플로우: 청크에서 라벨 제거", False, str(e))
                
            else:
                log_warning("워크플로우", "청크가 없어 워크플로우 테스트를 건너뜁니다.")
        else:
            log_test("워크플로우: 청크 목록 조회", False, f"HTTP {response.status_code}")
    except Exception as e:
        log_test("워크플로우: 청크 목록 조회", False, str(e))
    
    # 6. 테스트 라벨 삭제
    if test_label_id:
        try:
            response = requests.delete(f"{API_BASE}/labels/{test_label_id}", timeout=5)
            if response.status_code == 200:
                log_test("워크플로우: 테스트 라벨 삭제", True, f"라벨 ID {test_label_id} 삭제 완료")
            else:
                log_test("워크플로우: 테스트 라벨 삭제", False, f"HTTP {response.status_code}")
        except Exception as e:
            log_test("워크플로우: 테스트 라벨 삭제", False, str(e))


def test_web_pages():
    """웹 페이지 접근 테스트"""
    print("\n🔍 6. 웹 페이지 접근 테스트")
    print("=" * 60)
    
    pages = [
        ("/reason", "Reasoning Lab"),
        ("/knowledge-admin", "Knowledge Admin"),
        ("/knowledge", "Knowledge Studio"),
    ]
    
    for path, name in pages:
        try:
            response = requests.get(f"{BASE_URL}{path}", timeout=5)
            if response.status_code == 200:
                log_test(f"웹 페이지: {name}", True, f"{path} 접근 성공")
            else:
                log_test(f"웹 페이지: {name}", False, f"HTTP {response.status_code}")
        except Exception as e:
            log_test(f"웹 페이지: {name}", False, str(e))


def print_summary():
    """테스트 결과 요약 출력"""
    print("\n" + "=" * 60)
    print("📊 테스트 결과 요약")
    print("=" * 60)
    
    total = len(test_results["passed"]) + len(test_results["failed"])
    passed = len(test_results["passed"])
    failed = len(test_results["failed"])
    warnings = len(test_results["warnings"])
    
    print(f"\n✅ 통과: {passed}개")
    print(f"❌ 실패: {failed}개")
    print(f"⚠️  경고: {warnings}개")
    print(f"📈 성공률: {(passed/total*100) if total > 0 else 0:.1f}%")
    
    if test_results["failed"]:
        print("\n❌ 실패한 테스트:")
        for test in test_results["failed"]:
            print(f"   - {test}")
    
    if test_results["warnings"]:
        print("\n⚠️  경고:")
        for warning in test_results["warnings"]:
            print(f"   - {warning}")
    
    print("\n" + "=" * 60)
    
    if failed == 0:
        print("🎉 모든 테스트 통과!")
        return True
    else:
        print("⚠️  일부 테스트 실패. 위의 실패 항목을 확인하세요.")
        return False


def main():
    """메인 테스트 실행"""
    print("=" * 60)
    print("🧪 Phase 7 통합 테스트 시작")
    print("=" * 60)
    print(f"서버 URL: {BASE_URL}")
    print()
    
    # 서버 상태 확인
    if not test_server_health():
        print("\n❌ 서버가 실행 중이지 않습니다. 테스트를 중단합니다.")
        print("서버를 시작하려면: python scripts/start_server.py")
        return False
    
    # 각 테스트 실행
    test_labels_api()
    test_knowledge_chunks_api()
    test_reasoning_modes()
    test_knowledge_admin_workflow()
    test_web_pages()
    
    # 결과 요약
    success = print_summary()
    
    return success


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  테스트가 사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 테스트 실행 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

