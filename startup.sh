#!/bin/bash

# Azure App Service에서 Streamlit 앱을 시작하는 스크립트

echo "🚀 Starting AI Document Assistant on Azure App Service..."

# Python 패키지 설치 (필요한 경우)
if [ ! -f "/tmp/.packages_installed" ]; then
    echo "📦 Installing Python packages..."
    pip install -r requirements.txt
    touch /tmp/.packages_installed
    echo "✅ Packages installed"
fi

# 환경 변수 확인
echo "🔍 Checking environment variables..."
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OPENAI_API_KEY not set"
fi

if [ -z "$TAVILY_API_KEY" ]; then
    echo "⚠️  TAVILY_API_KEY not set"
fi

if [ -z "$ONLYOFFICE_API_KEY" ]; then
    echo "⚠️  ONLYOFFICE_API_KEY not set"
fi

# Streamlit 설정
export STREAMLIT_SERVER_PORT=${WEBSITES_PORT:-8000}
export STREAMLIT_SERVER_ADDRESS="0.0.0.0"
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_SERVER_ENABLE_CORS=false
export STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false

echo "🌐 Starting Streamlit on port $STREAMLIT_SERVER_PORT..."

# Streamlit 앱 시작
streamlit run app.py \
    --server.port=$STREAMLIT_SERVER_PORT \
    --server.address=$STREAMLIT_SERVER_ADDRESS \
    --server.headless=$STREAMLIT_SERVER_HEADLESS \
    --server.enableCORS=$STREAMLIT_SERVER_ENABLE_CORS \
    --server.enableXsrfProtection=$STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION