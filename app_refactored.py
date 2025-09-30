"""
개선된 메인 애플리케이션
리팩토링된 구조로 코드 간소화 및 모듈화
"""
import streamlit as st
import time
from typing import Dict, List, Any

# Core modules
from core.session_manager import session_manager
from core.constants import UIConstants, MessageConstants
from core.utils import show_message

# Services
from services.document_management_service import DocumentManagementService
from services.ai_analysis_orchestrator_refactored import AIAnalysisOrchestrator

# UI Components
from ui.styles import load_app_styles
from ui.home_page import render_home_page
from ui.navigation import render_navigation_sidebar
from ui.document_upload import render_document_upload_page
from ui.document_creation import render_document_creation_page
from ui.generated_documents import render_generated_documents_page

class MainApplication:
    """메인 애플리케이션 클래스"""
    
    def __init__(self):
        self._setup_page()
        self._initialize_services()
        
    def _setup_page(self):
        """페이지 기본 설정"""
        st.set_page_config(
            page_title="AI 문서 작성 어시스턴트",
            page_icon="📝",
            layout="wide",
            initial_sidebar_state="expanded"
        )
    
    def _initialize_services(self):
        """서비스 초기화"""
        # 세션 상태 초기화
        session_manager.initialize_all_states()
        
        # 문서 관리 서비스 초기화
        if 'doc_manager' not in st.session_state:
            st.session_state.doc_manager = DocumentManagementService()
    
    def run(self):
        """애플리케이션 실행"""
        try:
            # CSS 스타일 로드
            load_app_styles()
            
            # 네비게이션 사이드바
            render_navigation_sidebar()
            
            # 메인 컨텐츠 렌더링
            self._render_main_content()
            
        except Exception as e:
            st.error(f"애플리케이션 실행 중 오류 발생: {str(e)}")
            st.exception(e)
    
    def _render_main_content(self):
        """메인 컨텐츠 렌더링"""
        current_view = session_manager.get_main_view()
        
        if current_view == UIConstants.VIEW_HOME:
            render_home_page()
            
        elif current_view == UIConstants.VIEW_TRAINING_UPLOAD:
            render_document_upload_page(st.session_state.doc_manager)
            
        elif current_view == UIConstants.VIEW_DOCUMENT_CREATE:
            self._render_document_creation_with_ai()
            
        elif current_view == UIConstants.VIEW_AI_ANALYSIS:
            self._render_ai_analysis_page()
            
        elif current_view == UIConstants.VIEW_DOCUMENT_MANAGE:
            render_generated_documents_page(st.session_state.doc_manager)
            
        else:
            st.error(f"알 수 없는 뷰: {current_view}")
    
    def _render_document_creation_with_ai(self):
        """문서 생성 + AI 패널 통합 렌더링"""
        # AI 패널 상태에 따른 레이아웃
        if session_manager.is_ai_panel_open():
            col1, col2 = st.columns(UIConstants.LAYOUT_EDITOR_AI)
            
            with col1:
                render_document_creation_page()
            
            with col2:
                self._render_ai_panel()
        else:
            # AI 패널이 닫혀있을 때는 전체 화면 사용
            render_document_creation_page()
        
        # 팝업 렌더링 (AI 패널과 독립적)
        self._render_popups()
    
    def _render_ai_panel(self):
        """AI 패널 렌더링"""
        from ui.ai_sidebar import render_ai_sidebar
        render_ai_sidebar()
    
    def _render_popups(self):
        """팝업 렌더링"""
        popup_keys = [key for key in st.session_state.keys() 
                     if key.startswith('popup_content_')]
        
        for key in popup_keys:
            popup_data = st.session_state.get(key)
            if popup_data and popup_data.get('show', True):
                self._render_single_popup(key, popup_data)
    
    def _render_ai_analysis_page(self):
        """AI 분석 페이지 렌더링"""
        from ui.ai_analysis_ui import ai_analysis_page
        ai_analysis_page()
    
    def _render_single_popup(self, key: str, popup_data: Dict):
        """단일 팝업 렌더링"""
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
            
            # 닫기 버튼
            if st.button("❌ 닫기", key=f"close_{key}"):
                st.session_state[key]['show'] = False

def main():
    """메인 진입점"""
    app = MainApplication()
    app.run()

if __name__ == "__main__":
    main()