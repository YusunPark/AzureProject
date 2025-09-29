# app_text_editor.py
import streamlit as st
import time
import json
import random
from datetime import datetime
from typing import Dict, List, Any

# 필요한 서비스들 import
from utils.ai_service import AIService

# 페이지 설정
st.set_page_config(
    page_title="AI 문서 작성 어시스턴트",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed"
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
    
    /* 프로그레스 스타일 */
    .progress-step {
        display: flex;
        align-items: center;
        margin: 8px 0;
        padding: 8px;
        border-radius: 4px;
        background-color: #f8f9fa;
    }
    
    .progress-step.completed {
        background-color: #dcfce7;
        color: #166534;
    }
    
    .progress-step.current {
        background-color: #fef3c7;
        color: #92400e;
    }
    
    .progress-step.pending {
        background-color: #f1f5f9;
        color: #64748b;
    }
    
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
    if 'ai_panel_open' not in st.session_state:
        st.session_state.ai_panel_open = True  # 기본값을 True로 변경
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
        
        with st.spinner("사내 문서 데이터베이스에서 관련 자료를 검색하고 있습니다..."):
            internal_docs = ai_service.search_internal_documents(enhanced_prompt)
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
                internal_docs, 
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
        # 폴백으로 기존 방식 실행
        show_analysis_progress()

# AI 분석 진행 상태 표시
def show_analysis_progress():
    steps = [
        ("✅", "선택된 텍스트 분석", "completed"),
        ("✅", "관련 키워드 추출", "completed"),
        ("🔄", "데이터베이스에서 관련 문서 검색", "current"),
        ("⏳", "AI 모델로 관련성 점수 계산", "pending"),
        ("⏳", "최적의 추천 결과 생성", "pending")
    ]
    
    st.markdown("### 🔄 AI 분석 진행 중")
    
    progress_container = st.empty()
    
    for i, (icon, text, status) in enumerate(steps):
        progress_html = ""
        for j, (s_icon, s_text, s_status) in enumerate(steps):
            if j <= i:
                if j == i and status == "current":
                    progress_html += f'<div class="progress-step current">{s_icon} {s_text}... (진행중)</div>'
                else:
                    progress_html += f'<div class="progress-step completed">{s_icon} {s_text}... (완료)</div>'
            else:
                progress_html += f'<div class="progress-step pending">{s_icon} {s_text}... (대기)</div>'
        
        progress_container.markdown(progress_html, unsafe_allow_html=True)
        time.sleep(0.8)
    
    # 완료 상태
    final_html = ""
    for icon, text, _ in steps:
        final_html += f'<div class="progress-step completed">✅ {text}... (완료)</div>'
    
    progress_container.markdown(final_html, unsafe_allow_html=True)
    st.success("✅ AI 분석이 완료되었습니다!")

# 강화된 분석 결과 표시 
def show_enhanced_analysis_results():
    """3단계 완료 후 검색 결과 요약 표시"""
    st.markdown("### 🎯 강화된 분석 결과 요약")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if hasattr(st.session_state, 'internal_search_results'):
            internal_count = len(st.session_state.internal_search_results)
            st.metric("📁 사내 문서", f"{internal_count}개")
            if internal_count > 0:
                st.caption("Azure AI Search로 검색됨")
        else:
            st.metric("📁 사내 문서", "0개")
    
    with col2:
        if hasattr(st.session_state, 'external_search_results'):
            external_count = len(st.session_state.external_search_results) 
            st.metric("🌐 외부 레퍼런스", f"{external_count}개")
            if external_count > 0:
                st.caption("Tavily 검색으로 발견됨")
        else:
            st.metric("🌐 외부 레퍼런스", "0개")
    
    with col3:
        if hasattr(st.session_state, 'analysis_versions'):
            versions_count = len(st.session_state.analysis_versions)
            st.metric("📋 분석 버전", f"{versions_count}개")
            st.caption("다양한 관점의 결과 생성")
        else:
            st.metric("📋 분석 버전", "0개")

def show_multiple_analysis_versions():
    """여러 버전의 분석 결과 표시"""
    if not hasattr(st.session_state, 'analysis_versions') or not st.session_state.analysis_versions:
        st.warning("분석 결과가 없습니다. AI 분석을 먼저 실행해주세요.")
        return
    
    st.markdown("### 🎯 다양한 관점의 분석 결과")
    st.markdown("동일한 주제에 대해 여러 관점에서 분석한 결과를 확인하고 가장 적합한 버전을 선택하세요.")
    
    versions = st.session_state.analysis_versions
    
    # 버전 선택 탭
    version_titles = [f"{v['title']}" for v in versions]
    selected_tab = st.radio(
        "분석 버전을 선택하세요:",
        options=range(len(versions)),
        format_func=lambda x: version_titles[x],
        key="analysis_version_selector"
    )
    
    # 선택된 버전 표시
    if 0 <= selected_tab < len(versions):
        selected_version = versions[selected_tab]
        
        # 헤더 정보
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.markdown(f"#### {selected_version['title']}")
            st.caption(selected_version['description'])
        
        with col2:
            confidence = selected_version.get('confidence', 0.8) 
            st.metric("신뢰도", f"{confidence:.0%}")
        
        with col3:
            priority = selected_version.get('priority', 1)
            priority_text = ["🔥 최우선", "⚡ 높음", "📋 보통", "💡 참고"][min(priority-1, 3)]
            st.metric("우선순위", priority_text)
        
        # 내용 표시
        st.markdown("---")
        st.markdown(selected_version['content'])
        
        # 액션 버튼
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📝 문서에 삽입", key=f"insert_version_{selected_tab}"):
                insert_content_to_document(selected_version['content'])
                st.success("✅ 선택한 분석 결과가 문서에 삽입되었습니다!")
        
        with col2:
            if st.button("📋 클립보드 복사", key=f"copy_version_{selected_tab}"):
                st.write("클립보드 복사 기능 (브라우저 제한으로 수동 복사 필요)")
                st.code(selected_version['content'], language='markdown')
        
        with col3:
            if st.button("📊 상세 분석", key=f"detail_version_{selected_tab}"):
                with st.expander("🔍 상세 분석 정보", expanded=True):
                    st.markdown("**생성 기준:**")
                    if hasattr(st.session_state, 'enhanced_prompt'):
                        st.markdown(f"- 최적화된 프롬프트: {st.session_state.enhanced_prompt}")
                    
                    st.markdown("**참조 자료:**")
                    if hasattr(st.session_state, 'internal_search_results'):
                        st.markdown(f"- 사내 문서 {len(st.session_state.internal_search_results)}개")
                    if hasattr(st.session_state, 'external_search_results'): 
                        st.markdown(f"- 외부 레퍼런스 {len(st.session_state.external_search_results)}개")
    
    # 전체 버전 비교 (확장 가능)
    with st.expander("🔄 모든 버전 비교 보기"):
        for i, version in enumerate(versions):
            st.markdown(f"#### {i+1}. {version['title']}")
            st.markdown(f"**설명:** {version['description']}")
            st.markdown(f"**신뢰도:** {version.get('confidence', 0.8):.0%} | **우선순위:** {version.get('priority', 1)}")
            
            # 내용 미리보기 (처음 200자)
            preview = version['content'][:200] + "..." if len(version['content']) > 200 else version['content']
            st.markdown(f"**미리보기:**\n{preview}")
            st.markdown("---")

# 문서 추천 결과 표시
def show_recommendations(search_query=""):
    st.markdown("### 📚 추천 문서")
    
    try:
        # AI 서비스 초기화
        ai_service = AIService()
        
        # 검색 쿼리가 있으면 AI 분석 수행
        if search_query:
            with st.spinner("AI가 텍스트를 분석하고 관련 문서를 검색하고 있습니다..."):
                # 텍스트 분석
                analysis_result = ai_service.analyze_text(search_query)
                keywords = analysis_result.get("keywords", [])
                
                # 관련 문서 검색
                docs = ai_service.search_related_documents(search_query, keywords)
        else:
            # 기본 문서 표시
            docs = st.session_state.dummy_data.get("documents", [])
            docs = docs[:3]  # 최대 3개만 표시
        
        if not docs:
            st.info("검색된 문서가 없습니다. 다른 키워드로 시도해보세요.")
            return
        
        for doc in docs:
            with st.expander(f"📄 {doc['title']} (관련도: {doc.get('relevance_score', 0.5):.0%})"):
                st.markdown(f"**요약:** {doc['summary']}")
                st.markdown(f"**출처:** {doc.get('source', '출처 불명')}")
                if doc.get('keywords'):
                    st.markdown(f"**키워드:** {', '.join(doc['keywords'])}")
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown("**내용 미리보기:**")
                    content_preview = doc['content'][:200] + "..." if len(doc['content']) > 200 else doc['content']
                    st.markdown(content_preview)
                
                with col2:
                    if st.button(f"📝 문서에 삽입", key=f"insert_{doc['id']}"):
                        insert_content_to_document(doc['content'])
    
    except Exception as e:
        st.error(f"문서 검색 중 오류가 발생했습니다: {str(e)}")
        # 오류 발생시 더미 데이터 사용
        docs = st.session_state.dummy_data.get("documents", [])[:3]
        for doc in docs:
            with st.expander(f"📄 {doc['title']} (더미 데이터)"):
                st.markdown(f"**요약:** {doc['summary']}")
                st.markdown(f"**출처:** {doc['source']}")
                if st.button(f"📝 문서에 삽입", key=f"dummy_insert_{doc['id']}"):
                    insert_content_to_document(doc['content'])

# 문장 다듬기 기능
def show_text_refinement(selected_text):
    st.markdown("### ✨ 문장 다듬기")
    
    if not selected_text or not selected_text.strip():
        st.info("분석할 텍스트를 선택해주세요.")
        return
    
    try:
        ai_service = AIService()
        
        # AI가 다듬은 버전들
        refinement_styles = [
            ("clear", "명확성 개선", "문장 구조를 단순화하고 모호한 표현을 구체적으로 수정했습니다."),
            ("professional", "전문성 강화", "해당 분야의 전문 용어를 사용하여 신뢰도를 높였습니다."),
            ("concise", "간결성 개선", "불필요한 수식어와 중복 표현을 제거했습니다.")
        ]
        
        for style_key, title, explanation in refinement_styles:
            with st.expander(f"✏️ {title}"):
                with st.spinner(f"{title} 버전을 생성하고 있습니다..."):
                    refined_text = ai_service.refine_text(selected_text, style_key)
                
                st.markdown("**개선된 내용:**")
                st.markdown(f"```\n{refined_text}\n```")
                st.markdown(f"**개선 사유:** {explanation}")
                
                if st.button(f"적용하기", key=f"refine_{style_key}"):
                    insert_content_to_document(refined_text)
    
    except Exception as e:
        st.error(f"문장 다듬기 중 오류가 발생했습니다: {str(e)}")
        # 오류 발생시 더미 데이터 사용
        refined_versions = [
            {
                "title": "명확성 개선",
                "content": f"[개선된 버전] {selected_text}를 더 명확하고 이해하기 쉽게 표현했습니다.",
                "explanation": "문장 구조를 단순화하고 모호한 표현을 구체적으로 수정했습니다."
            },
            {
                "title": "전문성 강화", 
                "content": f"[전문적 버전] {selected_text}에 전문 용어와 정확한 표현을 적용했습니다.",
                "explanation": "해당 분야의 전문 용어를 사용하여 신뢰도를 높였습니다."
            }
        ]
        
        for i, version in enumerate(refined_versions):
            with st.expander(f"✏️ {version['title']} (더미)"):
                st.markdown(f"**개선된 내용:**")
                st.markdown(f"```\n{version['content']}\n```")
                st.markdown(f"**개선 사유:** {version['explanation']}")
                
                if st.button(f"적용하기", key=f"dummy_refine_{i}"):
                    insert_content_to_document(version['content'])

# 구조화 기능
def show_structuring(selected_text):
    st.markdown("### 🏗️ 내용 구조화")
    
    if not selected_text or not selected_text.strip():
        st.info("구조화할 텍스트를 선택해주세요.")
        return
    
    try:
        ai_service = AIService()
        
        # 구조화 유형들
        structure_types = [
            ("outline", "목차 형식", "체계적인 목차와 소제목으로 구성"),
            ("steps", "단계별 가이드", "순차적인 실행 단계로 구성"),
            ("qa", "Q&A 형식", "질문과 답변 형태로 구성")
        ]
        
        for structure_key, title, description in structure_types:
            with st.expander(f"📋 {title}"):
                st.markdown(f"**설명:** {description}")
                
                with st.spinner(f"{title}으로 구조화하고 있습니다..."):
                    structured_content = ai_service.structure_content(selected_text, structure_key)
                
                st.markdown("**구조화된 내용:**")
                st.markdown(structured_content)
                
                if st.button(f"구조 적용", key=f"struct_{structure_key}"):
                    insert_content_to_document(structured_content)
    
    except Exception as e:
        st.error(f"구조화 중 오류가 발생했습니다: {str(e)}")
        # 오류 발생시 더미 데이터 사용
        structures = [
            {
                "title": "목차 형식",
                "content": f"""# 주제

## 1. 개요
{selected_text[:50]}...

## 2. 주요 내용
- 핵심 포인트 1
- 핵심 포인트 2
- 핵심 포인트 3

## 3. 결론
정리 및 마무리"""
            },
            {
                "title": "단계별 가이드", 
                "content": f"""### 📋 단계별 가이드

**1단계: 준비**
{selected_text[:30]}...

**2단계: 실행**
구체적인 실행 방법

**3단계: 검토**
결과 확인 및 개선"""
            }
        ]
        
        for i, structure in enumerate(structures):
            with st.expander(f"📋 {structure['title']} (더미)"):
                st.markdown("**구조화된 내용:**")
                st.markdown(structure['content'])
                
                if st.button(f"구조 적용", key=f"dummy_struct_{i}"):
                    insert_content_to_document(structure['content'])

# 문서에 내용 삽입
def insert_content_to_document(content):
    # 현재 문서 내용에 삽입 (커서 위치는 더미로 처리)
    current_content = st.session_state.document_content
    
    # 삽입 위치 찾기 (실제로는 커서 위치)
    insert_position = len(current_content)  # 끝에 추가
    
    new_content = current_content + f"\n\n{content}"
    
    st.session_state.document_content = new_content
    
    # 삽입 완료 메시지
    st.success("✅ 내용이 문서에 삽입되었습니다!")
    time.sleep(0.5)

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
            
            # 디버깅 정보 표시
            st.write(f"🔍 디버그 정보:")
            st.write(f"- 검색 모드: {search_mode}")
            st.write(f"- 선택된 텍스트: {st.session_state.get('selected_text', 'None')}")
            st.write(f"- 문서 내용 길이: {len(str(st.session_state.get('document_content', '')))}")
            st.write(f"- 최종 쿼리 길이: {len(str(search_query)) if search_query else 0}")
            
            if search_query and search_query.strip():
                st.success("✅ 분석을 시작합니다...")
                run_enhanced_analysis_process(search_query.strip())
            else:
                st.error("❌ 분석할 내용이 없습니다. 문서에 내용을 입력하거나 텍스트를 선택해주세요.")
                # 테스트용 기본 내용 제공
                if st.button("📝 테스트용 샘플 내용으로 분석하기"):
                    test_query = "AI와 머신러닝을 활용한 비즈니스 프로세스 개선 방안에 대해 분석해주세요."
                    st.info(f"테스트 쿼리로 분석합니다: {test_query}")
                    run_enhanced_analysis_process(test_query)
            
            st.session_state.analysis_state = 'completed'
    
    # 분석 완료 후 결과 표시
    if st.session_state.analysis_state == 'completed':
        
        # 강화된 분석 결과가 있는 경우
        if hasattr(st.session_state, 'analysis_versions') and st.session_state.analysis_versions:
            show_enhanced_analysis_results()
        
        # 기존 탭 방식도 유지
        tabs = st.tabs(["🎯 다중 분석 결과", "📚 문서 추천", "✨ 문장 다듬기", "🏗️ 구조화"])
        
        with tabs[0]:
            if hasattr(st.session_state, 'analysis_versions'):
                show_multiple_analysis_versions()
            else:
                st.info("강화된 분석 결과가 없습니다. AI 분석을 다시 실행해주세요.")
        
        with tabs[1]:
            search_query = st.session_state.selected_text if search_mode == "선택된 텍스트 기반" else ""
            show_recommendations(search_query)
        
        with tabs[2]:
            if st.session_state.selected_text:
                show_text_refinement(st.session_state.selected_text)
            else:
                st.info("텍스트를 선택하면 문장 다듬기 기능을 사용할 수 있습니다.")
        
        with tabs[3]:
            if st.session_state.selected_text:
                show_structuring(st.session_state.selected_text)
            else:
                st.info("텍스트를 선택하면 구조화 기능을 사용할 수 있습니다.")

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
    
    # 파일 업로드 기능
    if getattr(st.session_state, 'show_file_upload', False):
        st.markdown("---")
        st.markdown("#### 📥 파일 불러오기")
        
        uploaded_file = st.file_uploader(
            "텍스트 파일을 선택하세요",
            type=['txt', 'md', 'py', 'js', 'html', 'css', 'json'],
            help="지원 형식: TXT, MD, PY, JS, HTML, CSS, JSON"
        )
        
        if uploaded_file is not None:
            try:
                content = uploaded_file.read().decode('utf-8')
                doc_id = f"uploaded_{int(time.time())}"
                st.session_state.current_document = {
                    'id': doc_id,
                    'type': 'uploaded',
                    'title': f'{uploaded_file.name}'
                }
                st.session_state.document_content = content
                st.session_state.current_view = "editor"
                st.session_state.show_file_upload = False
                st.success(f"✅ {uploaded_file.name} 파일이 로드되었습니다!")
                st.rerun()
            except Exception as e:
                st.error(f"파일 로드 중 오류: {str(e)}")
        
        if st.button("취소", key="cancel_upload"):
            st.session_state.show_file_upload = False
            st.rerun()

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
    toolbar_col1, toolbar_col2, toolbar_col3, toolbar_col4, toolbar_col5 = st.columns(5)
    
    with toolbar_col1:
        if st.button("💾 저장", use_container_width=True):
            st.success("✅ 문서가 저장되었습니다!")
    
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
        if st.button("📊 통계", use_container_width=True):
            if st.session_state.document_content:
                content = st.session_state.document_content
                words = len(content.split())
                chars = len(content)
                lines = len(content.split('\n'))
                st.info(f"📊 **문서 통계**\n- 단어: {words:,}개\n- 문자: {chars:,}개\n- 줄: {lines:,}개")
    
    with toolbar_col4:
        editor_height = st.selectbox("편집기 높이", [300, 400, 500, 600, 700, 800], index=3, key="editor_height")
    
    with toolbar_col5:
        font_size = st.selectbox("글꼴 크기", [12, 14, 16, 18, 20], index=1, key="font_size")
    
    # 텍스트 분석 영역을 툴바 아래로 이동 (AI 패널이 닫혀있을 때만 표시)
    if not st.session_state.ai_panel_open:
        st.markdown("---")
        analysis_col1, analysis_col2, analysis_col3 = st.columns([2, 1, 1])
        
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
            st.markdown("#### 🚀 AI 분석 시작")
            if selected_text and selected_text.strip():
                if st.button("🤖 AI 전문 분석 시작", use_container_width=True, type="primary"):
                    st.session_state.ai_panel_open = True
                    st.session_state.analysis_state = 'analyzing'
                    st.rerun()
            else:
                st.button("🤖 AI 전문 분석 시작", use_container_width=True, disabled=True)
                st.caption("분석할 텍스트를 먼저 입력하세요")
        
        with analysis_col3:
            st.markdown("#### 📝 빠른 분석")
            if st.button("📄 전체 문서 분석", use_container_width=True):
                if st.session_state.document_content:
                    st.session_state.selected_text = st.session_state.document_content
                    st.session_state.ai_panel_open = True
                    st.session_state.analysis_state = 'analyzing'
                    st.rerun()
                else:
                    st.warning("문서 내용이 없습니다.")
            
            # AI 연결 상태 확인 버튼 추가
            if st.button("🔧 AI 상태 확인", use_container_width=True):
                with st.spinner("AI 연결 상태 확인 중..."):
                    ai_service = AIService()
                    status = ai_service.test_ai_connection()
                    
                    st.markdown("### 🔍 AI 서비스 상태")
                    
                    # 연결 상태 표시
                    if status["ai_available"]:
                        st.success("✅ Azure OpenAI 연결됨")
                        st.info(f"🤖 모델: {status['model']}\n📍 엔드포인트: {status['endpoint']}")
                        
                        if status["connection_test"] == "성공":
                            st.success("✅ API 호출 테스트 성공")
                            st.markdown(f"**테스트 응답:** {status['test_response']}")
                        else:
                            st.error(f"❌ API 호출 실패: {status['connection_test']}")
                    else:
                        st.error("❌ Azure OpenAI 연결 실패")
                        if not status["api_key_set"]:
                            st.warning("⚠️ OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
                    
                    # LangSmith 추적 상태 표시
                    if status.get("langsmith_enabled"):
                        st.success("✅ LangSmith 추적 활성화됨")
                        st.info(f"📊 프로젝트: {status.get('langsmith_project', 'Unknown')}")
                        st.markdown("🔗 [LangSmith 대시보드에서 추적 확인](https://smith.langchain.com)")
                    else:
                        st.warning("⚠️ LangSmith 추적 비활성화됨")
                        if not status.get("langsmith_key_set"):
                            st.info("💡 LANGSMITH_API_KEY 환경변수를 설정하면 추적이 가능합니다")
                    
                    # 기타 서비스 상태
                    if status["search_available"]:
                        st.success("✅ Tavily 검색 활성화됨")
                    else:
                        st.warning("⚠️ Tavily 검색 비활성화됨")
                        if not status["tavily_key_set"]:
                            st.info("💡 TAVILY_API_KEY를 설정하면 실시간 웹 검색을 사용할 수 있습니다.")
    
    # 메인 텍스트 편집기
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

# 메인 애플리케이션
def main():
    load_css()
    init_session_state()
    
    # 뷰 선택에 따른 렌더링
    if st.session_state.current_view == "create":
        # 문서 생성 인터페이스
        render_document_creation()
        
    elif st.session_state.current_view == "editor":
        # 문서 편집기 인터페이스  
        if st.session_state.ai_panel_open:
            col1, col2 = st.columns([3, 1])
        else:
            col1, col2 = st.columns([1, 0.001])
        
        with col1:
            render_document_editor()
        
        # AI 사이드바
        with col2:
            if st.session_state.ai_panel_open:
                render_ai_sidebar()
                
                # 패널 닫기 버튼
                if st.button("❌ 패널 닫기", key="close_panel"):
                    st.session_state.ai_panel_open = False
                    st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()