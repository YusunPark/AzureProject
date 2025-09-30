# 🤖 AI 문서 작성 어시스턴트 - 프로젝트 구조 및 기능 설명서

## 📋 프로젝트 개요

**AI 문서 작성 어시스턴트**는 Azure OpenAI, Azure AI Search, Azure Storage를 활용한 고도화된 문서 작성 및 분석 플랫폼입니다. 사용자가 효율적으로 문서를 작성하고 AI 기반 분석을 통해 내용을 개선할 수 있도록 돕는 종합적인 솔루션을 제공합니다.

### 🎯 핵심 기능

- **4단계 순차 AI 분석**: 프롬프트 고도화 → 검색 쿼리 생성 → 참고 자료 검색 → 최종 분석
- **실시간 문서 편집**: 다중 편집기 지원 및 동기화
- **참고 자료 통합**: 사내 문서(Azure AI Search) + 외부 자료(Tavily API) 동시 검색
- **문서 관리 시스템**: 문서 업로드, 저장, 버전 관리
- **150자 미리보기**: 분석 결과 요약 제공 및 전체 내용 팝업
- **세로 레이아웃 참고자료**: 사내문서(상) → 외부자료(하) 구성

## 📁 프로젝트 구조

```
AzureProject/
├── 📱 Core Application
│   ├── app_enhanced.py              # 메인 애플리케이션 (Streamlit)
│   ├── config.py                    # 설정 관리 (Azure 서비스 연결)
│   └── requirements.txt             # Python 패키지 의존성
│
├── 🧠 Services (핵심 비즈니스 로직)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai_analysis_service.py           # 기본 AI 분석 서비스
│   │   ├── enhanced_ai_analysis_service.py  # 4단계 고도화 분석 서비스 ⭐
│   │   └── document_management_service.py   # 문서 관리 서비스
│
├── 🎨 User Interface
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── ai_sidebar.py           # AI 분석 사이드바 (4단계 분석 UI) ⭐
│   │   ├── document_creation.py    # 문서 작성 인터페이스 ⭐
│   │   ├── document_editor.py      # 문서 편집기
│   │   ├── document_upload.py      # 문서 업로드 UI
│   │   ├── generated_documents.py  # 생성된 문서 관리 UI
│   │   ├── styles.py              # CSS 스타일 정의
│   │   └── text_selection.py      # 텍스트 선택 기능
│
├── 🔧 Utilities (유틸리티 및 서비스 연결)
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── ai_service.py               # Azure OpenAI 연결 서비스 ⭐
│   │   ├── azure_search_management.py  # Azure AI Search 관리
│   │   ├── azure_search_setup.py       # Azure AI Search 초기 설정
│   │   ├── azure_storage_service.py    # Azure Storage 연결 서비스
│   │   └── simple_azure_search.py      # 간단한 검색 인터페이스
│
├── 💾 State Management
│   ├── state/
│   │   ├── __init__.py
│   │   └── session_state.py        # Streamlit 세션 상태 관리
│
├── 📊 Data
│   ├── data/
│   │   ├── keywords.json           # 키워드 데이터
│   │   └── sample_documents.json   # 샘플 문서 데이터
│
├── 📚 Documentation
│   ├── docs/
│   │   └── storage_structure.md    # 저장소 구조 설명
│   ├── demo_docs/                  # 데모 문서들
│   └── README.md                   # 프로젝트 README
│
├── 🗂️ Configuration & Environment
│   ├── .env                       # 환경 변수 (로컬)
│   ├── .env.azure                 # Azure 환경 변수
│   ├── .streamlit/               # Streamlit 설정
│   ├── .github/                  # GitHub Actions
│   └── .vscode/                  # VS Code 설정
│
└── 📦 Archive
    └── backup_old_files/          # 사용하지 않는 백업 파일들
```

## 🚀 핵심 기능 상세 설명

### 1. 📝 4단계 순차 AI 분석 시스템 ⭐

**위치**: `services/enhanced_ai_analysis_service.py`

#### 분석 단계:
1. **🔧 Step 1: 프롬프트 고도화**
   - 사용자 입력을 AI가 분석하기 적합한 형태로 개선
   - 맥락 정보 추가 및 분석 방향 설정

2. **🔍 Step 2: 검색 쿼리 생성**
   - 고도화된 프롬프트에서 핵심 키워드 추출
   - 사내 검색용/외부 검색용 쿼리 분리 생성

3. **📚 Step 3: 병렬 참고 자료 검색**
   - **사내 문서**: Azure AI Search로 기업 내부 문서 검색
   - **외부 자료**: Tavily API로 인터넷 레퍼런스 검색
   - 두 검색을 동시 실행하여 시간 단축

4. **🎯 Step 4: 최종 분석 생성**
   - 수집된 모든 자료를 종합하여 최종 분석 결과 생성
   - 150자 미리보기 + 전체 내용 제공

### 2. 🎨 사용자 인터페이스 시스템

#### A. 메인 문서 작성 (`ui/document_creation.py`)
- **상단 AI 분석 버튼**: "전체분석하기", "선택내용 분석하기", "고급 분석 설정"
- **문서 편집 영역**: 실시간 동기화되는 텍스트 에디터
- **텍스트 선택 영역**: 부분 분석을 위한 별도 입력창
- **빠른 통계**: 단어수, 글자수 실시간 표시
- **문서 관리**: 저장, 내보내기, 템플릿, 새로시작

