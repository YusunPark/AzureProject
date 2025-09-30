"""
문서 편집기 UI 컴포넌트
"""
import streamlit as st
import time
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
    
    # AI 패널이 닫혀있고 문서에 내용이 있을 때만 AI 도구 표시
    if (not st.session_state.ai_panel_open and 
        st.session_state.get('document_content', '').strip()):
        _render_analysis_section()
    
    # 메인 텍스트 편집기
    _render_main_editor(editor_height, font_size)
    
    # 저장 다이얼로그
    if st.session_state.get('show_save_dialog', False):
        _render_save_dialog(doc)

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
        if st.button("💾 저장", use_container_width=True, key="save_doc_btn"):
            # 저장 모드 활성화
            st.session_state.show_save_dialog = True
            st.rerun()
    
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
    st.markdown("#### 🤖 AI 분석 도구")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 전체 문서 분석", use_container_width=True, type="primary"):
            # 현재 문서 내용을 분석 텍스트로 설정
            document_content = st.session_state.get('document_content', '')
            if document_content.strip():
                session_state.set_analysis_text(document_content)
                session_state.toggle_ai_panel()
                st.session_state.analysis_state = 'analyzing'
                st.rerun()
            else:
                st.warning("문서 내용이 없습니다.")
    
    with col2:
        if st.button("� 선택 영역 분석", use_container_width=True):
            # 현재 문서 내용이 있는 경우에만 AI 패널 열기
            document_content = st.session_state.get('document_content', '')
            if document_content.strip():
                # AI 패널 열기 (사용자가 선택할 수 있게)
                session_state.toggle_ai_panel()
                st.session_state.search_mode = "선택된 텍스트 기반"
                st.info("💡 AI 패널이 열렸습니다. 문서에서 분석할 텍스트를 복사해서 AI 패널에 붙여넣으세요.")
                st.rerun()
            else:
                st.warning("먼저 문서 내용을 작성해주세요.")
    
    with col3:
        if st.button("🔧 AI 상태 확인", use_container_width=True):
            _show_ai_status_check()
    
    # 사용 방법 안내
    st.info("""
    💡 **사용 방법:**
    - **📄 전체 문서 분석**: 작성한 문서 전체를 AI가 분석합니다
    - **📝 선택 영역 분석**: 문서에서 원하는 부분을 복사해서 AI 패널에 붙여넣어 분석하세요
    - **🔧 AI 상태 확인**: Azure OpenAI 연결 상태를 확인합니다
    """)



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
        key="document_editor_main_content",
        help="여기에 문서 내용을 작성하세요. AI 패널을 열어 도움을 받을 수 있습니다.",
        placeholder="여기에 문서 내용을 입력하세요..."
    )
    
    # 문서 내용 실시간 업데이트
    st.session_state.document_content = document_content

def _render_save_dialog(doc):
    """저장 다이얼로그 렌더링"""
    # 현재 문서 내용 가져오기
    content = doc.content.strip() if hasattr(doc, 'content') and doc.content else ""
    if not content.strip() and 'document_editor_main_content' in st.session_state:
        content = st.session_state.document_editor_main_content

def _render_save_dialog(doc):
    """저장 다이얼로그 렌더링"""
    # 현재 문서 내용 가져오기
    content = st.session_state.get('document_content', '')
    
    # 텍스트 에어리어에서 직접 값 가져오기 시도
    if not content.strip() and 'main_document_editor' in st.session_state:
        content = st.session_state.main_document_editor
    
    if not content.strip():
        st.error("⚠️ 저장할 내용이 없습니다. 문서 편집 영역에 내용을 입력해주세요.")
        if st.button("확인", key="no_content_ok"):
            st.session_state.show_save_dialog = False
            st.rerun()
        return
    
    # 제목 입력 받기
    with st.form("save_document_form", clear_on_submit=False):
        st.markdown("### 📝 문서 저장")
        
        # 기본 제목 설정
        default_title = doc.get('title', '새 문서')
        if default_title in ['새 문서', '템플릿 문서']:
            # 내용의 첫 줄을 제목으로 사용
            lines = content.split('\n')
            first_line = lines[0].strip()
            if first_line and len(first_line) < 50:
                default_title = first_line.replace('#', '').strip()
        
        document_title = st.text_input(
            "문서 제목",
            value=default_title,
            placeholder="문서 제목을 입력하세요",
            help="이 제목으로 파일이 저장됩니다",
            key="save_dialog_title"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            save_clicked = st.form_submit_button("💾 저장", use_container_width=True)
        
        with col2:
            cancel_clicked = st.form_submit_button("취소", use_container_width=True)
        
        if save_clicked and document_title.strip():
            # 문서 관리 서비스를 통해 저장
            try:
                # 앱 Enhanced에서 document manager 가져오기
                if hasattr(st.session_state, 'doc_manager'):
                    doc_manager = st.session_state.doc_manager
                else:
                    # 동적으로 문서 관리 서비스 생성
                    from services.document_management_service import DocumentManagementService
                    doc_manager = DocumentManagementService()
                
                result = doc_manager.save_generated_document(
                    content=content,
                    title=document_title.strip(),
                    document_id=doc.get('id') if doc.get('type') == 'existing' else None,
                    metadata={
                        "editor_created": True,
                        "word_count": len(content.split()),
                        "char_count": len(content)
                    }
                )
                
                if result['success']:
                    st.success(f"✅ '{document_title}' 문서가 저장되었습니다!")
                    
                    # 문서 정보 업데이트
                    doc['title'] = document_title.strip()
                    doc['type'] = 'existing'
                    
                    # 저장 다이얼로그 닫기
                    st.session_state.show_save_dialog = False
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"❌ 저장 실패: {', '.join(result.get('errors', ['Unknown error']))}")
                    
            except Exception as e:
                st.error(f"❌ 저장 중 오류: {str(e)}")
        
        elif save_clicked and not document_title.strip():
            st.error("❌ 문서 제목을 입력해주세요.")
        
        elif cancel_clicked:
            st.session_state.show_save_dialog = False
            st.rerun()

def _save_document(doc):
    """문서 저장 기능 (이전 버전 - 사용하지 않음)"""
    pass

def _show_ai_status_check():
    """AI 상태 확인 표시"""
    with st.spinner("AI 연결 상태 확인 중..."):
        from services.ai_analysis_orchestrator import AIAnalysisOrchestrator
        orchestrator = AIAnalysisOrchestrator()
        
        st.markdown("### 🔍 AI 서비스 상태")
        
        # 연결 상태 표시
        if orchestrator.azure_search.available and orchestrator.openai_client:
            st.success("✅ Azure OpenAI 연결됨")
            st.info(f"🤖 모델: GPT-4o\n📍 Azure OpenAI 서비스")
            st.success("✅ AI 분석 오케스트레이터 준비 완료")
        else:
            st.error("❌ AI 서비스 연결 실패")
            st.warning("⚠️ Azure OpenAI 또는 Azure Search 설정을 확인해주세요.")
        
        # 기타 서비스 상태
        if orchestrator.azure_search.available:
            st.success("✅ Azure AI Search 활성화됨")
        else:
            st.warning("⚠️ Azure AI Search 비활성화됨")
        
        # Tavily API 상태 확인
        import os
        if os.getenv("TAVILY_API_KEY"):
            st.success("✅ Tavily 검색 API 활성화됨")
        else:
            st.warning("⚠️ Tavily 검색 API 비활성화됨")