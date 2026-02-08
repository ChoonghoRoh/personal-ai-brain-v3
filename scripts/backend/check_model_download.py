#!/usr/bin/env python3
"""
모델 다운로드 진행 상황 확인 스크립트
"""

import os
from pathlib import Path

cache_dir = Path.home() / ".cache" / "gpt4all"

print("="*60)
print("모델 다운로드 진행 상황 확인")
print("="*60)

if not cache_dir.exists():
    print("❌ 캐시 디렉토리가 없습니다.")
    exit(1)

# 모델 파일 확인
model_name = "Meta-Llama-3-8B-Instruct.Q4_0.gguf"
model_file = cache_dir / model_name
part_file = cache_dir / f"{model_name}.part"

expected_size = 4.66 * 1024 * 1024 * 1024  # 4.66 GB in bytes

print(f"\n모델: {model_name}")
print(f"예상 크기: 4.66 GB\n")

# 완료된 파일 확인
if model_file.exists():
    size = model_file.stat().st_size
    size_gb = size / (1024 * 1024 * 1024)
    percentage = (size / expected_size) * 100
    
    print(f"✅ 모델 파일 존재")
    print(f"   크기: {size_gb:.2f} GB ({percentage:.1f}%)")
    
    if size >= expected_size * 0.95:  # 95% 이상이면 완료로 간주
        print(f"   상태: 다운로드 완료 ✅")
    else:
        print(f"   상태: 다운로드 불완전 ⚠️")
elif part_file.exists():
    size = part_file.stat().st_size
    size_gb = size / (1024 * 1024 * 1024)
    percentage = (size / expected_size) * 100
    
    print(f"⏳ 다운로드 진행 중")
    print(f"   현재 크기: {size_gb:.2f} GB")
    print(f"   진행률: {percentage:.1f}%")
    print(f"   남은 크기: {4.66 - size_gb:.2f} GB")
    
    # 예상 남은 시간 계산 (평균 속도 10 MiB/s 가정)
    remaining_gb = 4.66 - size_gb
    estimated_minutes = (remaining_gb * 1024) / 10 / 60
    print(f"   예상 남은 시간: 약 {estimated_minutes:.1f}분")
else:
    print(f"❌ 모델 파일이 없습니다.")
    print(f"   다운로드가 시작되지 않았거나 완료되지 않았습니다.")

# 기존 모델 확인
print(f"\n기존 모델:")
for file in cache_dir.glob("*.gguf"):
    if file.name != model_name:
        size_gb = file.stat().st_size / (1024 * 1024 * 1024)
        print(f"  - {file.name}: {size_gb:.2f} GB")

print("\n" + "="*60)
print("다운로드 확인 방법:")
print("  python scripts/check_model_download.py")
print("="*60)
