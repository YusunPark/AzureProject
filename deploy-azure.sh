#!/bin/bash

# Azure App Service 배포 스크립트

set -e

echo "🚀 Azure App Service 배포를 시작합니다..."

# 변수 설정
APP_NAME="appsvc-yusun-01"
RESOURCE_GROUP="rg-yusun-01"
LOCATION="Korea Central"
SKU="B1"  # Basic tier

echo "📋 배포 정보:"
echo "   앱 이름: $APP_NAME"
echo "   리소스 그룹: $RESOURCE_GROUP"
echo "   위치: $LOCATION"
echo "   SKU: $SKU"

# Azure CLI 로그인 확인
echo "🔐 Azure 로그인 상태 확인..."
az account show > /dev/null 2>&1 || {
    echo "❌ Azure CLI에 로그인이 필요합니다."
    echo "   다음 명령어를 실행하세요: az login"
    exit 1
}

echo "✅ Azure 로그인 확인됨"

# 파일 실행 권한 설정
chmod +x startup.sh

# Azure App Service에 배포
echo "📦 Azure App Service에 배포 중..."
az webapp up \
    --name "$APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --location "$LOCATION" \
    --runtime "PYTHON:3.13" \
    --sku "$SKU" \
    --logs

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 배포 완료!"
    echo ""
    echo "📋 배포 정보:"
    echo "   앱 이름: $APP_NAME"
    echo "   URL: https://$APP_NAME.azurewebsites.net"
    echo "   리소스 그룹: $RESOURCE_GROUP"
    echo ""
    echo "⚙️  다음 단계:"
    echo "1. Azure Portal에서 App Service 설정으로 이동"
    echo "2. 환경 변수 설정:"
    echo "   - OPENAI_ENDPOINT"
    echo "   - OPENAI_API_KEY"
    echo "   - OPENAI_DEPLOYMENT_NAME"
    echo "   - TAVILY_API_KEY"
    echo "   - ONLYOFFICE_API_KEY"
    echo ""
    echo "3. OnlyOffice DocSpace에서 허용 도메인에 추가:"
    echo "   https://$APP_NAME.azurewebsites.net"
    echo ""
    echo "🌐 앱 접속: https://$APP_NAME.azurewebsites.net"
else
    echo "❌ 배포 실패!"
    exit 1
fi