# app_enhanced.py
import streamlit as st
import time
import json
import random
from datetime import datetime
from typing import Dict, List, Any

# 필요한 서비스들 import
from services.document_management_service import DocumentManagementService
from services.ai_analysis_orchestrator import AIAnalysisOrchestrator
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

# 새로운 4단계 AI 분석 프로세스 실행
def run_new_ai_analysis_process(user_input: str, mode: str = "full", selection: str = None):
    """
    새로운 4단계 AI 분석 프로세스
    1. 프롬프트 고도화
    2. 검색 쿼리 생성
    3. 사내/외부 레퍼런스 병렬 검색
    4. 최종 분석 결과 생성
    """
    
    # 중복 실행 방지
    input_hash = str(hash(user_input + str(selection)))
    if st.session_state.get('last_analysis_hash') == input_hash:
        st.info("이미 분석된 내용입니다. 기존 결과를 표시합니다.")
        return
    
    try:
        st.session_state.last_analysis_hash = input_hash
        
        # AI 분석 오케스트레이터 초기화
        orchestrator = AIAnalysisOrchestrator(mode=mode)
        
        # 진행 상황 표시
        progress_container = st.container()
        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # 각 단계별 실행
            st.markdown("### 🔄 AI 분석 4단계 프로세스")
            
            # 1단계: 프롬프트 고도화
            st.markdown("#### 🔄 1단계: 프롬프트 고도화")
            status_text.text("🧠 사용자 입력을 AI가 더 잘 이해할 수 있도록 개선 중...")
            
            enhanced_prompt = orchestrator._refine_prompt(user_input, selection)
            progress_bar.progress(25)
            st.success("✅ 1단계 완료: 프롬프트 고도화")
            
            with st.expander("🔍 고도화된 프롬프트 확인"):
                st.markdown(f"**원본 입력:**\n{user_input}")
                if selection:
                    st.markdown(f"**선택된 텍스트:**\n{selection}")
                st.markdown(f"**AI 고도화 프롬프트:**\n{enhanced_prompt}")
            
            # 2단계: 검색 쿼리 생성
            st.markdown("#### � 2단계: 검색 쿼리 생성")
            status_text.text("� 사내/외부 검색에 최적화된 쿼리 생성 중...")
            
            internal_query, external_query = orchestrator._generate_queries(enhanced_prompt)
            progress_bar.progress(40)
            st.success("✅ 2단계 완료: 검색 쿼리 생성")
            
            with st.expander("🔍 생성된 검색 쿼리 확인"):
                st.markdown(f"**사내 문서 검색 쿼리:**\n{internal_query}")
                st.markdown(f"**외부 자료 검색 쿼리:**\n{external_query}")
            
            # 3단계: 병렬 검색
            st.markdown("#### 🔄 3단계: 사내/외부 레퍼런스 병렬 검색")
            status_text.text("📚 사내 문서 및 외부 자료를 동시 검색 중...")
            
            internal_refs, external_refs = orchestrator._parallel_reference_search(internal_query, external_query)
            progress_bar.progress(70)
            st.success(f"✅ 3단계 완료: 사내 문서 {len(internal_refs)}개, 외부 자료 {len(external_refs)}개 발견")
            
            # 검색 결과 미리보기
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**📁 사내 문서 결과**")
                for i, doc in enumerate(internal_refs[:3], 1):
                    st.markdown(f"{i}. {doc.get('title', 'N/A')}")
                    
            with col2:
                st.markdown("**🌐 외부 자료 결과**")
                for i, doc in enumerate(external_refs[:3], 1):
                    st.markdown(f"{i}. {doc.get('title', 'N/A')}")
            
            # 4단계: 최종 분석 결과 생성
            st.markdown("#### 🔄 4단계: 최종 분석 결과 생성")
            status_text.text("🤖 모든 정보를 종합하여 최종 AI 분석 결과 생성 중...")
            
            final_result = orchestrator._generate_final_result(enhanced_prompt, internal_refs, external_refs)
            progress_bar.progress(100)
            status_text.text("✅ 모든 단계 완료!")
            st.success("✅ 4단계 완료: 최종 분석 결과 생성")
            
            # 최종 결과 표시
            st.markdown("---")
            st.markdown("### 🎯 최종 AI 분석 결과")
            st.markdown(final_result)
            
            # 레퍼런스 상세 보기
            st.session_state.ai_analysis_references = {"internal": internal_refs, "external": external_refs}
            st.session_state.ai_analysis_result = final_result
            
            # 📖 전체 분석 결과 보기 버튼
            if st.button("📖 전체 분석 결과 보기", use_container_width=True, type="secondary"):
                popup_key = f"popup_content_analysis_{int(time.time())}"
                st.session_state[popup_key] = {
                    "title": "AI 분석 전체 결과",
                    "content": final_result,
                    "show": True
                }
                st.rerun()
            
            # 레퍼런스 관리
            with st.expander("� 레퍼런스 상세 보기"):
                tab1, tab2 = st.tabs(["📁 사내 문서", "🌐 외부 자료"])
                
                with tab1:
                    if internal_refs:
                        for i, ref in enumerate(internal_refs, 1):
                            with st.container():
                                st.markdown(f"**{i}. {ref.get('title', '제목없음')}**")
                                st.caption(f"점수: {ref.get('score', 0):.2f} | 출처: 사내문서")
                                if ref.get('url'):
                                    st.markdown(f"🔗 [링크]({ref.get('url')})")
                                st.markdown(f"{ref.get('content', '')[:200]}...")
                                st.markdown("---")
                    else:
                        st.info("사내 문서 검색 결과가 없습니다.")
                
                with tab2:
                    if external_refs:
                        for i, ref in enumerate(external_refs, 1):
                            with st.container():
                                st.markdown(f"**{i}. {ref.get('title', '제목없음')}**")
                                st.caption(f"점수: {ref.get('score', 0):.2f} | 출처: 외부자료")
                                if ref.get('url'):
                                    st.markdown(f"🔗 [링크]({ref.get('url')})")
                                st.markdown(f"{ref.get('content', '')[:200]}...")
                                st.markdown("---")
                    else:
                        st.info("외부 자료 검색 결과가 없습니다.")
            
            # 문서 삽입 기능
            if st.button("📄 분석 결과를 문서에 삽입", use_container_width=True, type="primary"):
                if 'document_content' in st.session_state:
                    current_content = st.session_state.document_content
                    insert_content = f"\n\n## AI 분석 결과\n\n{final_result}\n\n"
                    st.session_state.document_content = current_content + insert_content
                    st.success("✅ 분석 결과가 문서에 삽입되었습니다!")
                    st.rerun()
                else:
                    st.warning("문서 편집기가 활성화되어 있지 않습니다.")
            
    except Exception as e:
        st.error(f"❌ 분석 프로세스 중 치명적 오류: {str(e)}")
        if 'progress_bar' in locals():
            progress_bar.progress(0)
        if 'status_text' in locals():
            status_text.text("❌ 오류 발생")
        st.exception(e)

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
            
            # 새로운 4단계 AI 분석 프로세스 실행
            search_query = st.session_state.selected_text if search_mode == "선택된 텍스트 기반" else st.session_state.document_content
            
            if search_query and search_query.strip():
                st.success("✅ 새로운 4단계 AI 분석을 시작합니다...")
                
                # 모드 결정
                analysis_mode = "selection" if search_mode == "선택된 텍스트 기반" else "full"
                selection_text = st.session_state.selected_text if search_mode == "선택된 텍스트 기반" else None
                
                run_new_ai_analysis_process(search_query.strip(), mode=analysis_mode, selection=selection_text)
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
        key="app_enhanced_main_editor",
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
        # 개선된 문서 작성 뷰 - AI 패널 통합
        if st.session_state.get('ai_panel_open', False):
            # AI 패널이 열린 경우 2컬럼 레이아웃
            col1, col2 = st.columns([2, 1])
            with col1:
                from ui.document_creation import render_document_creation
                render_document_creation()
            with col2:
                from ui.ai_sidebar import render_ai_sidebar
                render_ai_sidebar()
        else:
            # AI 패널이 닫힌 경우 전체 화면 사용
            from ui.document_creation import render_document_creation
            render_document_creation()
        
        # 팝업은 전체 화면에서 렌더링 (AI 패널과 독립적)
        # 간단한 팝업 시스템 - rerun 없이 동작
        popup_keys = [key for key in st.session_state.keys() if key.startswith('popup_content_')]
        for key in popup_keys:
            popup_data = st.session_state.get(key)
            if popup_data and popup_data.get('show', True):  # show가 없거나 True인 경우에만 표시
                with st.expander(f"📋 {popup_data['title']} - 전체 내용", expanded=True):
                    content = popup_data['content']
                    
                    if isinstance(content, dict):
                        if content.get('title'):
                            st.markdown(f"**📄 제목:** {content.get('title')}")
                        if content.get('summary'):
                            st.markdown("**📋 요약:**")
                            st.markdown(content.get('summary', ''))
                            st.markdown("---")
                        if content.get('content'):
                            st.markdown("**📖 전체 내용:**")
                            st.markdown(content.get('content', ''))
                    else:
                        st.markdown(content)
                    
                    # 닫기 버튼 - rerun 대신 상태만 변경
                    if st.button("❌ 닫기", key=f"close_{key}"):
                        st.session_state[key]['show'] = False  # show를 False로만 변경
                
    elif st.session_state.main_view == "document_manage":
        render_generated_documents_page(st.session_state.doc_manager)

if __name__ == "__main__":
    main()