#!/bin/bash

# 향상된 Azure App Service 배포 스크립트 (ZIP 배포 사용)

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 변수 설정
APP_NAME="appsvc-yusun-01"
RESOURCE_GROUP="rg-yusun-01"
LOCATION="Korea Central"
SKU="B1"
PYTHON_VERSION="3.11"

echo -e "${BLUE}🚀 Azure App Service ZIP 배포를 시작합니다...${NC}"

# 함수 정의
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Azure CLI 로그인 확인
log_info "Azure 로그인 상태 확인..."
az account show > /dev/null 2>&1 || {
    log_error "Azure CLI에 로그인이 필요합니다."
    echo "   다음 명령어를 실행하세요: az login"
    exit 1
}

log_success "Azure 로그인 확인됨"

# 배포 패키지 생성
log_info "배포 패키지 생성 중..."

# 임시 디렉토리 생성
TEMP_DIR=$(mktemp -d)
DEPLOY_ZIP="deploy.zip"

# 필요한 파일들을 임시 디렉토리로 복사
cp -r . "$TEMP_DIR/"

# 불필요한 파일들 제거
rm -rf "$TEMP_DIR"/.git
rm -rf "$TEMP_DIR"/__pycache__
rm -rf "$TEMP_DIR"/.venv
rm -rf "$TEMP_DIR"/venv
rm -f "$TEMP_DIR"/.env
rm -f "$TEMP_DIR"/*.zip
rm -f "$TEMP_DIR"/*.xml

# ZIP 파일 생성
cd "$TEMP_DIR"
zip -r "../$DEPLOY_ZIP" . -q
cd - > /dev/null

# 임시 디렉토리 정리
rm -rf "$TEMP_DIR"

log_success "배포 패키지 생성 완료: $DEPLOY_ZIP"

# App Service 존재 확인
log_info "App Service 상태 확인..."
APP_EXISTS=$(az webapp show --name "$APP_NAME" --resource-group "$RESOURCE_GROUP" --query "name" -o tsv 2>/dev/null || echo "")

if [ -z "$APP_EXISTS" ]; then
    log_info "App Service 생성 중..."
    
    # 리소스 그룹 생성 (존재하지 않는 경우)
    az group create --name "$RESOURCE_GROUP" --location "$LOCATION" > /dev/null
    
    # App Service Plan 생성 (존재하지 않는 경우)
    PLAN_NAME="${APP_NAME}-plan"
    az appservice plan create \
        --name "$PLAN_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --location "$LOCATION" \
        --sku "$SKU" \
        --is-linux > /dev/null
    
    # Web App 생성
    az webapp create \
        --name "$APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --plan "$PLAN_NAME" \
        --runtime "PYTHON|$PYTHON_VERSION" > /dev/null
    
    log_success "App Service 생성 완료"
else
    log_success "App Service 존재 확인"
fi

# 시작 명령어 설정
log_info "시작 명령어 설정..."
az webapp config set \
    --name "$APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --startup-file "bash startup.sh" > /dev/null

# ZIP 배포
log_info "ZIP 파일 배포 중..."
az webapp deploy \
    --name "$APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --src-path "$DEPLOY_ZIP" \
    --type zip

# 배포 패키지 정리
rm -f "$DEPLOY_ZIP"

# 환경 변수 설정 (이미 설정되어 있는지 확인)
log_info "환경 변수 확인..."
OPENAI_ENDPOINT=$(az webapp config appsettings list --name "$APP_NAME" --resource-group "$RESOURCE_GROUP" --query "[?name=='OPENAI_ENDPOINT'].value" -o tsv)

if [ -z "$OPENAI_ENDPOINT" ]; then
    log_warning "환경 변수가 설정되지 않았습니다."
    log_info "configure-env.sh 스크립트를 실행하여 환경 변수를 설정하세요."
else
    log_success "환경 변수 설정 확인"
fi

# 앱 재시작
log_info "App Service 재시작..."
az webapp restart --name "$APP_NAME" --resource-group "$RESOURCE_GROUP" > /dev/null

log_success "배포 완료!"
echo ""
echo -e "${BLUE}📋 배포 정보:${NC}"
echo "   앱 이름: $APP_NAME"
echo "   URL: https://$APP_NAME.azurewebsites.net"
echo "   리소스 그룹: $RESOURCE_GROUP"
echo ""
log_info "배포 로그 확인: az webapp log tail --name $APP_NAME --resource-group $RESOURCE_GROUP"
echo -e "${GREEN}🌐 앱 접속: https://$APP_NAME.azurewebsites.net${NC}"