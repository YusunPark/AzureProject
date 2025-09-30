"""
개선된 세션 상태 관리자
"""
import streamlit as st
from typing import Any, Dict, Optional
from core.constants import UIConstants

class SessionStateManager:
    """중앙화된 세션 상태 관리자"""
    
    def __init__(self):
        self.initialize_all_states()
    
    def initialize_all_states(self):
        """모든 세션 상태 초기화"""
        self._init_ui_states()
        self._init_document_states()
        self._init_ai_states()
        self._init_cache_states()
    
    def _init_ui_states(self):
        """UI 관련 상태 초기화"""
        ui_defaults = {
            'main_view': UIConstants.VIEW_HOME,
            'current_view': UIConstants.VIEW_CREATE,
            'ai_panel_open': False,
            'show_file_upload': False,
            'show_template_options': False,
            'editor_height': UIConstants.DEFAULT_EDITOR_HEIGHT,
            'font_size': UIConstants.DEFAULT_FONT_SIZE,
            'analysis_state': UIConstants.ANALYSIS_IDLE
        }
        
        for key, default_value in ui_defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
    
    def _init_document_states(self):
        """문서 관련 상태 초기화"""
        doc_defaults = {
            'document_content': '',
            'selected_text': '',
            'current_document': None,
            'document_title': '',
            'document_metadata': {},
            'last_saved_content': '',
            'unsaved_changes': False
        }
        
        for key, default_value in doc_defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
    
    def _init_ai_states(self):
        """AI 분석 관련 상태 초기화"""
        ai_defaults = {
            'ai_results': {},
            'ai_analysis_references': {},
            'ai_analysis_result': '',
            'search_results': [],
            'last_analysis_hash': '',
            'analysis_mode': 'full'
        }
        
        for key, default_value in ai_defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
    
    def _init_cache_states(self):
        """캐시 관련 상태 초기화"""
        cache_defaults = {
            'cached_documents': {},
            'cached_search_results': {},
            'cache_timestamps': {},
            'service_status_cache': {}
        }
        
        for key, default_value in cache_defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
    
    # Getter/Setter 메서드들
    def get_main_view(self) -> str:
        """현재 메인 뷰 반환"""
        return st.session_state.get('main_view', UIConstants.VIEW_HOME)
    
    def set_main_view(self, view: str):
        """메인 뷰 설정"""
        st.session_state.main_view = view
    
    def get_document_content(self) -> str:
        """문서 내용 반환"""
        return st.session_state.get('document_content', '')
    
    def set_document_content(self, content: str):
        """문서 내용 설정"""
        old_content = st.session_state.get('document_content', '')
        st.session_state.document_content = content
        
        # 변경 사항 추적
        if content != old_content:
            st.session_state.unsaved_changes = True
    
    def get_document_stats(self) -> Dict[str, int]:
        """문서 통계 반환"""
        content = self.get_document_content()
        if not content:
            return {"words": 0, "chars": 0, "lines": 0}
        
        return {
            "words": len(content.split()),
            "chars": len(content),
            "lines": len(content.split('\n'))
        }
    
    def is_ai_panel_open(self) -> bool:
        """AI 패널 열림 상태 확인"""
        return st.session_state.get('ai_panel_open', False)
    
    def toggle_ai_panel(self):
        """AI 패널 토글"""
        st.session_state.ai_panel_open = not st.session_state.get('ai_panel_open', False)
    
    def get_selected_text(self) -> str:
        """선택된 텍스트 반환"""
        return st.session_state.get('selected_text', '')
    
    def set_selected_text(self, text: str):
        """선택된 텍스트 설정"""
        st.session_state.selected_text = text
    
    def get_current_document(self) -> Optional[Dict]:
        """현재 문서 정보 반환"""
        return st.session_state.get('current_document')
    
    def set_current_document(self, document: Dict):
        """현재 문서 설정"""
        st.session_state.current_document = document
    
    def clear_current_document(self):
        """현재 문서 초기화"""
        st.session_state.current_document = None
        st.session_state.document_content = ''
        st.session_state.document_title = ''
        st.session_state.unsaved_changes = False
    
    def has_unsaved_changes(self) -> bool:
        """저장되지 않은 변경사항 확인"""
        return st.session_state.get('unsaved_changes', False)
    
    def mark_as_saved(self):
        """저장 완료로 표시"""
        st.session_state.unsaved_changes = False
        st.session_state.last_saved_content = st.session_state.get('document_content', '')
    
    def get_analysis_state(self) -> str:
        """AI 분석 상태 반환"""
        return st.session_state.get('analysis_state', UIConstants.ANALYSIS_IDLE)
    
    def set_analysis_state(self, state: str):
        """AI 분석 상태 설정"""
        st.session_state.analysis_state = state
    
    def cache_data(self, key: str, data: Any, ttl: int = 300):
        """데이터 캐시"""
        import time
        st.session_state.cached_documents[key] = data
        st.session_state.cache_timestamps[key] = time.time() + ttl
    
    def get_cached_data(self, key: str) -> Optional[Any]:
        """캐시된 데이터 조회"""
        import time
        current_time = time.time()
        
        if key in st.session_state.cached_documents:
            expiry_time = st.session_state.cache_timestamps.get(key, 0)
            if current_time < expiry_time:
                return st.session_state.cached_documents[key]
            else:
                # 만료된 캐시 삭제
                self.clear_cache_entry(key)
        
        return None
    
    def clear_cache_entry(self, key: str):
        """특정 캐시 항목 삭제"""
        st.session_state.cached_documents.pop(key, None)
        st.session_state.cache_timestamps.pop(key, None)
    
    def clear_all_cache(self):
        """모든 캐시 삭제"""
        st.session_state.cached_documents = {}
        st.session_state.cache_timestamps = {}
    
    def reset_all_states(self):
        """모든 상태 초기화 (로그아웃 등에 사용)"""
        keys_to_keep = ['doc_manager']  # 보존할 키들
        
        for key in list(st.session_state.keys()):
            if key not in keys_to_keep:
                del st.session_state[key]
        
        self.initialize_all_states()

# 전역 인스턴스
session_manager = SessionStateManager()