# AI 문서 작성 어시스턴트

https://appsvc-yusun-01.azurewebsites.net/


AI 기반의 스마트한 문서 작성, 학습, 관리 플랫폼입니다.

> 🚀 **최신 업데이트**: 전체 코드베이스가 리팩토링되어 더욱 안정적이고 확장 가능한 구조로 개선되었습니다!

## 🚀 새로운 주요 기능

### 📚 사내 문서 학습 시스템
- **다중 파일 업로드**: TXT, MD, DOCX, PDF, PY, JS, HTML, CSS, JSON, CSV 지원
- **Azure AI Search 연동**: 자동 인덱싱 및 벡터 검색
- **키워드 추출**: AI 기반 자동 키워드 생성
- **메타데이터 관리**: 카테고리, 부서, 태그 등 체계적 분류

### 📋 생성된 문서 관리
- **Azure Storage 연동**: 안전한 클라우드 저장
- **버전 관리**: 문서 편집 및 복사 기능
- **검색 및 필터링**: 제목, 내용 기반 검색
- **통계 및 분석**: 문서 현황 대시보드

### 🤖 강화된 AI 분석
- **3단계 분석 프로세스**: 프롬프트 최적화 → 다중 검색 → 통합 분석
- **사내 문서 기반 추천**: 학습된 문서를 활용한 맞춤형 제안
- **외부 레퍼런스 검색**: Tavily를 통한 실시간 웹 검색
- **다양한 분석 관점**: 여러 버전의 분석 결과 제공

### 🔍 통합 관리 시스템
- **홈 대시보드**: 전체 현황 한눈에 보기
- **서비스 상태 모니터링**: Azure 서비스 연결 상태 실시간 확인
- **사용자 친화적 UI**: 직관적인 네비게이션 및 작업 흐름

## 📊 시스템 아키텍처

```
Frontend (Streamlit)
    ↓
Document Management Service
    ↓
┌─────────────────┬─────────────────┐
│  Azure Storage  │ Azure AI Search │
│  (파일 저장)      │  (검색 인덱스)   │
└─────────────────┴─────────────────┘
    ↓
Azure OpenAI (AI 분석 및 임베딩)
```

## 🛠️ 기술 스택

- **Frontend**: Streamlit with Enhanced UI
- **AI Engine**: Azure OpenAI (GPT-4o + text-embedding-3-large)
- **Storage**: Azure Storage Account (Blob Storage)
- **Search**: Azure AI Search (REST API)
- **External Search**: Tavily API
- **Monitoring**: LangSmith (Optional)

## 📦 설치 및 실행

### 1. 필수 패키지 설치
```bash
pip install -r requirements.txt
```

### 2. Azure 리소스 설정
다음 Azure 서비스들이 필요합니다:
- Azure OpenAI Service
- Azure Storage Account
- Azure AI Search Service

### 3. 환경 변수 설정
`.env` 파일에 다음 설정을 추가하세요:

```bash
# Azure OpenAI
OPENAI_ENDPOINT=https://your-openai-endpoint.openai.azure.com/
OPENAI_API_KEY=your-api-key
OPENAI_DEPLOYMENT_NAME=gpt-4o
OPENAI_EMBEDDING_DEPLOYMENT_NAME=text-embedding-3-large
OPENAI_API_VERSION=2024-12-01-preview

# Azure Storage Account
AZURE_STORAGE_ACCOUNT_NAME=your-storage-account
AZURE_STORAGE_ACCOUNT_KEY=your-storage-key
AZURE_STORAGE_CONTAINER_NAME=documents
AZURE_STORAGE_BLOB_SERVICE_URL=https://your-account.blob.core.windows.net

# Azure AI Search
AZURE_SEARCH_ENDPOINT=https://your-search-service.search.windows.net
AZURE_SEARCH_ADMIN_KEY=your-search-admin-key
AZURE_SEARCH_API_KEY=your-search-api-key

# Tavily Search (Optional)
TAVILY_API_KEY=your-tavily-api-key

# LangSmith Monitoring (Optional)
LANGSMITH_API_KEY=your-langsmith-key
```

### 4. 애플리케이션 실행

#### 기존 버전 (호환성)
```bash
streamlit run app_enhanced.py
```

#### 🚀 리팩토링된 버전 (권장)
```bash
streamlit run app_refactored.py
# 또는
python main.py
```

> **새로운 기능**: 리팩토링된 버전은 더 안정적이고 확장 가능한 아키텍처를 제공합니다.

## 📖 사용 가이드

### 1. 사내 문서 학습
1. **📚 사내 문서 학습** 메뉴로 이동
2. **문서 업로드** 탭에서 파일 선택
3. 카테고리, 부서, 태그 등 메타데이터 입력
4. **업로드 및 학습 시작** 버튼 클릭

### 2. AI 문서 작성
1. **📝 문서 작성** 메뉴로 이동
2. 새 문서 생성 또는 템플릿 선택
3. 텍스트 입력 후 AI 분석 실행
4. AI 제안사항 검토 및 적용
5. **저장** 버튼으로 Azure Storage에 저장

### 3. 문서 관리
1. **📋 문서 관리** 메뉴로 이동
2. 생성된 문서 목록 확인
3. 편집, 복사, 다운로드, 삭제 등 관리 작업
4. 통계 탭에서 현황 분석

## 🔧 고급 설정

### Azure AI Search 인덱스 설정
시스템이 자동으로 `company-documents` 인덱스를 생성합니다. 필요시 수동 설정 가능:

```python
# utils/simple_azure_search.py에서 인덱스명 변경
self.index_name = "your-custom-index-name"
```

### 파일 업로드 제한
`config.py`에서 설정 변경 가능:

```python
APP_CONFIG = {
    "max_upload_size": 10 * 1024 * 1024,  # 10MB
    "supported_formats": [".docx", ".pdf", ".txt", ".md", "..."]
}
```

## 🚀 배포

### Azure App Service 배포
```bash
# Azure CLI를 통한 배포
az webapp up --sku F1 --name your-app-name --resource-group your-rg
```

### Docker 배포
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app_enhanced.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

## 🔍 문제 해결

### Azure Search 연결 오류
- Azure AI Search 서비스가 실행 중인지 확인
- API 키와 엔드포인트 URL 검증
- 방화벽 설정 확인

### Azure Storage 업로드 오류  
- Storage Account 접근 권한 확인
- 컨테이너 존재 여부 확인
- 네트워크 연결 상태 점검

### AI 분석 실패
- Azure OpenAI 배포 상태 확인
- API 할당량 및 요금 한도 점검
- 모델 배포명 정확성 확인

## 📝 라이선스

MIT License

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 지원

문의사항이나 버그 리포트는 GitHub Issues를 통해 제출해 주세요.

---

**⚡ 고도화된 AI 문서 어시스턴트로 더욱 스마트한 문서 작업을 경험하세요!**
