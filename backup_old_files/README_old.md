# 🤖 AI 문서 작성 어시스턴트 (리팩토링 버전)

Azure OpenAI와 Streamlit을 활용한 지능형 문서 작성 지원 시스템

## ✨ 주요 기능

### 🤖 핵심 AI 기능
- **3단계 통합 분석**: 프롬프트 최적화 → 사내/외부 검색 → 종합 분석
- **사내 문서 검색**: Azure AI Search를 통한 기업 내부 자료 검색
- **외부 레퍼런스 검색**: Tavily API를 통한 실시간 웹 검색
- **텍스트 다듬기**: 명확성, 전문성, 간결성 개선
- **내용 구조화**: 목차, 단계별 가이드, Q&A 형식으로 변환

### � 문서 편집 기능
- **다중 문서 타입**: 새 문서, 템플릿, 파일 불러오기
- **실시간 통계**: 단어 수, 문자 수, 줄 수 표시
- **편집기 커스터마이징**: 높이 조절, 폰트 크기 변경
- **내보내기**: TXT 형식으로 다운로드

### 🎨 사용자 경험
- **모듈형 UI**: 문서 생성 → 편집 → AI 분석 단계별 인터페이스
- **토글형 AI 패널**: 필요시에만 표시되는 AI 도구
- **진행 상황 표시**: AI 분석 과정의 실시간 피드백
- **원클릭 삽입**: 분석 결과를 문서에 바로 적용

## 🏗️ 리팩토링된 시스템 구조

```
AzureProject/
├── app_refactored.py        # 새로운 메인 앱 (간소화)
├── app.py                   # 기존 메인 앱 (백업용)
├── config.py                # 정리된 설정 관리
├── state/                   # 상태 관리
│   └── session_state.py     # Streamlit 세션 상태 중앙 관리
├── ui/                      # UI 컴포넌트
│   ├── styles.py            # CSS 스타일 정의
│   ├── document_creation.py # 문서 생성 UI
│   ├── document_editor.py   # 문서 편집 UI
│   └── ai_sidebar.py        # AI 도구 사이드바
├── services/                # 비즈니스 로직
│   └── ai_analysis_service.py # AI 분석 프로세스 관리
├── utils/                   # 유틸리티
│   ├── ai_service.py        # 간소화된 AI 서비스
│   └── ai_service_backup.py # 기존 AI 서비스 (백업)
├── backup_old_files/        # 사용하지 않는 파일들
└── data/                    # 데이터 파일들
    ├── sample_documents.json
    └── keywords.json
```

## 🚀 설치 및 실행

### 1. 환경 설정

```bash
# 저장소 클론
git clone <repository-url>
cd AzureProject

# Python 가상환경 생성 및 활성화
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 또는 .venv\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 다음 정보를 입력하세요:

```env
# Azure OpenAI 설정
OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
OPENAI_API_KEY=your_openai_api_key
OPENAI_DEPLOYMENT_NAME=gpt-4o
OPENAI_API_VERSION=2024-12-01-preview

# Tavily 검색 API
TAVILY_API_KEY=your_tavily_api_key

# OnlyOffice 설정
ONLYOFFICE_API_KEY=your_onlyoffice_api_key
ONLYOFFICE_SERVER_URL=http://localhost:8000
```

### 3. 애플리케이션 실행

```bash
# 실행 스크립트 사용
chmod +x run.sh
./run.sh

# 또는 직접 실행
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 접속

## 🔧 API 키 발급 방법

### Azure OpenAI
1. [Azure Portal](https://portal.azure.com) 로그인
2. Azure OpenAI 리소스 생성
3. 키 및 엔드포인트 페이지에서 API 키 복사
4. 모델 배포 (gpt-4o 권장)

### Tavily Search API
1. [Tavily 웹사이트](https://tavily.com) 회원가입
2. API 키 발급
3. 무료 플랜: 월 1,000회 검색 제한

### OnlyOffice Document Server
1. [OnlyOffice](https://www.onlyoffice.com) 계정 생성
2. Document Server 설치 또는 클라우드 서비스 이용
3. API 키 및 서버 URL 설정

## 📋 사용 방법

### 1. 문서 편집
- 메인 편집 영역에서 텍스트 작성
- OnlyOffice 편집기로 전문적인 문서 작성 가능

### 2. AI 추천 활용
- **전체 문서 분석**: 상단 "🤖 AI 추천" 버튼 클릭
- **텍스트 선택 분석**: 텍스트 선택 후 "🎯 선택된 텍스트로 AI 추천" 버튼 클릭

### 3. 분석 결과 활용
- **문서 추천**: 관련 문서 및 참조 자료 확인
- **문장 다듬기**: 명확성, 전문성, 간결성 개선안 확인
- **구조화**: 목차, 단계별, Q&A 형식으로 변환

### 4. 내용 삽입
- 각 추천 결과에서 "📝 문서에 삽입" 버튼 클릭
- 3초간 노란색 하이라이트로 삽입된 내용 확인

## 🎨 UI 컬러 테마

- **주 배경색**: #ffffff
- **보조 배경색**: #f8f9fa
- **사이드바**: #fafafa
- **AI 액센트**: #8b5cf6 (보라색)
- **테두리**: #e5e7eb
- **텍스트**: #1f2937
- **보조 텍스트**: #6b7280

## 🔍 트러블슈팅

### 패키지 설치 오류
```bash
# 개별 설치 시도
pip install streamlit openai python-dotenv tavily-python azure-identity python-docx

# 또는 업그레이드
pip install --upgrade pip
pip install -r requirements.txt
```

### API 연결 오류
- `.env` 파일의 API 키와 엔드포인트 확인
- 네트워크 연결 상태 확인
- API 사용량 한도 확인

### OnlyOffice 연동 오류
- Document Server URL 접근 가능성 확인
- CORS 설정 확인
- JWT 토큰 설정 확인

## 🤝 기여 방법

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 확인하세요.

## 📞 지원

문의사항이나 버그 리포트는 GitHub Issues를 통해 제출해 주세요.

---

**Made with ❤️ by AI Document Assistant Team**