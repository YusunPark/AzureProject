"""
세션 상태 관리 - Streamlit 세션 상태의 중앙 관리
"""
import streamlit as st
import time
from typing import Dict, Any, Optional

class SessionState:
    """애플리케이션 세션 상태 관리자"""
    
    def __init__(self):
        self.init_all_states()
    
    def init_all_states(self):
        """모든 세션 상태 초기화"""
        self._init_ui_states()
        self._init_document_states()
        self._init_ai_states()
        self._init_cache_states()
    
    def _init_ui_states(self):
        """UI 관련 상태 초기화"""
        if 'ai_panel_open' not in st.session_state:
            st.session_state.ai_panel_open = False  # 기본적으로 닫힌 상태
        if 'current_view' not in st.session_state:
            st.session_state.current_view = "create"
        if 'show_file_upload' not in st.session_state:
            st.session_state.show_file_upload = False
        if 'show_template_options' not in st.session_state:
            st.session_state.show_template_options = False
    
    def _init_document_states(self):
        """문서 관련 상태 초기화"""
        if 'document_content' not in st.session_state:
            st.session_state.document_content = ""
        if 'current_document' not in st.session_state:
            st.session_state.current_document = None
        if 'selected_text' not in st.session_state:
            st.session_state.selected_text = ""
        if 'current_document_title' not in st.session_state:
            st.session_state.current_document_title = ""
    
    def _init_ai_states(self):
        """AI 관련 상태 초기화"""
        if 'analysis_state' not in st.session_state:
            st.session_state.analysis_state = 'idle'
        if 'analysis_result' not in st.session_state:
            st.session_state.analysis_result = {}
        if 'enhanced_prompt' not in st.session_state:
            st.session_state.enhanced_prompt = ""
        if 'internal_search_results' not in st.session_state:
            st.session_state.internal_search_results = []
        if 'external_search_results' not in st.session_state:
            st.session_state.external_search_results = []
        # 새로운 개선된 분석 관련 상태들
        if 'analysis_mode' not in st.session_state:
            st.session_state.analysis_mode = 'manual'
        if 'analysis_text' not in st.session_state:
            st.session_state.analysis_text = ""
        if 'analysis_in_progress' not in st.session_state:
            st.session_state.analysis_in_progress = False
        if 'analysis_completed' not in st.session_state:
            st.session_state.analysis_completed = False
        if 'enhanced_analysis_results' not in st.session_state:
            st.session_state.enhanced_analysis_results = {}
        if 'auto_start_analysis' not in st.session_state:
            st.session_state.auto_start_analysis = False
    
    def _init_cache_states(self):
        """캐시 관련 상태 초기화"""
        if 'last_analysis_hash' not in st.session_state:
            st.session_state.last_analysis_hash = None
    
    def reset_analysis_states(self):
        """AI 분석 관련 상태 리셋"""
        st.session_state.analysis_state = 'idle'
        st.session_state.analysis_result = {}
        st.session_state.enhanced_prompt = ""
        st.session_state.internal_search_results = []
        st.session_state.external_search_results = []
        st.session_state.last_analysis_hash = None
    
    def create_new_document(self, doc_type: str, title: str = "새 문서", content: str = "") -> Dict[str, Any]:
        """새 문서 생성"""
        doc_id = f"{doc_type}_{int(time.time())}"
        document = {
            'id': doc_id,
            'type': doc_type,
            'title': title,
            'created_at': time.time()
        }
        
        st.session_state.current_document = document
        st.session_state.document_content = content
        st.session_state.current_view = "editor"
        
        return document
    
    def get_document_stats(self) -> Dict[str, int]:
        """현재 문서 통계 반환"""
        content = st.session_state.document_content or ""
        if not content.strip():
            return {"words": 0, "chars": 0, "lines": 0}
        
        return {
            "words": len(content.split()),
            "chars": len(content),
            "lines": len(content.split('\n'))
        }
    
    def toggle_ai_panel(self):
        """AI 패널 토글"""
        st.session_state.ai_panel_open = not st.session_state.ai_panel_open
    
    def set_analysis_text(self, text: str):
        """분석할 텍스트 설정"""
        st.session_state.selected_text = text
    
    def is_analysis_ready(self) -> bool:
        """AI 분석 준비 여부 확인"""
        return bool(st.session_state.selected_text and st.session_state.selected_text.strip())

# 글로벌 세션 상태 인스턴스
session_state = SessionState()