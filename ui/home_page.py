"""
홈 페이지 UI 컴포넌트
"""
import streamlit as st
import time
from typing import Dict, List, Any

from core.session_manager import session_manager
from core.constants import UIConstants, MessageConstants
from core.utils import show_message, format_datetime

def render_home_page():
    """메인 홈 페이지 렌더링"""
    st.markdown("# 🚀 AI 문서 작성 어시스턴트")
    st.markdown("---")
    
    # 환영 메시지 및 시스템 상태
    _render_welcome_section()
    
    st.markdown("---")
    
    # 주요 기능 카드들
    _render_feature_cards()
    
    st.markdown("---")
    
    # 최근 활동 및 통계
    _render_activity_section()

def _render_welcome_section():
    """환영 섹션 렌더링"""
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
        _render_system_status()

def _render_system_status():
    """시스템 상태 표시"""
    st.markdown("#### 🔍 시스템 상태")
    
    doc_manager = st.session_state.get('doc_manager')
    if not doc_manager:
        st.warning("문서 관리 서비스 초기화 중...")
        return
    
    test_results = doc_manager.test_services()
    
    # Azure Storage 상태
    if test_results["storage_service"]["available"]:
        st.markdown(
            '<div class="status-card status-good">✅ Azure Storage 연결됨</div>', 
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="status-card status-error">❌ Azure Storage 연결 실패</div>', 
            unsafe_allow_html=True
        )
    
    # Azure AI Search 상태
    if test_results["search_service"]["available"]:
        st.markdown(
            '<div class="status-card status-good">✅ Azure AI Search 연결됨</div>', 
            unsafe_allow_html=True
        )
        if test_results["search_service"]["has_embedding"]:
            st.markdown(
                '<div class="status-card status-good">🧠 벡터 검색 지원</div>', 
                unsafe_allow_html=True
            )
    else:
        st.markdown(
            '<div class="status-card status-warning">⚠️ Azure AI Search 연결 실패</div>', 
            unsafe_allow_html=True
        )

def _render_feature_cards():
    """주요 기능 카드 렌더링"""
    st.markdown("### 🎯 주요 기능")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📚 사내 문서 학습", 
                    use_container_width=True, 
                    type="primary", 
                    key="home_training"):
            _navigate_to_view(UIConstants.VIEW_TRAINING_UPLOAD)
        
        st.markdown("""
        <div class="status-card">
        <strong>문서 학습 기능</strong><br>
        • 다양한 형식의 문서 업로드<br>
        • Azure AI Search 자동 인덱싱<br>
        • 키워드 및 내용 기반 검색
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.button("📝 새 문서 작성", 
                    use_container_width=True, 
                    type="primary", 
                    key="home_create"):
            _navigate_to_document_creation()
        
        st.markdown("""
        <div class="status-card">
        <strong>AI 문서 작성</strong><br>
        • 실시간 AI 도움말<br>
        • 사내 문서 기반 추천<br>
        • 문장 다듬기 및 구조화
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if st.button("📋 문서 관리", 
                    use_container_width=True, 
                    type="primary", 
                    key="home_manage"):
            _navigate_to_view(UIConstants.VIEW_DOCUMENT_MANAGE)
        
        st.markdown("""
        <div class="status-card">
        <strong>문서 관리</strong><br>
        • 생성된 문서 목록<br>
        • 편집 및 버전 관리<br>
        • Azure Storage 연동 저장
        </div>
        """, unsafe_allow_html=True)

def _render_activity_section():
    """최근 활동 섹션 렌더링"""
    st.markdown("### 📊 최근 활동")
    
    doc_manager = st.session_state.get('doc_manager')
    if not doc_manager:
        st.warning("문서 관리 서비스를 초기화하는 중...")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        _render_training_documents_summary(doc_manager)
    
    with col2:
        _render_generated_documents_summary(doc_manager)

def _render_training_documents_summary(doc_manager):
    """학습 문서 요약"""
    st.markdown("#### 📚 학습된 문서")
    
    try:
        training_docs = doc_manager.list_training_documents()
        
        if training_docs:
            st.metric("총 문서 수", len(training_docs))
            
            # 최근 3개 문서 표시
            st.markdown("**최근 문서:**")
            for doc in training_docs[:3]:
                st.markdown(f"• {doc.get('title', '제목 없음')}")
        else:
            st.info("아직 학습된 문서가 없습니다.")
            if st.button("📤 첫 문서 업로드하기", key="upload_first"):
                _navigate_to_view(UIConstants.VIEW_TRAINING_UPLOAD)
    except Exception as e:
        st.error(f"학습 문서 정보 로드 실패: {str(e)}")

def _render_generated_documents_summary(doc_manager):
    """생성 문서 요약"""
    st.markdown("#### 📄 생성된 문서")
    
    try:
        generated_docs = doc_manager.list_generated_documents()
        
        if generated_docs:
            st.metric("총 문서 수", len(generated_docs))
            
            # 최근 3개 문서 표시
            st.markdown("**최근 문서:**")
            for doc in generated_docs[:3]:
                st.markdown(f"• {doc.get('title', '제목 없음')}")
        else:
            st.info("아직 생성된 문서가 없습니다.")
            if st.button("📝 첫 문서 작성하기", key="create_first"):
                _navigate_to_document_creation()
    except Exception as e:
        st.error(f"생성 문서 정보 로드 실패: {str(e)}")

def _navigate_to_view(view: str):
    """뷰 네비게이션 헬퍼"""
    with st.spinner("페이지 로딩 중..."):
        session_manager.set_main_view(view)
        time.sleep(0.1)  # 상태 업데이트 시간 확보
    st.rerun()

def _navigate_to_document_creation():
    """문서 작성 페이지로 이동"""
    with st.spinner("페이지 로딩 중..."):
        session_manager.set_main_view(UIConstants.VIEW_DOCUMENT_CREATE)
        st.session_state.current_view = UIConstants.VIEW_CREATE
        st.session_state.ai_panel_open = False  # AI 패널 초기화
        time.sleep(0.1)
    st.rerun()