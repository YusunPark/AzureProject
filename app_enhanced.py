# app_enhanced.py
import streamlit as st
import time
import json
import random
from datetime import datetime
from typing import Dict, List, Any

# 필요한 서비스들 import
from utils.ai_service import AIService
from services.document_management_service import DocumentManagementService
from ui.document_upload import render_document_upload_page
from ui.generated_documents import render_generated_documents_page

# 페이지 설정
st.set_page_config(
    page_title="AI 문서 작성 어시스턴트 - 고도화",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일 정의
def load_css():
    st.markdown("""
    <style>
    /* 전체 배경 및 기본 색상 */
    .main {
        background-color: #ffffff;
    }
    
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
    }
    
    /* 사이드바 스타일 */
    .ai-sidebar {
        background-color: #fafafa;
        border-left: 1px solid #e5e7eb;
        padding: 20px;
        height: 100vh;
        overflow-y: auto;
    }
    
    /* AI 액센트 색상 */
    .ai-accent {
        color: #8b5cf6;
        font-weight: 600;
    }
    
    .ai-background {
        background-color: #f3f4f6;
    }
    
    /* 버튼 스타일 */
    .stButton > button {
        background-color: #8b5cf6;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    
    .stButton > button:hover {
        background-color: #7c3aed;
    }
    
    /* 네비게이션 스타일 */
    .nav-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 20px;
        color: white;
        text-align: center;
        margin: 10px 0;
        cursor: pointer;
        transition: transform 0.2s;
    }
    
    .nav-card:hover {
        transform: translateY(-2px);
    }
    
    .nav-card h3 {
        margin: 0;
        font-size: 1.2rem;
    }
    
    .nav-card p {
        margin: 5px 0 0 0;
        opacity: 0.9;
        font-size: 0.9rem;
    }
    
    /* 상태 표시 */
    .status-card {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
    
    .status-good { border-left: 4px solid #28a745; }
    .status-warning { border-left: 4px solid #ffc107; }
    .status-error { border-left: 4px solid #dc3545; }
    
    /* 문서 카드 */
    .doc-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .doc-title {
        font-weight: 600;
        color: #1f2937;
        margin-bottom: 8px;
    }
    
    .doc-summary {
        color: #6b7280;
        font-size: 14px;
        margin-bottom: 8px;
    }
    
    .doc-source {
        color: #8b5cf6;
        font-size: 12px;
        font-style: italic;
    }
    
    /* 편집기 스타일 */
    .stTextArea textarea {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1.6;
        border-radius: 8px;
        border: 1px solid #e5e7eb;
    }
    
    /* 통계 카드 스타일 */
    .metric-card {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 12px;
        margin: 4px 0;
        text-align: center;
    }
    
    .metric-value {
        font-size: 1.5rem;
        font-weight: bold;
        color: #8b5cf6;
    }
    
    .metric-label {
        font-size: 0.8rem;
        color: #6c757d;
        margin-top: 4px;
    }
    </style>
    """, unsafe_allow_html=True)

# 더미 데이터 생성
def generate_dummy_data():
    return {
        "documents": [
            {
                "id": 1,
                "title": "AI와 머신러닝의 미래 전망",
                "summary": "인공지능 기술의 발전 방향과 산업에 미치는 영향에 대한 종합적 분석",
                "content": "인공지능 기술은 빠르게 발전하고 있으며, 특히 대규모 언어 모델과 생성형 AI의 등장으로...",
                "source": "AI Research Journal, 2024",
                "relevance_score": 0.95,
                "keywords": ["AI", "머신러닝", "미래", "기술"]
            },
            {
                "id": 2,
                "title": "디지털 트랜스포메이션 가이드",
                "summary": "기업의 디지털 전환 과정에서 고려해야 할 핵심 요소들",
                "content": "디지털 트랜스포메이션은 단순한 기술 도입이 아니라 조직 문화의 변화를 포함하는...",
                "source": "Business Innovation Review, 2024",
                "relevance_score": 0.88,
                "keywords": ["디지털", "혁신", "비즈니스", "전환"]
            },
            {
                "id": 3,
                "title": "효과적인 문서 작성 방법론",
                "summary": "명확하고 설득력 있는 문서 작성을 위한 실용적 가이드",
                "content": "좋은 문서는 명확한 구조와 논리적 흐름을 가져야 합니다. 먼저 목적을 명확히 하고...",
                "source": "Writing Excellence Handbook, 2023",
                "relevance_score": 0.82,
                "keywords": ["문서작성", "커뮤니케이션", "구조화", "방법론"]
            }
        ]
    }

# 세션 상태 초기화
def init_session_state():
    if 'main_view' not in st.session_state:
        st.session_state.main_view = "home"
    if 'ai_panel_open' not in st.session_state:
        st.session_state.ai_panel_open = False
    if 'selected_text' not in st.session_state:
        st.session_state.selected_text = ""
    if 'document_content' not in st.session_state:
        st.session_state.document_content = ""
    if 'analysis_state' not in st.session_state:
        st.session_state.analysis_state = 'idle'
    if 'dummy_data' not in st.session_state:
        st.session_state.dummy_data = generate_dummy_data()
    if 'search_results' not in st.session_state:
        st.session_state.search_results = []
    if 'current_view' not in st.session_state:
        st.session_state.current_view = "create"
    if 'current_document' not in st.session_state:
        st.session_state.current_document = None
    if 'ai_results' not in st.session_state:
        st.session_state.ai_results = {}
    
    # 문서 관리 서비스 초기화
    if 'doc_manager' not in st.session_state:
        st.session_state.doc_manager = DocumentManagementService()
    if 'doc_manager' not in st.session_state:
        st.session_state.doc_manager = DocumentManagementService()

# 홈 페이지 렌더링
def render_home_page():
    """메인 홈 페이지"""
    st.markdown("# 🚀 AI 문서 작성 어시스턴트")
    st.markdown("---")
    
    # 환영 메시지
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### 👋 환영합니다!
        
        이 플랫폼에서 다음 기능들을 사용할 수 있습니다:
        - 📚 **사내 문서 학습**: 회사 문서를 업로드하여 AI가 학습하도록 합니다
        - 📝 **AI 문서 작성**: 학습된 지식을 바탕으로 문서를 작성합니다  
        - 📋 **문서 관리**: 생성된 문서들을 체계적으로 관리합니다
        - 🔍 **스마트 검색**: AI 기반으로 관련 문서를 찾아줍니다
        """)
    
    with col2:
        # 시스템 상태 표시
        render_system_status()
    
    st.markdown("---")
    
    # 주요 기능 카드들
    st.markdown("### 🎯 주요 기능")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📚 사내 문서 학습", use_container_width=True, type="primary", key="home_training"):
            with st.spinner("페이지 로딩 중..."):
                st.session_state.main_view = "training_upload"
                time.sleep(0.1)  # 상태 업데이트 시간 확보
            st.rerun()
        
        st.markdown("""
        <div class="status-card">
        <strong>문서 학습 기능</strong><br>
        • 다양한 형식의 문서 업로드<br>
        • Azure AI Search 자동 인덱싱<br>
        • 키워드 및 내용 기반 검색
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.button("📝 새 문서 작성", use_container_width=True, type="primary", key="home_create"):
            with st.spinner("페이지 로딩 중..."):
                st.session_state.main_view = "document_create"
                st.session_state.current_view = "create"
                st.session_state.ai_panel_open = False  # AI 패널 초기화
                time.sleep(0.1)
            st.rerun()
        
        st.markdown("""
        <div class="status-card">
        <strong>AI 문서 작성</strong><br>
        • 실시간 AI 도움말<br>
        • 사내 문서 기반 추천<br>
        • 문장 다듬기 및 구조화
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if st.button("📋 문서 관리", use_container_width=True, type="primary", key="home_manage"):
            with st.spinner("페이지 로딩 중..."):
                st.session_state.main_view = "document_manage"
                time.sleep(0.1)
            st.rerun()
        
        st.markdown("""
        <div class="status-card">
        <strong>문서 관리</strong><br>
        • 생성된 문서 목록<br>
        • 편집 및 버전 관리<br>
        • Azure Storage 연동 저장
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 최근 활동 및 통계
    render_recent_activity()

def render_system_status():
    """시스템 상태 표시"""
    st.markdown("#### 🔍 시스템 상태")
    
    # 문서 관리 서비스 테스트
    doc_manager = st.session_state.doc_manager
    test_results = doc_manager.test_services()
    
    # Azure Storage 상태
    if test_results["storage_service"]["available"]:
        st.markdown('<div class="status-card status-good">✅ Azure Storage 연결됨</div>', 
                   unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-card status-error">❌ Azure Storage 연결 실패</div>', 
                   unsafe_allow_html=True)
    
    # Azure AI Search 상태
    if test_results["search_service"]["available"]:
        st.markdown('<div class="status-card status-good">✅ Azure AI Search 연결됨</div>', 
                   unsafe_allow_html=True)
        if test_results["search_service"]["has_embedding"]:
            st.markdown('<div class="status-card status-good">🧠 벡터 검색 지원</div>', 
                       unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-card status-warning">⚠️ Azure AI Search 연결 실패</div>', 
                   unsafe_allow_html=True)

def render_recent_activity():
    """최근 활동 표시"""
    st.markdown("### 📊 최근 활동")
    
    doc_manager = st.session_state.doc_manager
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📚 학습된 문서")
        training_docs = doc_manager.list_training_documents()
        
        if training_docs:
            st.metric("총 문서 수", len(training_docs))
            
            # 최근 3개 문서 표시
            for doc in training_docs[:3]:
                st.markdown(f"• {doc['title']}")
        else:
            st.info("아직 학습된 문서가 없습니다.")
            if st.button("📤 첫 문서 업로드하기"):
                st.session_state.main_view = "training_upload"
                st.rerun()
    
    with col2:
        st.markdown("#### 📄 생성된 문서")
        generated_docs = doc_manager.list_generated_documents()
        
        if generated_docs:
            st.metric("총 문서 수", len(generated_docs))
            
            # 최근 3개 문서 표시
            for doc in generated_docs[:3]:
                st.markdown(f"• {doc['title']}")
        else:
            st.info("아직 생성된 문서가 없습니다.")
            if st.button("📝 첫 문서 작성하기"):
                st.session_state.main_view = "document_create"
                st.session_state.current_view = "create"
                st.rerun()

# 강화된 AI 분석 프로세스 실행
def run_enhanced_analysis_process(user_input: str):
    """
    개선된 동기적 3단계 AI 분석 프로세스 (API 호출 최적화)
    1. 프롬프트 재생성 (사용자 의도 파악)
    2. 병렬 검색 (사내 문서 + 외부 레퍼런스)
    3. 통합 분석 결과 생성 (단일 API 호출)
    """
    
    # 중복 실행 방지 - 동일한 입력에 대해서는 캐시된 결과 사용
    input_hash = str(hash(user_input))
    if st.session_state.get('last_analysis_hash') == input_hash:
        st.info("이미 분석된 내용입니다. 기존 결과를 표시합니다.")
        return
    
    try:
        st.session_state.last_analysis_hash = input_hash
        # 전체 진행 상황 표시
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # AI 서비스 초기화
        status_text.text("🔧 AI 서비스 초기화 중...")
        ai_service = AIService()
        progress_bar.progress(10)
        
        # 1단계: 사용자 의도 파악 및 프롬프트 재생성
        st.markdown("### 🔄 1단계: 사용자 의도 분석 및 프롬프트 최적화")
        status_text.text("🧠 사용자 의도 분석 중...")
        
        with st.spinner("사용자 의도를 분석하고 AI가 더 잘 이해할 수 있도록 프롬프트를 재생성하고 있습니다..."):
            enhanced_prompt = ai_service.enhance_user_prompt(user_input)
            st.session_state.enhanced_prompt = enhanced_prompt
        
        progress_bar.progress(30)
        st.success("✅ 1단계 완료: 프롬프트 재생성")
        
        with st.expander("🔍 재생성된 프롬프트 확인"):
            st.markdown(f"**원본 입력:**\n{user_input}")
            st.markdown(f"**AI 최적화 프롬프트:**\n{enhanced_prompt}")
        
        # 2단계: 순차적 검색 수행 (동기적 실행)
        st.markdown("### 🔄 2단계: 다중 소스 검색")
        
        # 2-1단계: 사내 문서 RAG 검색
        st.markdown("#### 📁 2-1. 사내 문서 검색 (Azure AI Search)")
        status_text.text("📚 사내 문서 검색 중...")
        
        doc_manager = st.session_state.doc_manager
        
        with st.spinner("사내 문서 데이터베이스에서 관련 자료를 검색하고 있습니다..."):
            # 사내 문서 검색 (통합 검색 서비스 사용)
            internal_docs = doc_manager.search_training_documents(enhanced_prompt, top=5)
            st.session_state.internal_search_results = internal_docs
        
        progress_bar.progress(50)
        st.success(f"✅ 2-1단계 완료: 사내 문서 {len(internal_docs)}개 발견")
        
        # 2-2단계: 사외 인터넷 검색
        st.markdown("#### 🌐 2-2. 외부 레퍼런스 검색 (Tavily)")
        status_text.text("🌍 외부 레퍼런스 검색 중...")
        
        with st.spinner("인터넷에서 유사 사례와 레퍼런스를 검색하고 있습니다..."):
            external_docs = ai_service.search_external_references(enhanced_prompt)
            st.session_state.external_search_results = external_docs
        
        progress_bar.progress(70)
        st.success(f"✅ 2-2단계 완료: 외부 참조 {len(external_docs)}개 발견")
        
        # 3단계: 통합 분석 결과 생성 (단일 API 호출로 최적화)
        st.markdown("### 🔄 3단계: 통합 분석 결과 생성")
        status_text.text("🤖 AI 분석 결과 생성 중...")
        
        with st.spinner("검색 결과를 바탕으로 통합 분석 결과를 생성하고 있습니다..."):
            # 기존 4번의 API 호출을 1번으로 최적화
            analysis_result = ai_service.generate_optimized_analysis(
                enhanced_prompt, 
                convert_docs_for_ai(internal_docs), 
                external_docs,
                user_input
            )
            st.session_state.analysis_result = analysis_result
        
        progress_bar.progress(100)
        status_text.text("✅ 모든 단계 완료!")
        
        st.success("✅ 3단계 완료: 통합 분석 결과 생성")
        
        # 결과 표시
        st.markdown("#### 🎯 AI 분석 결과")
        st.markdown(analysis_result.get('content', '분석 결과를 생성하지 못했습니다.'))
        
        # 검색 결과 요약 표시
        if internal_docs or external_docs:
            with st.expander("📊 검색 결과 요약"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**📁 사내 문서 결과**")
                    for i, doc in enumerate(internal_docs[:3], 1):
                        st.markdown(f"{i}. {doc.get('title', 'N/A')}")
                
                with col2:
                    st.markdown("**🌐 외부 레퍼런스**")
                    for i, doc in enumerate(external_docs[:3], 1):
                        st.markdown(f"{i}. {doc.get('title', 'N/A')}")
            
    except Exception as e:
        st.error(f"분석 프로세스 중 오류 발생: {str(e)}")
        progress_bar.progress(0)
        status_text.text("❌ 오류 발생")

def convert_docs_for_ai(docs: List[Dict]) -> List[Dict]:
    """문서 관리 서비스의 문서 형식을 AI 서비스 형식으로 변환"""
    converted_docs = []
    for doc in docs:
        converted_doc = {
            "id": doc.get("file_id", "unknown"),
            "title": doc.get("title", "제목 없음"),
            "content": doc.get("content", ""),
            "summary": doc.get("summary", ""),
            "source_detail": f"사내 문서 - {doc.get('filename', 'Unknown')}",
            "relevance_score": doc.get("search_score", 0.5) / 10 if doc.get("search_score") else 0.5,
            "search_type": "company_docs"
        }
        converted_docs.append(converted_doc)
    return converted_docs

# AI 사이드바 패널
def render_ai_sidebar():
    if not st.session_state.ai_panel_open:
        return
    
    st.markdown("## 🤖 AI 문서 어시스턴트")
    
    # 검색 모드 선택
    search_mode = st.radio(
        "검색 모드 선택:",
        ["전체 문서 기반", "선택된 텍스트 기반"],
        key="search_mode"
    )
    
    if search_mode == "선택된 텍스트 기반" and st.session_state.selected_text:
        st.markdown(f"**선택된 텍스트:**")
        st.markdown(f"```\n{st.session_state.selected_text}\n```")
    
    # AI 분석 시작 버튼
    if st.button("🚀 AI 분석 시작"):
        # 분석 중복 실행 방지
        if st.session_state.get('analysis_state') != 'analyzing':
            st.session_state.analysis_state = 'analyzing'
            
            # 실제 AI 분석 프로세스 실행
            search_query = st.session_state.selected_text if search_mode == "선택된 텍스트 기반" else st.session_state.document_content
            
            if search_query and search_query.strip():
                st.success("✅ 분석을 시작합니다...")
                run_enhanced_analysis_process(search_query.strip())
            else:
                st.error("❌ 분석할 내용이 없습니다. 문서에 내용을 입력하거나 텍스트를 선택해주세요.")
            
            st.session_state.analysis_state = 'completed'

# 문서 생성 인터페이스
def render_document_creation():
    """문서 생성 인터페이스 렌더링"""
    st.markdown("## 📝 AI 문서 작성 어시스턴트")
    st.markdown("---")
    
    # 상태 체크
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 새로운 문서를 시작하세요")
        st.markdown("텍스트 편집기에서 문서를 작성하고 AI 도구로 내용을 개선하세요.")
    
    with col2:
        st.markdown("#### 📊 문서 통계")
        if hasattr(st.session_state, 'document_content') and st.session_state.document_content:
            content = st.session_state.document_content.strip()
            if content:
                words = len(content.split())
                chars = len(content)
                lines = len(content.split('\n'))
                st.metric("단어 수", f"{words:,}")
                st.metric("문자 수", f"{chars:,}")
                st.metric("줄 수", f"{lines:,}")
            else:
                st.info("문서를 작성하면 통계가 표시됩니다.")
        else:
            st.info("문서를 작성하면 통계가 표시됩니다.")
    
    st.markdown("---")
    
    # 문서 생성 버튼들
    st.markdown("### 새 문서 생성")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 새 문서", key="create_text", use_container_width=True):
            doc_id = f"new_text_{int(time.time())}"
            st.session_state.current_document = {
                'id': doc_id,
                'type': 'text',
                'title': '새 문서'
            }
            st.session_state.document_content = ""
            st.session_state.current_view = "editor"
            st.rerun()
    
    with col2:
        if st.button("📋 템플릿 문서", key="create_template", use_container_width=True):
            doc_id = f"template_{int(time.time())}"
            st.session_state.current_document = {
                'id': doc_id,
                'type': 'template',
                'title': '템플릿 문서'
            }
            st.session_state.document_content = """# 제목

## 개요
이 문서의 목적과 개요를 작성하세요.

## 주요 내용

### 섹션 1
내용을 작성하세요.

### 섹션 2
내용을 작성하세요.

## 결론
결론을 작성하세요.
"""
            st.session_state.current_view = "editor"
            st.rerun()
    
    with col3:
        if st.button("📥 불러오기", key="load_document", use_container_width=True):
            st.session_state.show_file_upload = True

# 텍스트 편집기 렌더링
def render_document_editor():
    """텍스트 편집기 렌더링"""
    doc = st.session_state.current_document
    if not doc:
        st.error("문서 정보가 없습니다.")
        if st.button("← 문서 생성으로 돌아가기"):
            st.session_state.current_view = "create"
            st.rerun()
        return
    
    # 헤더
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"## {doc['title']}")
        st.caption(f"문서 ID: {doc['id']} | 타입: {doc['type'].upper()}")
    
    with col2:
        if st.button("🏠 새 문서 생성", use_container_width=True):
            st.session_state.current_view = "create"
            st.session_state.current_document = None
            st.rerun()
    
    with col3:
        if st.button("🤖 AI 패널 토글", use_container_width=True):
            st.session_state.ai_panel_open = not st.session_state.ai_panel_open
    
    st.markdown("---")
    
    # 툴바
    toolbar_col1, toolbar_col2, toolbar_col3, toolbar_col4 = st.columns(4)
    
    with toolbar_col1:
        if st.button("💾 저장", use_container_width=True):
            save_document_to_storage()
    
    with toolbar_col2:
        if st.button("📤 내보내기", use_container_width=True):
            # 문서 내용을 다운로드 링크로 제공
            if st.session_state.document_content:
                content = st.session_state.document_content
                st.download_button(
                    label="💾 TXT 다운로드",
                    data=content,
                    file_name=f"{doc['title']}.txt",
                    mime="text/plain"
                )
    
    with toolbar_col3:
        editor_height = st.selectbox("편집기 높이", [300, 400, 500, 600, 700, 800], index=3, key="editor_height")
    
    with toolbar_col4:
        font_size = st.selectbox("글꼴 크기", [12, 14, 16, 18, 20], index=1, key="font_size")
    
    # 텍스트 분석 영역
    if not st.session_state.ai_panel_open:
        st.markdown("---")
        analysis_col1, analysis_col2 = st.columns([3, 1])
        
        with analysis_col1:
            st.markdown("#### 🎯 AI 분석할 텍스트 선택")
            selected_text = st.text_input(
                "분석하고 싶은 텍스트를 입력하세요:",
                placeholder="문서에서 분석할 부분을 여기에 입력하세요...",
                help="입력한 텍스트를 AI가 분석하여 맞춤형 결과를 제공합니다.",
                key="analysis_text_input"
            )
            
            if selected_text != st.session_state.selected_text:
                st.session_state.selected_text = selected_text
        
        with analysis_col2:
            st.markdown("#### 🚀 AI 분석")
            if st.button("🤖 AI 분석 시작", use_container_width=True, type="primary"):
                if selected_text and selected_text.strip():
                    st.session_state.ai_panel_open = True
                    st.session_state.analysis_state = 'analyzing'
                    st.rerun()
                else:
                    st.warning("분석할 텍스트를 먼저 입력하세요")
    
    # 메인 텍스트 편집기
    st.markdown("#### 📝 문서 편집")
    
    # CSS 스타일 적용
    st.markdown(f"""
    <style>
    .stTextArea textarea {{
        font-size: {font_size}px !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1.6;
    }}
    </style>
    """, unsafe_allow_html=True)
    
    # 문서 내용 편집
    document_content = st.text_area(
        "문서 내용:",
        value=st.session_state.get('document_content', ''),
        height=editor_height,
        key="main_document_editor",
        help="여기에 문서 내용을 작성하세요. AI 패널을 열어 도움을 받을 수 있습니다.",
        placeholder="여기에 문서 내용을 입력하세요..."
    )
    
    # 문서 내용 업데이트
    if document_content != st.session_state.get('document_content', ''):
        st.session_state.document_content = document_content

def save_document_to_storage():
    """문서를 Azure Storage에 저장"""
    if not st.session_state.document_content.strip():
        st.warning("저장할 내용이 없습니다.")
        return
    
    doc_manager = st.session_state.doc_manager
    doc = st.session_state.current_document
    
    with st.spinner("문서를 저장하는 중..."):
        result = doc_manager.save_generated_document(
            content=st.session_state.document_content,
            title=doc['title'],
            document_id=doc['id'],
            metadata={
                "document_type": doc['type'],
                "editor_version": "enhanced_v1"
            }
        )
    
    if result['success']:
        st.success(f"✅ '{doc['title']}' 문서가 저장되었습니다!")
    else:
        st.error(f"❌ 저장 실패: {', '.join(result['errors'])}")

# 네비게이션 사이드바
def render_navigation():
    """네비게이션 사이드바"""
    st.sidebar.markdown("# 🚀 AI 문서 어시스턴트")
    st.sidebar.markdown("---")
    
    # 메인 메뉴
    menu_options = {
        "🏠 홈": "home",
        "📚 사내 문서 학습": "training_upload", 
        "📝 문서 작성": "document_create",
        "📋 문서 관리": "document_manage"
    }
    
    for label, view in menu_options.items():
        if st.sidebar.button(label, use_container_width=True, 
                           type="primary" if st.session_state.main_view == view else "secondary"):
            st.session_state.main_view = view
            if view == "document_create":
                st.session_state.current_view = "create"
            st.rerun()
    
    st.sidebar.markdown("---")
    
    # 시스템 정보
    st.sidebar.markdown("### 📊 시스템 정보")
    
    doc_manager = st.session_state.doc_manager
    stats = doc_manager.get_statistics()
    
    st.sidebar.metric("학습 문서", stats.get("total_training_documents", 0))
    st.sidebar.metric("생성 문서", stats.get("total_generated_documents", 0))
    
    # 상태 표시
    st.sidebar.markdown("### 🔍 연결 상태")
    if stats.get("storage_available"):
        st.sidebar.success("✅ Azure Storage")
    else:
        st.sidebar.error("❌ Azure Storage")
    
    if stats.get("search_available"):
        st.sidebar.success("✅ Azure AI Search")
    else:
        st.sidebar.error("❌ Azure AI Search")

# 메인 애플리케이션
def main():
    load_css()
    init_session_state()
    
    # 네비게이션 사이드바
    render_navigation()
    
    # 메인 뷰 렌더링
    if st.session_state.main_view == "home":
        render_home_page()
        
    elif st.session_state.main_view == "training_upload":
        render_document_upload_page(st.session_state.doc_manager)
        
    elif st.session_state.main_view == "document_create":
        # 문서 작성 뷰
        if st.session_state.current_view == "create":
            render_document_creation()
        elif st.session_state.current_view == "editor":
            # AI 패널이 열린 경우 레이아웃 조정
            if st.session_state.ai_panel_open:
                col1, col2 = st.columns([3, 1])
                with col1:
                    render_document_editor()
                with col2:
                    render_ai_sidebar()
                    if st.button("❌ 패널 닫기", key="close_panel"):
                        st.session_state.ai_panel_open = False
                        st.rerun()
            else:
                render_document_editor()
                
    elif st.session_state.main_view == "document_manage":
        render_generated_documents_page(st.session_state.doc_manager)

if __name__ == "__main__":
    main()