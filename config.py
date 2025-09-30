"""
설정 파일 - 애플리케이션 전체 설정 관리
"""
import os
from dotenv import load_dotenv

# Azure App Service 환경 감지
IS_AZURE_APP_SERVICE = os.getenv('WEBSITE_SITE_NAME') is not None

# 환경에 따라 .env 파일 로드
if IS_AZURE_APP_SERVICE:
    print("🔵 Azure App Service 환경에서 실행 중")
else:
    print("🟢 로컬 환경에서 실행 중")
    load_dotenv()

# AI 모델 설정 (Azure OpenAI)
AI_CONFIG = {
    "openai_endpoint": os.getenv("OPENAI_ENDPOINT"),
    "openai_api_key": os.getenv("OPENAI_API_KEY"),
    "deployment_name": os.getenv("OPENAI_DEPLOYMENT_NAME", "gpt-4o"),
    "embedding_deployment_name": os.getenv("OPENAI_EMBEDDING_DEPLOYMENT_NAME", "text-embedding-3-large"),
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

# Azure Search 설정
AZURE_SEARCH_CONFIG = {
    "endpoint": os.getenv("AZURE_SEARCH_ENDPOINT"),
    "admin_key": os.getenv("AZURE_SEARCH_ADMIN_KEY"),
    "api_key": os.getenv("AZURE_SEARCH_API_KEY"),
    "index_name": os.getenv("AZURE_SEARCH_INDEX_NAME", "doc-index"),
    "api_version": "2019-05-06"
}

# Azure Storage 설정
AZURE_STORAGE_CONFIG = {
    "account_name": os.getenv("AZURE_STORAGE_ACCOUNT_NAME"),
    "account_key": os.getenv("AZURE_STORAGE_ACCOUNT_KEY"),
    "container_name": os.getenv("AZURE_STORAGE_CONTAINER_NAME", "documents"),
    "blob_service_url": os.getenv("AZURE_STORAGE_BLOB_SERVICE_URL")
}

# LangSmith 추적 설정
LANGSMITH_CONFIG = {
    "api_key": os.getenv("LANGSMITH_API_KEY"),
    "project_name": "AI-Document-Assistant",
    "endpoint": "https://api.smith.langchain.com",
    "enabled": bool(os.getenv("LANGSMITH_API_KEY"))
}

# 앱 설정
APP_CONFIG = {
    "page_title": "AI 문서 작성 어시스턴트",
    "page_icon": "📝",
    "layout": "wide",
    "max_upload_size": 10 * 1024 * 1024,  # 10MB
    "supported_formats": [".docx", ".pptx", ".pdf", ".txt", ".md"],
    "cache_duration": 300,  # 5분
    "editor_heights": [300, 400, 500, 600, 700, 800],
    "font_sizes": [12, 14, 16, 18, 20]
}