#### B. AI 분석 사이드바 (`ui/ai_sidebar.py`)
- **분석 모드 표시**: 전체문서/선택텍스트/수동 모드 구분
- **진행 상황 표시**: 4단계 분석 진행률 시각화
- **결과 탭 구성**:
  - 🎯 **최종 분석**: 150자 미리보기 + 전체보기 버튼
  - 📋 **단계별 결과**: 각 단계별 세부 결과
  - 📚 **참고 자료**: 세로 배치 (사내문서 → 외부자료)
  - 💡 **추천 액션**: 체크리스트, 테이블, 질문, 개선방안 생성

#### C. 문서 관리 시스템 (`ui/generated_documents.py`)
- 생성된 문서 목록 및 관리
- 문서 검색, 필터링, 정렬 기능
- 문서 통계 및 분석 현황

### 3. 🔗 Azure 서비스 통합

#### A. Azure OpenAI (`utils/ai_service.py`)
- **모델**: GPT-4 기반 텍스트 분석 및 생성
- **기능**: 프롬프트 고도화, 분석 결과 생성, 추가 분석 요청
- **캐싱**: 동일 요청에 대한 응답 캐시로 성능 최적화

#### B. Azure AI Search (`utils/azure_search_management.py`)
- **사내 문서 검색**: 기업 내부 문서 및 정책 검색
- **벡터 검색**: 의미 기반 유사 문서 검색
- **하이브리드 검색**: 키워드 + 벡터 검색 조합

#### C. Azure Storage (`utils/azure_storage_service.py`)
- **문서 저장**: 생성된 문서 및 업로드 파일 저장
- **버전 관리**: 문서 변경 이력 추적
- **메타데이터**: 문서 분류 및 태깅

### 4. 📊 상태 관리 시스템

#### 세션 상태 (`state/session_state.py`)
```python
# 주요 상태 변수들
- document_content: 현재 편집 중인 문서 내용
- selected_text: 선택된 텍스트 (부분 분석용)
- ai_panel_open: AI 분석 패널 열림 여부
- analysis_mode: 분석 모드 (full_document/selected_text/manual)
- analysis_text: 현재 분석 대상 텍스트
- analysis_in_progress: 분석 진행 중 여부
- enhanced_analysis_results: 4단계 분석 결과
- analysis_completed: 분석 완료 여부
```

## 🔧 주요 개선사항 (리팩토링 결과)

### ✅ 제거된 중복 코드
1. **중복 앱 파일 정리**: `app.py`, `app_refactored.py` → `backup_old_files/`
2. **백업 파일 정리**: 모든 `*_backup.py` 파일들을 백업 디렉토리로 이동
3. **사용하지 않는 유틸리티**: `document_service.py`, `ai_service_backup.py` 제거
4. **임시 설정 파일**: 배포 관련 스크립트들을 백업으로 이동

### ✅ 키 중복 문제 해결
- Streamlit 요소의 중복 키 문제 해결
- 각 편집기별 고유 키 할당:
  - `document_content_main_editor` (document_creation.py)
  - `document_editor_main_content` (document_editor.py)  
  - `app_enhanced_main_editor` (app_enhanced.py)

### ✅ 코드 구조 개선
- 기능별 모듈 분리 명확화
- 사용하지 않는 import 제거
- 일관된 네이밍 컨벤션 적용

## 🚀 사용법

### 환경 설정
1. **Azure 서비스 설정**:
   ```bash
   # .env 파일 설정
   AZURE_OPENAI_API_KEY=your_key
   AZURE_OPENAI_ENDPOINT=your_endpoint
   AZURE_SEARCH_SERVICE_NAME=your_search_service
   AZURE_SEARCH_API_KEY=your_search_key
   AZURE_STORAGE_CONNECTION_STRING=your_storage_string
   TAVILY_API_KEY=your_tavily_key
   ```

2. **의존성 설치**:
   ```bash
   pip install -r requirements.txt
   ```

3. **앱 실행**:
   ```bash
   streamlit run app_enhanced.py --server.port=8503
   ```

### 기본 워크플로우
1. **문서 작성**: 메인 편집기에 내용 입력
2. **AI 분석 시작**: "전체분석하기" 또는 "선택내용 분석하기" 클릭
3. **결과 확인**: 우측 사이드바에서 4단계 분석 결과 검토
4. **내용 삽입**: 분석 결과를 문서에 삽입 (요약/전체)
5. **문서 저장**: 완성된 문서를 저장 및 관리

## 📈 성능 최적화

- **캐싱 시스템**: AI 응답 및 검색 결과 캐시
- **병렬 처리**: 사내/외부 검색 동시 실행
- **청크 처리**: 대용량 문서의 분할 처리
- **세션 관리**: 효율적인 상태 관리 및 메모리 사용

## 🔧 기술 스택

- **프론트엔드**: Streamlit
- **AI 서비스**: Azure OpenAI (GPT-4)
- **검색 엔진**: Azure AI Search
- **저장소**: Azure Blob Storage
- **외부 검색**: Tavily API
- **언어**: Python 3.11+
- **배포**: Azure App Service

## 📝 라이센스 및 기여

이 프로젝트는 기업 내부 문서 작성 효율성 향상을 목적으로 개발되었습니다. 
추가 기능 요청이나 버그 리포트는 GitHub Issues를 통해 제출해 주세요.

---

**최종 업데이트**: 2025년 9월 30일  
**버전**: v2.0 (Enhanced & Refactored)  
**주요 개선**: 4단계 순차 분석, 중복 코드 제거, UI/UX 개선