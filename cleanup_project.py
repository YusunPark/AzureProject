#!/usr/bin/env python3
"""
프로젝트 정리 스크립트
불필요한 파일들과 __pycache__ 폴더들을 정리합니다.
"""
import os
import shutil
from pathlib import Path

def cleanup_project():
    """프로젝트 정리 실행"""
    project_root = Path(__file__).parent
    
    print("🧹 프로젝트 정리 시작...")
    
    # 1. __pycache__ 폴더들 정리
    pycache_count = 0
    for pycache_dir in project_root.rglob("__pycache__"):
        if pycache_dir.is_dir() and not str(pycache_dir).startswith(".venv"):
            try:
                shutil.rmtree(pycache_dir)
                pycache_count += 1
                print(f"   🗑️ 삭제: {pycache_dir}")
            except Exception as e:
                print(f"   ❌ 삭제 실패: {pycache_dir} - {e}")
    
    # 2. .pyc 파일들 정리
    pyc_count = 0
    for pyc_file in project_root.rglob("*.pyc"):
        if not str(pyc_file).startswith(".venv"):
            try:
                pyc_file.unlink()
                pyc_count += 1
            except Exception as e:
                print(f"   ❌ .pyc 파일 삭제 실패: {pyc_file} - {e}")
    
    # 3. 임시 파일들 정리
    temp_patterns = ["*.tmp", "*.temp", "*~", ".DS_Store"]
    temp_count = 0
    for pattern in temp_patterns:
        for temp_file in project_root.rglob(pattern):
            if not str(temp_file).startswith(".venv"):
                try:
                    if temp_file.is_file():
                        temp_file.unlink()
                        temp_count += 1
                        print(f"   🗑️ 임시 파일 삭제: {temp_file}")
                except Exception as e:
                    print(f"   ❌ 임시 파일 삭제 실패: {temp_file} - {e}")
    
    # 4. 사용하지 않는 스크립트 파일들 확인
    unused_files = [
        "fix_azure_search.py"  # 일회성 수정 스크립트
    ]
    
    for unused_file in unused_files:
        file_path = project_root / unused_file
        if file_path.exists():
            print(f"   ⚠️ 사용하지 않는 파일 발견: {unused_file}")
            print(f"      (필요 시 수동으로 삭제하세요)")
    
    print(f"\n✅ 정리 완료:")
    print(f"   📁 __pycache__ 폴더: {pycache_count}개 삭제")
    print(f"   🐍 .pyc 파일: {pyc_count}개 삭제") 
    print(f"   📄 임시 파일: {temp_count}개 삭제")
    
    # 5. 현재 프로젝트 구조 요약
    print(f"\n📋 현재 프로젝트 구조:")
    important_dirs = ["core", "services", "ui", "utils", "state"]
    for dir_name in important_dirs:
        dir_path = project_root / dir_name
        if dir_path.exists():
            py_files = list(dir_path.rglob("*.py"))
            print(f"   📁 {dir_name}/: {len(py_files)}개 Python 파일")
    
    print(f"\n🚀 프로젝트가 깨끗하게 정리되었습니다!")

if __name__ == "__main__":
    cleanup_project()