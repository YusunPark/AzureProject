#!/bin/bash

# Azure App Service 환경 변수 설정 스크립트

APP_NAME="appsvc-yusun-01"
RESOURCE_GROUP="rg-yusun-01"

echo "🔧 Azure App Service 환경 변수를 설정합니다..."
echo "   앱 이름: $APP_NAME"
echo "   리소스 그룹: $RESOURCE_GROUP"

# .env 파일에서 환경 변수 읽기
if [ -f ".env" ]; then
    source .env
    echo "📁 .env 파일에서 환경 변수를 로드했습니다."
else
    echo "⚠️  .env 파일이 없습니다. 수동으로 값을 입력해주세요."
fi

# 환경 변수 설정
echo "🔑 API 키 및 설정을 Azure App Service에 적용 중..."

az webapp config appsettings set \
    --name "$APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --settings \
        "OPENAI_ENDPOINT=${OPENAI_ENDPOINT}" \
        "OPENAI_API_KEY=${OPENAI_API_KEY}" \
        "OPENAI_DEPLOYMENT_NAME=${OPENAI_DEPLOYMENT_NAME:-gpt-4o}" \
        "OPENAI_API_VERSION=${OPENAI_API_VERSION:-2024-12-01-preview}" \
        "TAVILY_API_KEY=${TAVILY_API_KEY}" \
        "ONLYOFFICE_API_KEY=${ONLYOFFICE_API_KEY}" \
        "ONLYOFFICE_DOCSPACE_URL=${ONLYOFFICE_DOCSPACE_URL:-https://docspace-i0p5og.onlyoffice.com}" \
        "ONLYOFFICE_SDK_URL=${ONLYOFFICE_SDK_URL:-https://docspace-i0p5og.onlyoffice.com/static/scripts/sdk/2.0.0/api.js}" \
        "WEBSITES_PORT=8000" \
        "SCM_DO_BUILD_DURING_DEPLOYMENT=true" \
        "STREAMLIT_SERVER_PORT=8000" \
        "STREAMLIT_SERVER_ADDRESS=0.0.0.0" \
        "STREAMLIT_SERVER_HEADLESS=true" \
        "STREAMLIT_SERVER_ENABLE_CORS=false" \
        "STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false" \
        "ENVIRONMENT=production" \
        "DEBUG=False"

if [ $? -eq 0 ]; then
    echo "✅ 환경 변수 설정 완료!"
    echo ""
    echo "🔄 App Service를 다시 시작하여 새 설정을 적용합니다..."
    
    az webapp restart \
        --name "$APP_NAME" \
        --resource-group "$RESOURCE_GROUP"
    
    echo "✅ App Service 재시작 완료!"
    echo ""
    echo "🌐 앱 접속: https://$APP_NAME.azurewebsites.net"
    echo ""
    echo "📋 다음 단계:"
    echo "1. OnlyOffice DocSpace 설정에서 허용 도메인에 추가:"
    echo "   https://$APP_NAME.azurewebsites.net"
    echo "2. 앱이 정상 작동하는지 확인"
    
else
    echo "❌ 환경 변수 설정 실패!"
    exit 1
fi