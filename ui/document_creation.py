"""
문서 생성 UI 컴포넌트
"""
import streamlit as st
import time
from state.session_state import session_state

def render_document_creation():
    """문서 생성 인터페이스 렌더링"""
    st.markdown("## 📝 AI 문서 작성 어시스턴트")
    st.markdown("---")
    
    # 상태와 통계 표시
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 새로운 문서를 시작하세요")
        st.markdown("텍스트 편집기에서 문서를 작성하고 AI 도구로 내용을 개선하세요.")
    
    with col2:
        _render_document_stats()
    
    st.markdown("---")
    
    # 문서 생성 버튼들
    st.markdown("### 새 문서 생성")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 새 문서", key="create_text", use_container_width=True):
            session_state.create_new_document("text", "새 문서")
            st.rerun()
    
    with col2:
        if st.button("📋 템플릿 문서", key="create_template", use_container_width=True):
            template_content = """# 제목

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
            session_state.create_new_document("template", "템플릿 문서", template_content)
            st.rerun()
    
    with col3:
        if st.button("📥 불러오기", key="load_document", use_container_width=True):
            st.session_state.show_file_upload = True
    
    # 파일 업로드 기능
    if st.session_state.get('show_file_upload', False):
        _render_file_upload()

def _render_document_stats():
    """문서 통계 렌더링"""
    st.markdown("#### 📊 문서 통계")
    stats = session_state.get_document_stats()
    
    if stats["words"] > 0:
        st.metric("단어 수", f"{stats['words']:,}")
        st.metric("문자 수", f"{stats['chars']:,}")
        st.metric("줄 수", f"{stats['lines']:,}")
    else:
        st.info("문서를 작성하면 통계가 표시됩니다.")

def _render_file_upload():
    """파일 업로드 UI 렌더링"""
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
            session_state.create_new_document("uploaded", uploaded_file.name, content)
            st.session_state.show_file_upload = False
            st.success(f"✅ {uploaded_file.name} 파일이 로드되었습니다!")
            st.rerun()
        except Exception as e:
            st.error(f"파일 로드 중 오류: {str(e)}")
    
    if st.button("취소", key="cancel_upload"):
        st.session_state.show_file_upload = False
        st.rerun()