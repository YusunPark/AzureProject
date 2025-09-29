"""
AI 문서 작성 어시스턴트 - 메인 애플리케이션
리팩토링된 버전: UI 컴포넌트와 비즈니스 로직 분리
"""
import streamlit as st
from config import APP_CONFIG
from state.session_state import session_state
from ui.styles import load_app_styles
from ui.document_creation import render_document_creation
from ui.document_editor import render_document_editor
from ui.ai_sidebar import render_ai_sidebar

def setup_page():
    """페이지 기본 설정"""
    st.set_page_config(
        page_title=APP_CONFIG["page_title"],
        page_icon=APP_CONFIG["page_icon"],
        layout=APP_CONFIG["layout"],
        initial_sidebar_state="collapsed"
    )

def main():
    """메인 애플리케이션"""
    # 페이지 설정
    setup_page()
    
    # CSS 스타일 로드
    load_app_styles()
    
    # 세션 상태 초기화
    session_state.init_all_states()
    
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
            render_ai_sidebar()

if __name__ == "__main__":
    main()