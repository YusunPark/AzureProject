#!/bin/bash

echo "🚀 AI 문서 작성 어시스턴트 시작 중..."

# 가상환경 활성화 (필요한 경우)
# source venv/bin/activate

# 의존성 설치
echo "📦 의존성 설치 중..."
pip install -r requirements.txt

# 환경 변수 설정
export STREAMLIT_THEME_BASE="light"
export STREAMLIT_THEME_PRIMARY_COLOR="#8b5cf6"

# Streamlit 앱 실행 (리팩토링된 버전)
echo "🌐 Streamlit 서버 시작 (리팩토링 버전)..."
streamlit run app_refactored.py --server.port=8501 --server.address=0.0.0.0

echo "✅ 애플리케이션이 실행되었습니다!"
echo "🔗 브라우저에서 http://localhost:8501 접속"