# app.py
import streamlit as st
import time
import json
import random
from datetime import datetime
from typing import Dict, List, Any

# 필요한 서비스들 import
from utils.document_service import DocumentService
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
    
    /* CSP 오류 알림 스타일 */
    .csp-warning {
        background-color: #fef2f2;
        border: 1px solid #fecaca;
        border-radius: 8px;
        padding: 16px;
        margin: 16px 0;
        color: #dc2626;
    }
    
    .csp-warning h4 {
        margin: 0 0 8px 0;
        color: #dc2626;
    }
    
    .domain-code {
        background-color: #f1f5f9;
        padding: 4px 8px;
        border-radius: 4px;
        font-family: monospace;
        color: #1e40af;
        font-size: 13px;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #e5e7eb;
        margin: 10px 0;
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
    
    /* 토글 스타일 */
    .toggle-content {
        border: 1px solid #e5e7eb;
        border-radius: 6px;
        margin: 10px 0;
    }
    
    .toggle-header {
        background-color: #f7f7f7;
        padding: 12px;
        cursor: pointer;
        border-bottom: 1px solid #e5e7eb;
        font-weight: 500;
    }
    
    .toggle-body {
        padding: 15px;
        background-color: #ffffff;
    }
    
    /* 하이라이트 효과 */
    .highlight-insert {
        background-color: #fef3c7;
        transition: background-color 3s ease-out;
    }
    
    /* OnlyOffice 프레임 */
    .onlyoffice-frame {
        width: 100%;
        height: 600px;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        background-color: white;
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
        st.session_state.ai_panel_open = False
    if 'selected_text' not in st.session_state:
        st.session_state.selected_text = ""
    if 'document_content' not in st.session_state:
        st.session_state.document_content = "여기에 문서 내용을 작성하세요..."
    if 'analysis_state' not in st.session_state:
        st.session_state.analysis_state = 'idle'
    if 'dummy_data' not in st.session_state:
        st.session_state.dummy_data = generate_dummy_data()
    if 'search_results' not in st.session_state:
        st.session_state.search_results = []

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
    insert_position = len(current_content) // 2  # 더미로 중간 지점 사용
    
    new_content = (current_content[:insert_position] + 
                  f"\n\n{content}\n\n" + 
                  current_content[insert_position:])
    
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
        st.session_state.analysis_state = 'analyzing'
        show_analysis_progress()
        st.session_state.analysis_state = 'completed'
        st.rerun()
    
    # 분석 완료 후 결과 표시
    if st.session_state.analysis_state == 'completed':
        tabs = st.tabs(["📚 문서 추천", "✨ 문장 다듬기", "🏗️ 구조화"])
        
        with tabs[0]:
            search_query = st.session_state.selected_text if search_mode == "선택된 텍스트 기반" else ""
            show_recommendations(search_query)
        
        with tabs[1]:
            if st.session_state.selected_text:
                show_text_refinement(st.session_state.selected_text)
            else:
                st.info("텍스트를 선택하면 문장 다듬기 기능을 사용할 수 있습니다.")
        
        with tabs[2]:
            if st.session_state.selected_text:
                show_structuring(st.session_state.selected_text)
            else:
                st.info("텍스트를 선택하면 구조화 기능을 사용할 수 있습니다.")

# OnlyOffice DocSpace 에디터
def render_onlyoffice_editor():
    st.markdown("### 📝 문서 편집기")
    
    # 툴바
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        if st.button("🤖 AI 추천", key="ai_recommend_all"):
            st.session_state.ai_panel_open = True
            st.rerun()
    
    with col2:
        if st.button("💾 저장"):
            st.success("문서가 저장되었습니다!")
    
    with col3:
        if st.button("📤 내보내기"):
            st.info("문서 내보내기 기능")
    
    with col4:
        if st.button("👥 공유"):
            st.info("문서 공유 기능")
    
    st.markdown("---")
    
    # OnlyOffice 통합 옵션 선택
    integration_mode = st.selectbox(
        "OnlyOffice 통합 방식 선택:",
        ["JavaScript SDK (권장)", "개선된 iframe 통합", "직접 편집기 연결", "임베디드 에디터 옵션", "외부 링크"],
        help="CSP 오류나 iframe 제한이 발생하면 다른 옵션을 시도해보세요."
    )
    
    # 높이 조절
    editor_height = st.slider("편집기 높이 (px)", 400, 800, 600, 50)
    
    # 텍스트 선택 시뮬레이션
    st.markdown("#### 텍스트 분석 (시뮬레이션)")
    selected_text = st.text_input(
        "분석할 텍스트 입력:",
        placeholder="AI가 분석할 텍스트를 입력하세요...",
        help="실제로는 OnlyOffice에서 선택된 텍스트가 자동으로 전달됩니다."
    )
    
    if selected_text != st.session_state.selected_text:
        st.session_state.selected_text = selected_text
    
    if selected_text:
        if st.button("🎯 선택된 텍스트로 AI 추천"):
            st.session_state.ai_panel_open = True
            st.rerun()
    
    st.markdown("---")
    
    # 문서 서비스 초기화
    doc_service = DocumentService()
    
    # OnlyOffice 통합
    if integration_mode == "JavaScript SDK (권장)":
        st.markdown("#### OnlyOffice DocSpace (JavaScript SDK)")
        
        # CSP 관련 안내
        with st.expander("⚠️ CSP 오류 해결 방법", expanded=True):
            st.markdown("""
        **Azure App Service 배포 후 OnlyOffice DocSpace 설정:**
        
        1. **OnlyOffice DocSpace 관리자 계정**으로 로그인
        2. **Settings** → **Developer Tools** → **JavaScript SDK** 선택
        3. **Allowed domains** 섹션에 다음 주소들을 **정확히** 추가:
           - `https://appsvc-yusun-01.azurewebsites.net`
           - `*.azurewebsites.net` (와일드카드 도메인)
           - `http://localhost:8504` (로컬 개발용)
           - `http://127.0.0.1:8504` (로컬 개발용)
        
        4. **Save** 버튼 클릭 후 약 1-2분 대기
        5. 브라우저 **강력 새로고침** (Ctrl+F5 또는 Cmd+Shift+R)
        
        📋 **현재 접속 URL**: `https://appsvc-yusun-01.azurewebsites.net`
        
        ⚠️ **여전히 문제가 발생하면:**
        - "개선된 iframe 통합" 또는 "외부 링크" 옵션 사용
        - OnlyOffice 관리자에게 도메인 허용 요청
        """)
        
        # JavaScript SDK 방식
        onlyoffice_html = doc_service.create_onlyoffice_docspace_html(
            width="100%", 
            height=f"{editor_height}px"
        )
        st.components.v1.html(onlyoffice_html, height=editor_height + 50)
        
    elif integration_mode == "개선된 iframe 통합":
        st.markdown("#### OnlyOffice DocSpace (개선된 iframe)")
        st.info("💡 개선된 iframe 방식: 새로고침 및 전체화면 버튼이 포함되어 있습니다.")
        
        iframe_html = doc_service.create_alternative_docspace_iframe(
            width="100%", 
            height=f"{editor_height}px"
        )
        st.components.v1.html(iframe_html, height=editor_height + 50)
        
    elif integration_mode == "직접 편집기 연결":
        st.markdown("#### OnlyOffice 직접 편집기")
        
        # 파일 ID 입력 옵션
        col1, col2 = st.columns([2, 1])
        with col1:
            file_id = st.text_input(
                "파일 ID (선택사항):",
                placeholder="예: 2403165",
                help="특정 문서를 열려면 파일 ID를 입력하세요. 비워두면 기본 편집기가 열립니다."
            )
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔍 파일 ID 확인 방법"):
                st.info("OnlyOffice에서 문서 URL을 확인하면 'fileId=' 뒤의 숫자가 파일 ID입니다.")
        
        direct_editor_html = doc_service.create_direct_editor_iframe(
            file_id=file_id if file_id else None,
            width="100%", 
            height=f"{editor_height}px"
        )
        st.components.v1.html(direct_editor_html, height=editor_height + 50)
        
    elif integration_mode == "임베디드 에디터 옵션":
        st.markdown("#### OnlyOffice 임베디드 에디터")
        st.success("🎯 **추천**: iframe 제한을 우회하는 가장 안정적인 방법입니다.")
        
        embedded_editor_html = doc_service.create_embedded_editor_option(
            width="100%", 
            height=f"{editor_height}px"
        )
        st.components.v1.html(embedded_editor_html, height=editor_height + 20)
        
    else:  # 외부 링크
        st.markdown("#### OnlyOffice DocSpace (외부 링크)")
        external_link_html = doc_service.create_external_link_option()
        st.components.v1.html(external_link_html, height=300)
    
    # 메인 편집 영역 (대체)
    st.markdown("---")
    st.markdown("#### 📄 문서 편집 영역 (대체용)")
    document_content = st.text_area(
        "문서 내용:",
        value=st.session_state.document_content,
        height=200,
        key="document_editor",
        help="OnlyOffice가 로드되지 않을 때 사용하는 대체 편집기입니다."
    )
    
    if document_content != st.session_state.document_content:
        st.session_state.document_content = document_content

# 메인 애플리케이션
def main():
    load_css()
    init_session_state()
    
    st.title("📝 AI 문서 작성 어시스턴트")
    
    # 레이아웃 구성
    if st.session_state.ai_panel_open:
        col1, col2 = st.columns([3, 1])
    else:
        col1, col2 = st.columns([1, 0.001])
    
    # 메인 편집 영역
    with col1:
        render_onlyoffice_editor()
    
    # AI 사이드바 영역
    with col2:
        if st.session_state.ai_panel_open:
            st.markdown('<div class="ai-sidebar">', unsafe_allow_html=True)
            render_ai_sidebar()
            
            # 패널 닫기 버튼
            if st.button("❌ 패널 닫기", key="close_panel"):
                st.session_state.ai_panel_open = False
                st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()

