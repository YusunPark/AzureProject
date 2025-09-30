#!/bin/bash

# Azure App Service 게시 프로필 다운로드 스크립트

set -e

# 변수 설정
APP_NAME="appsvc-yusun-01"
RESOURCE_GROUP="rg-yusun-01"

echo "📥 Azure App Service 게시 프로필 다운로드 중..."

# Azure CLI 로그인 확인
az account show > /dev/null 2>&1 || {
    echo "❌ Azure CLI에 로그인이 필요합니다."
    echo "   다음 명령어를 실행하세요: az login"
    exit 1
}

# 게시 프로필 다운로드
az webapp deployment list-publishing-profiles \
    --name "$APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --xml > "${APP_NAME}_publish_profile.xml"

if [ $? -eq 0 ]; then
    echo "✅ 게시 프로필 다운로드 완료: ${APP_NAME}_publish_profile.xml"
    echo ""
    echo "📋 GitHub Actions 설정 방법:"
    echo "1. GitHub 저장소의 Settings > Secrets and variables > Actions로 이동"
    echo "2. 'New repository secret' 클릭"
    echo "3. Name: AZURE_WEBAPP_PUBLISH_PROFILE"
    echo "4. Value: ${APP_NAME}_publish_profile.xml 파일의 내용을 복사하여 붙여넣기"
    echo ""
    echo "⚠️  보안상 게시 프로필 파일을 Git에 커밋하지 마세요!"
else
    echo "❌ 게시 프로필 다운로드 실패!"
    exit 1
fi