#!/usr/bin/env python3
"""
GPT4All 모델 설치 정보 및 라이브러리 연결 확인 스크립트

사용법:
    python scripts/check_gpt4all_model.py
"""

import sys
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def check_gpt4all_installation():
    """GPT4All 패키지 설치 여부 확인"""
    print("="*60)
    print("1. GPT4All 패키지 설치 확인")
    print("="*60)
    
    try:
        import gpt4all
        print(f"✅ gpt4all 패키지 설치됨")
        
        # 버전 확인
        try:
            version = gpt4all.__version__
            print(f"   버전: {version}")
        except AttributeError:
            print("   버전: 확인 불가")
        
        return True
    except ImportError:
        print("❌ gpt4all 패키지가 설치되지 않았습니다.")
        print("   설치 방법: pip install gpt4all")
        return False


def check_model_info():
    """모델 정보 확인"""
    print("\n" + "="*60)
    print("2. 모델 정보 확인")
    print("="*60)
    
    model_name = "Meta-Llama-3-8B-Instruct.Q4_0.gguf"
    print(f"모델 이름: {model_name}")
    print(f"모델 크기: 약 4.66 GB")
    print(f"필요 RAM: 약 8 GB")
    print(f"파라미터: 8B")
    
    return model_name


def check_model_storage_location():
    """모델 저장 위치 확인"""
    print("\n" + "="*60)
    print("3. 모델 저장 위치 확인")
    print("="*60)
    
    # GPT4All 기본 저장 위치
    home_dir = Path.home()
    cache_dir = home_dir / ".cache" / "gpt4all"
    
    print(f"기본 저장 위치: {cache_dir}")
    
    if cache_dir.exists():
        print(f"✅ 캐시 디렉토리 존재")
        
        # 모델 파일 확인
        model_files = list(cache_dir.glob("*.gguf"))
        model_files.extend(list(cache_dir.glob("*.bin")))
        
        if model_files:
            print(f"\n📁 발견된 모델 파일 ({len(model_files)}개):")
            for model_file in model_files:
                size_mb = model_file.stat().st_size / (1024 * 1024)
                size_gb = size_mb / 1024
                print(f"   - {model_file.name} ({size_gb:.2f} GB)")
        else:
            print("⚠️  모델 파일이 없습니다. 첫 실행 시 자동으로 다운로드됩니다.")
    else:
        print("⚠️  캐시 디렉토리가 없습니다. 첫 실행 시 생성됩니다.")
    
    return cache_dir


def check_code_connections():
    """코드에서 라이브러리 연결 확인"""
    print("\n" + "="*60)
    print("4. 코드에서 라이브러리 연결 확인")
    print("="*60)
    
    files_to_check = [
        ("backend/routers/ai.py", "get_gpt4all_model()"),
        ("backend/services/system_service.py", "_get_gpt4all_status()"),
        ("scripts/embed_and_store.py", "extract_title_with_ai()"),
        ("scripts/extract_keywords_and_labels.py", "extract_keywords_with_gpt4all()"),
        ("scripts/search_and_query.py", "query_with_gpt4all()"),
        ("scripts/generate_chunk_titles.py", "extract_title_with_ai() (import)"),
    ]
    
    model_name = "Meta-Llama-3-8B-Instruct.Q4_0.gguf"
    
    print(f"사용 모델: {model_name}\n")
    
    for file_path, function_name in files_to_check:
        full_path = PROJECT_ROOT / file_path
        if full_path.exists():
            # 파일에서 모델 이름 확인
            content = full_path.read_text(encoding='utf-8')
            if model_name in content:
                print(f"✅ {file_path}")
                print(f"   함수: {function_name}")
            elif "GPT4All" in content or "gpt4all" in content:
                print(f"⚠️  {file_path}")
                print(f"   함수: {function_name}")
                print(f"   모델 이름이 명시되지 않았거나 다른 모델 사용 중")
            else:
                print(f"ℹ️  {file_path}")
                print(f"   GPT4All 사용 안 함")
        else:
            print(f"❌ {file_path} - 파일 없음")


def test_model_loading():
    """모델 로딩 테스트"""
    print("\n" + "="*60)
    print("5. 모델 로딩 테스트")
    print("="*60)
    
    try:
        from gpt4all import GPT4All
        
        model_name = "Meta-Llama-3-8B-Instruct.Q4_0.gguf"
        print(f"모델 로딩 시도: {model_name}")
        print("⏳ 모델 다운로드/로딩 중... (처음 실행 시 시간이 걸릴 수 있습니다)")
        
        try:
            model = GPT4All(model_name)
            print("✅ 모델 로딩 성공!")
            
            # 간단한 테스트
            print("\n간단한 생성 테스트 중...")
            response = model.generate("Hello", max_tokens=10, temp=0.1)
            print(f"✅ 생성 테스트 성공: '{response[:50]}...'")
            
            return True
            
        except Exception as e:
            print(f"❌ 모델 로딩 실패: {e}")
            print("\n가능한 원인:")
            print("  - 모델 다운로드 실패 (인터넷 연결 확인)")
            print("  - 디스크 공간 부족")
            print("  - 메모리 부족")
            return False
            
    except ImportError:
        print("❌ gpt4all 패키지가 설치되지 않았습니다.")
        return False


def main():
    """메인 함수"""
    print("\n" + "="*60)
    print("GPT4All 모델 설치 정보 및 라이브러리 연결 확인")
    print("="*60 + "\n")
    
    # 1. 패키지 설치 확인
    is_installed = check_gpt4all_installation()
    
    if not is_installed:
        print("\n⚠️  gpt4all 패키지를 먼저 설치하세요:")
        print("   pip install gpt4all")
        return
    
    # 2. 모델 정보
    model_name = check_model_info()
    
    # 3. 저장 위치 확인
    cache_dir = check_model_storage_location()
    
    # 4. 코드 연결 확인
    check_code_connections()
    
    # 5. 모델 로딩 테스트 (선택적)
    print("\n" + "="*60)
    user_input = input("모델 로딩 테스트를 실행하시겠습니까? (y/n): ").strip().lower()
    if user_input == 'y':
        test_model_loading()
    else:
        print("모델 로딩 테스트를 건너뜁니다.")
    
    print("\n" + "="*60)
    print("확인 완료!")
    print("="*60)
    print("\n다음 단계:")
    print("1. 모델이 없으면 첫 실행 시 자동으로 다운로드됩니다")
    print("2. 제목 생성 스크립트 실행: python scripts/generate_chunk_titles.py --limit 5")
    print("3. 대시보드에서 GPT4All 상태 확인: http://localhost:8000/dashboard")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
