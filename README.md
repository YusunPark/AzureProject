# 🤖 AI 문서 작성 어시스턴트

Streamlit과 OnlyOffice를 활용한 지능형 문서 작성 지원 시스템

## ✨ 주요 기능

### 📝 OnlyOffice 통합
- Word, PowerPoint 문서 편집 지원
- 실시간 협업 기능
- 다양한 파일 형식 지원 (.docx, .pptx, .pdf, .txt)

### 🤖 AI 기능
- **텍스트 분석**: 선택된 텍스트의 키워드, 주제, 맥락 분석
- **문서 추천**: 관련 문서 및 참조 자료 추천
- **문장 다듬기**: 명확성, 전문성, 간결성 개선
- **내용 구조화**: 목차, 단계별 가이드, Q&A 형식으로 변환

### 🔍 검색 기능
- **전체 문서 기반 검색**: 문서 전체 내용을 바탕으로 AI 추천
- **선택된 텍스트 기반 검색**: 특정 텍스트 선택 후 맞춤 추천
- **Tavily 검색 엔진**: 실시간 웹 검색을 통한 최신 정보 제공

### 🎨 사용자 경험
- **단계별 분석 과정 시각화**: AI 작업 진행 상황 실시간 표시
- **토글형 결과 표시**: 핵심 내용 빠른 확인, 세부사항 펼쳐보기
- **원클릭 삽입**: 추천 내용을 문서에 바로 삽입
- **하이라이트 효과**: 삽입된 내용 3초간 노란색 강조

## 🏗️ 시스템 구조

```
AzureProject/
├── app.py                    # 메인 Streamlit 애플리케이션
├── config.py                 # 설정 관리
├── requirements.txt          # Python 의존성
├── .env                      # 환경 변수 (API 키 등)
├── run.sh                    # 실행 스크립트
├── utils/
│   ├── ai_service.py         # Azure OpenAI 연동 AI 서비스
│   └── document_service.py   # OnlyOffice 연동 문서 서비스
└── data/
    ├── sample_documents.json # 샘플 문서 데이터
    └── keywords.json         # 키워드 및 카테고리 정보
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