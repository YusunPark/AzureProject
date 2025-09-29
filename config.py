"""
설정 파일
"""
import os
from dotenv import load_dotenv

# Azure App Service 환경 감지
IS_AZURE_APP_SERVICE = os.getenv('WEBSITE_SITE_NAME') is not None

# 환경에 따라 .env 파일 로드
if IS_AZURE_APP_SERVICE:
    print("🔵 Azure App Service 환경에서 실행 중")
    # Azure에서는 환경 변수를 직접 사용
else:
    print("🟢 로컬 환경에서 실행 중")
    # 로컬에서는 .env 파일 로드
    load_dotenv()

# OnlyOffice DocSpace 설정
ONLYOFFICE_CONFIG = {
    "docspace_url": os.getenv("ONLYOFFICE_DOCSPACE_URL", "https://docspace-i0p5og.onlyoffice.com"),
    "sdk_url": os.getenv("ONLYOFFICE_SDK_URL", "https://docspace-i0p5og.onlyoffice.com/static/scripts/sdk/2.0.0/api.js"),
    "api_key": os.getenv("ONLYOFFICE_API_KEY"),
    "jwt_secret": os.getenv("ONLYOFFICE_JWT_SECRET", "your_jwt_secret_key"),
    "jwt_header": "Authorization",
    "mode": "editor",
    "frame_id": "ds-frame"
}

# AI 모델 설정 (Azure OpenAI)
AI_CONFIG = {
    "openai_endpoint": os.getenv("OPENAI_ENDPOINT"),
    "openai_api_key": os.getenv("OPENAI_API_KEY"),
    "deployment_name": os.getenv("OPENAI_DEPLOYMENT_NAME", "gpt-4o"),
    "api_version": os.getenv("OPENAI_API_VERSION", "2024-12-01-preview"),
    "max_tokens": 1000,
    "temperature": 0.7
}

# Tavily 검색 API 설정
TAVILY_CONFIG = {
    "api_key": os.getenv("TAVILY_API_KEY"),
    "search_depth": "advanced",
    "max_results": 10
}

# LangSmith 추적 설정
LANGSMITH_CONFIG = {
    "api_key": os.getenv("LANGSMITH_API_KEY"),
    "project_name": "AI-Document-Assistant",
    "endpoint": "https://api.smith.langchain.com",
    "enabled": bool(os.getenv("LANGSMITH_API_KEY"))
}

# 데이터베이스 설정
DATABASE_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "document_assistant",
    "user": "your_username",
    "password": "your_password"
}

# 앱 설정
APP_CONFIG = {
    "max_upload_size": 10 * 1024 * 1024,  # 10MB
    "supported_formats": [".docx", ".pptx", ".pdf", ".txt"],
    "cache_duration": 3600  # 1시간
}