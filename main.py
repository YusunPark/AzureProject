"""
🤖 AI 문서 작성 어시스턴트 - 메인 진입점
리팩토링된 최신 버전 
"""
import sys
import os

# 프로젝트 루트 경로를 Python path에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app_refactored import main

if __name__ == "__main__":
    print("🚀 AI 문서 작성 어시스턴트 시작...")
    main()