"""
문서 편집기 UI 컴포넌트
"""
import streamlit as st
from state.session_state import session_state
from ui.styles import apply_editor_font_style
from config import APP_CONFIG

def render_document_editor():
    """문서 편집기 렌더링"""
    doc = st.session_state.current_document
    if not doc:
        st.error("문서 정보가 없습니다.")
        if st.button("← 문서 생성으로 돌아가기"):
            st.session_state.current_view = "create"
            st.rerun()
        return
    
    # 헤더 렌더링
    _render_editor_header(doc)
    
    st.markdown("---")
    
    # 툴바 렌더링
    editor_height, font_size = _render_editor_toolbar(doc)
    
    # 분석 영역 렌더링 (AI 패널이 닫혀있을 때만)
    if not st.session_state.ai_panel_open:
        _render_analysis_section()
    
    # 메인 텍스트 편집기
    _render_main_editor(editor_height, font_size)

def _render_editor_header(doc):
    """편집기 헤더 렌더링"""
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
            session_state.toggle_ai_panel()

def _render_editor_toolbar(doc):
    """편집기 툴바 렌더링"""
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("💾 저장", use_container_width=True):
            st.success("✅ 문서가 저장되었습니다!")
    
    with col2:
        if st.button("📤 내보내기", use_container_width=True):
            if st.session_state.document_content:
                st.download_button(
                    label="💾 TXT 다운로드",
                    data=st.session_state.document_content,
                    file_name=f"{doc['title']}.txt",
                    mime="text/plain"
                )
    
    with col3:
        if st.button("📊 통계", use_container_width=True):
            stats = session_state.get_document_stats()
            if stats["words"] > 0:
                st.info(f"📊 **문서 통계**\n- 단어: {stats['words']:,}개\n- 문자: {stats['chars']:,}개\n- 줄: {stats['lines']:,}개")
    
    with col4:
        editor_height = st.selectbox(
            "편집기 높이", 
            APP_CONFIG["editor_heights"], 
            index=3, 
            key="editor_height"
        )
    
    with col5:
        font_size = st.selectbox(
            "글꼴 크기", 
            APP_CONFIG["font_sizes"], 
            index=1, 
            key="font_size"
        )
    
    return editor_height, font_size

def _render_analysis_section():
    """분석 섹션 렌더링 (AI 패널이 닫혀있을 때)"""
    st.markdown("---")
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown("#### 🎯 AI 분석할 텍스트 선택")
        selected_text = st.text_input(
            "분석하고 싶은 텍스트를 입력하세요:",
            placeholder="문서에서 분석할 부분을 여기에 입력하세요...",
            help="입력한 텍스트를 AI가 분석하여 맞춤형 결과를 제공합니다.",
            key="analysis_text_input"
        )
        
        if selected_text != st.session_state.selected_text:
            session_state.set_analysis_text(selected_text)
    
    with col2:
        st.markdown("#### 🚀 AI 분석 시작")
        if session_state.is_analysis_ready():
            if st.button("🤖 AI 전문 분석 시작", use_container_width=True, type="primary"):
                session_state.toggle_ai_panel()
                st.session_state.analysis_state = 'analyzing'
                st.rerun()
        else:
            st.button("🤖 AI 전문 분석 시작", use_container_width=True, disabled=True)
            st.caption("분석할 텍스트를 먼저 입력하세요")
    
    with col3:
        _render_quick_analysis_buttons()

def _render_quick_analysis_buttons():
    """빠른 분석 버튼들 렌더링"""
    st.markdown("#### 📝 빠른 분석")
    
    if st.button("📄 전체 문서 분석", use_container_width=True):
        if st.session_state.document_content:
            session_state.set_analysis_text(st.session_state.document_content)
            session_state.toggle_ai_panel()
            st.session_state.analysis_state = 'analyzing'
            st.rerun()
        else:
            st.warning("문서 내용이 없습니다.")
    
    # AI 상태 확인 버튼
    if st.button("🔧 AI 상태 확인", use_container_width=True):
        _show_ai_status_check()

def _render_main_editor(editor_height, font_size):
    """메인 텍스트 편집기 렌더링"""
    st.markdown("#### 📝 문서 편집")
    
    # CSS 스타일 적용
    apply_editor_font_style(font_size)
    
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

def _show_ai_status_check():
    """AI 상태 확인 표시"""
    with st.spinner("AI 연결 상태 확인 중..."):
        from utils.ai_service import AIService
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
        
        # 기타 서비스 상태
        if status["search_available"]:
            st.success("✅ Tavily 검색 활성화됨")
        else:
            st.warning("⚠️ Tavily 검색 비활성화됨")