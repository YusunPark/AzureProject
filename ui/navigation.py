"""
네비게이션 사이드바 UI 컴포넌트
"""
import streamlit as st
from core.session_manager import session_manager
from core.constants import UIConstants

def render_navigation_sidebar():
    """네비게이션 사이드바 렌더링"""
    st.sidebar.markdown("# 🚀 AI 문서 어시스턴트")
    st.sidebar.markdown("---")
    
    # 메인 메뉴 렌더링
    _render_main_menu()
    
    st.sidebar.markdown("---")
    
    # 시스템 정보 렌더링
    _render_system_info()

def _render_main_menu():
    """메인 메뉴 렌더링"""
    menu_options = {
        "🏠 홈": UIConstants.VIEW_HOME,
        "📚 사내 문서 학습": UIConstants.VIEW_TRAINING_UPLOAD, 
        "📝 문서 작성": UIConstants.VIEW_DOCUMENT_CREATE,
        "🤖 AI 분석": UIConstants.VIEW_AI_ANALYSIS,
        "📋 문서 관리": UIConstants.VIEW_DOCUMENT_MANAGE
    }
    
    current_view = session_manager.get_main_view()
    
    for label, view in menu_options.items():
        button_type = "primary" if current_view == view else "secondary"
        
        if st.sidebar.button(label, use_container_width=True, type=button_type):
            session_manager.set_main_view(view)
            if view == UIConstants.VIEW_DOCUMENT_CREATE:
                st.session_state.current_view = UIConstants.VIEW_CREATE
            st.rerun()

def _render_system_info():
    """시스템 정보 렌더링"""
    st.sidebar.markdown("### 📊 시스템 정보")
    
    doc_manager = st.session_state.get('doc_manager')
    if doc_manager:
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
    else:
        st.sidebar.info("시스템 초기화 중...")