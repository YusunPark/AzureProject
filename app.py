# app.py
import streamlit as st
import time
import json
import random
from datetime import datetime
from typing import Dict, List, Any

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
    
    # 검색어에 따른 결과 필터링 (더미 구현)
    docs = st.session_state.dummy_data["documents"]
    if search_query:
        # 실제로는 더 정교한 검색 로직 구현
        docs = [doc for doc in docs if any(keyword.lower() in search_query.lower() for keyword in doc["keywords"])]
    
    for doc in docs:
        with st.expander(f"📄 {doc['title']} (관련도: {doc['relevance_score']:.0%})"):
            st.markdown(f"**요약:** {doc['summary']}")
            st.markdown(f"**출처:** {doc['source']}")
            st.markdown(f"**키워드:** {', '.join(doc['keywords'])}")
            
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown("**내용 미리보기:**")
                st.markdown(doc['content'])
            
            with col2:
                if st.button(f"📝 문서에 삽입", key=f"insert_{doc['id']}"):
                    insert_content_to_document(doc['content'])

# 문장 다듬기 기능
def show_text_refinement(selected_text):
    st.markdown("### ✨ 문장 다듬기")
    
    # AI가 다듬은 버전들 (더미)
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
        },
        {
            "title": "간결성 개선",
            "content": f"[간결한 버전] {selected_text}의 핵심 내용만 추려 간결하게 표현했습니다.",
            "explanation": "불필요한 수식어와 중복 표현을 제거했습니다."
        }
    ]
    
    for version in refined_versions:
        with st.expander(f"✏️ {version['title']}"):
            st.markdown(f"**개선된 내용:**")
            st.markdown(f"```\n{version['content']}\n```")
            st.markdown(f"**개선 사유:** {version['explanation']}")
            
            if st.button(f"적용하기", key=f"refine_{version['title']}"):
                insert_content_to_document(version['content'])

# 구조화 기능
def show_structuring(selected_text):
    st.markdown("### 🏗️ 내용 구조화")
    
    structures = [
        {
            "title": "목차 형식",
            "content": f"""
# 주제
## 1. 개요
{selected_text[:50]}...

## 2. 주요 내용
- 핵심 포인트 1
- 핵심 포인트 2
- 핵심 포인트 3

## 3. 결론
정리 및 마무리
            """.strip()
        },
        {
            "title": "단계별 가이드",
            "content": f"""
### 📋 단계별 가이드

**1단계: 준비**
{selected_text[:30]}...

**2단계: 실행**
구체적인 실행 방법

**3단계: 검토**
결과 확인 및 개선
            """.strip()
        },
        {
            "title": "Q&A 형식",
            "content": f"""
### ❓ Q&A 형식

**Q: 주요 질문은 무엇인가요?**
A: {selected_text[:50]}...

**Q: 어떤 방법을 사용해야 하나요?**
A: 구체적인 방법론 설명

**Q: 주의사항은 무엇인가요?**
A: 유의해야 할 점들
            """.strip()
        }
    ]
    
    for structure in structures:
        with st.expander(f"📋 {structure['title']}"):
            st.markdown("**구조화된 내용:**")
            st.markdown(structure['content'])
            
            if st.button(f"구조 적용", key=f"struct_{structure['title']}"):
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
    from utils.document_service import DocumentService
    
    st.markdown("### 📝 문서 편집기")
    
    # 툴바
    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
    
    with col1:
        if st.button("🤖 AI 추천", key="ai_recommend_all"):
            st.session_state.ai_panel_open = True
            st.rerun()
    
    with col2:
        doc_type = st.selectbox("📄 문서 유형", ["docx", "pptx", "xlsx"], key="doc_type")
    
    with col3:
        if st.button("� 새 문서"):
            doc_service = DocumentService()
            result = doc_service.create_new_document(doc_type, f"새 {doc_type} 문서")
            if result["success"]:
                st.success(f"새 {doc_type} 문서가 생성되었습니다!")
                st.session_state.current_document = result
    
    with col4:
        if st.button("� 저장"):
            st.success("문서가 저장되었습니다!")
    
    with col5:
        if st.button("👥 공유"):
            st.info("문서 공유 기능")
    
    # 문서 내용 편집 영역
    st.markdown("---")
    
    # 텍스트 선택 기능
    col_text, col_button = st.columns([3, 1])
    
    with col_text:
        selected_text = st.text_input(
            "🎯 텍스트 선택 (AI 분석용):",
            placeholder="분석하고 싶은 텍스트를 입력하세요...",
            help="OnlyOffice에서 텍스트를 선택한 후, 여기에 붙여넣어 AI 추천을 받으세요."
        )
    
    with col_button:
        st.markdown("<br>", unsafe_allow_html=True)  # 버튼 위치 조정
        if st.button("🎯 AI 분석", disabled=not selected_text):
            st.session_state.selected_text = selected_text
            st.session_state.ai_panel_open = True
            st.rerun()
    
    if selected_text != st.session_state.selected_text:
        st.session_state.selected_text = selected_text
    
    # OnlyOffice DocSpace 편집기
    st.markdown("#### 📝 OnlyOffice DocSpace 편집기")
    
    # 편집기 옵션
    editor_col1, editor_col2 = st.columns([1, 3])
    
    with editor_col1:
        editor_height = st.slider("편집기 높이", 400, 800, 600, 50)
        show_editor = st.checkbox("편집기 표시", value=True)
    
    with editor_col2:
        if show_editor:
            st.info("💡 **사용 방법**: 아래 편집기에서 텍스트를 선택한 후, 위의 '텍스트 선택' 필드에 붙여넣어 AI 분석을 받으세요.")
    
    if show_editor:
        # OnlyOffice DocSpace 편집기 HTML 생성
        doc_service = DocumentService()
        editor_html = doc_service.create_onlyoffice_docspace_html(
            width="100%", 
            height=f"{editor_height}px"
        )
        
        # HTML 컴포넌트로 표시
        st.components.v1.html(editor_html, height=editor_height + 50, scrolling=True)
        
        # 사용 안내
        with st.expander("📖 편집기 사용 가이드"):
            st.markdown("""
            ### OnlyOffice DocSpace 편집기 사용법
            
            1. **문서 작성**: 편집기에서 직접 텍스트를 입력하고 편집하세요
            2. **텍스트 선택**: 분석하고 싶은 텍스트를 드래그하여 선택하세요  
            3. **복사 및 분석**: 선택한 텍스트를 복사하여 위의 'AI 분석' 필드에 붙여넣으세요
            4. **AI 추천 활용**: 우측 사이드바에서 문서 추천, 문장 다듬기, 구조화 기능을 사용하세요
            5. **결과 삽입**: AI 추천 결과를 편집기에 다시 삽입하여 문서를 개선하세요
            
            #### 지원 기능
            - 📝 실시간 문서 편집
            - 💾 자동 저장
            - 📤 다양한 형식으로 내보내기  
            - 👥 협업 및 공유
            - 🔍 AI 기반 문서 분석 및 개선
            """)
    else:
        # 편집기가 비활성화된 경우 텍스트 영역 표시
        st.markdown("#### 📝 텍스트 편집 영역 (시뮬레이션)")
        
        document_content = st.text_area(
            "문서 내용:",
            value=st.session_state.document_content,
            height=400,
            key="document_editor",
            help="OnlyOffice 편집기 대신 사용할 수 있는 간단한 텍스트 편집 영역입니다."
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
