"""
문서 생성 UI 컴포넌트 - 개선된 버전
"""
import streamlit as st
import time
from state.session_state import session_state
from datetime import datetime

def render_document_creation():
    """개선된 문서 생성 인터페이스 렌더링"""
    st.markdown("## 📝 AI 문서 작성 어시스턴트")
    st.markdown("---")
    
    # 문서 제목 입력
    st.markdown("### 📄 문서 정보")
    document_title = st.text_input(
        "문서 제목",
        value=st.session_state.get('current_document_title', ''),
        placeholder="문서 제목을 입력하세요...",
        key="document_title_input"
    )
    
    # 제목이 변경되면 세션에 저장
    if document_title != st.session_state.get('current_document_title', ''):
        st.session_state.current_document_title = document_title
    
    # AI 분석 버튼들 (메인 기능) - 상단으로 이동
    st.markdown("### 🤖 AI 분석 기능")
    
    # AI 패널이 열려있지 않을 때만 버튼들 표시
    if not st.session_state.get('ai_panel_open', False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button(
                "📄 전체분석하기", 
                type="primary", 
                use_container_width=True,
                help="문서 전체 내용을 기반으로 AI 분석을 수행합니다"
            ):
                # 현재 문서 내용 가져오기 (아래에서 정의되기 전에 세션에서 가져옴)
                current_content = st.session_state.get('document_content', '')
                if current_content and current_content.strip():
                    _start_full_analysis(current_content.strip())
                else:
                    st.warning("⚠️ 먼저 아래 문서 내용을 입력해주세요.")
        
        with col2:
            if st.button(
                "🎯 선택내용 분석하기", 
                type="secondary", 
                use_container_width=True,
                help="선택된 텍스트만을 대상으로 AI 분석을 수행합니다"
            ):
                # 현재 선택된 텍스트 가져오기
                current_selected = st.session_state.get('selected_text', '')
                if current_selected and current_selected.strip():
                    _start_selected_analysis(current_selected.strip())
                else:
                    st.warning("⚠️ 먼저 아래 선택 영역에 분석할 텍스트를 입력해주세요.")
        
        with col3:
            if st.button(
                "⚙️ 고급 분석 설정",
                use_container_width=True,
                help="상세한 분석 옵션을 설정할 수 있습니다"
            ):
                st.session_state.ai_panel_open = True
                st.session_state.analysis_mode = "manual"
                st.rerun()
        
        # 분석 상태 정보 표시
        if st.session_state.get('analysis_in_progress', False):
            st.info("🔄 AI 분석이 진행 중입니다...")
    
    else:
        # AI 패널이 열려있을 때는 간단한 안내만
        st.info("🤖 AI 분석 패널이 활성화되어 있습니다. 우측 사이드바를 확인하세요.")
        
        if st.button("❌ AI 패널 닫기", key="close_ai_panel_main"):
            _close_ai_panel()
    
    st.markdown("---")
    
    # 문서 내용 입력 영역
    st.markdown("### ✍️ 문서 내용")
    document_content = st.text_area(
        "문서 내용을 입력하세요:",
        value=st.session_state.get('document_content', ''),
        placeholder="여기에 문서 내용을 작성하세요...",
        height=350,
        key="document_content_main_editor"
    )
    
    # 문서 내용이 변경되면 세션에 저장
    if document_content != st.session_state.get('document_content', ''):
        st.session_state.document_content = document_content
    
    # 텍스트 선택 영역 (선택내용 분석용)
    st.markdown("### 🎯 텍스트 선택 (부분 분석용)")
    selected_text = st.text_area(
        "분석할 텍스트를 여기에 붙여넣으세요:",
        value=st.session_state.get('selected_text', ''),
        placeholder="위 문서에서 특정 부분을 복사해서 여기에 붙여넣으면 해당 부분만 분석할 수 있습니다.",
        height=120,
        key="selected_text_area"
    )
    
    # 선택된 텍스트가 변경되면 세션에 저장
    if selected_text != st.session_state.get('selected_text', ''):
        st.session_state.selected_text = selected_text
    
    # 빠른 통계 표시
    _render_quick_stats(document_content, selected_text)
    
    # 문서 관리 기능
    st.markdown("---")
    st.markdown("### 💾 문서 관리")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("� 저장", type="primary", use_container_width=True):
            if document_title and document_content:
                _save_document(document_title, document_content)
            else:
                st.error("제목과 내용을 모두 입력해주세요.")
    
    with col2:
        if st.button("📤 내보내기", use_container_width=True):
            if document_content:
                filename = f"{document_title or 'document'}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
                st.download_button(
                    label="📄 TXT 다운로드",
                    data=document_content,
                    file_name=filename,
                    mime="text/plain",
                    key="download_document"
                )
            else:
                st.warning("내보낼 내용이 없습니다.")
    
    with col3:
        if st.button("📋 템플릿", use_container_width=True):
            _insert_template()
    
    with col4:
        if st.button("� 새로 시작", use_container_width=True):
            _reset_document()
    
    # 템플릿/파일 로드 기능들
    if st.session_state.get('show_template_options', False):
        _render_template_options()
    
    if st.session_state.get('show_file_upload', False):
        _render_file_upload()

def _start_full_analysis(content: str):
    """전체 문서 분석 시작"""
    st.session_state.ai_panel_open = True
    st.session_state.analysis_mode = "full_document"
    st.session_state.analysis_text = content
    st.session_state.analysis_in_progress = True
    st.session_state.auto_start_analysis = True
    
    st.success("📄 전체 문서 분석을 시작합니다...")
    st.rerun()

def _start_selected_analysis(content: str):
    """선택된 텍스트 분석 시작"""
    st.session_state.ai_panel_open = True
    st.session_state.analysis_mode = "selected_text" 
    st.session_state.analysis_text = content
    st.session_state.analysis_in_progress = True
    st.session_state.auto_start_analysis = True
    
    st.success("🎯 선택된 텍스트 분석을 시작합니다...")
    st.rerun()

def _render_quick_stats(document_content: str, selected_text: str):
    """빠른 통계 표시"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        doc_words = len(document_content.split()) if document_content else 0
        st.metric("📄 문서 단어수", f"{doc_words:,}")
    
    with col2:
        doc_chars = len(document_content) if document_content else 0
        st.metric("📝 문서 글자수", f"{doc_chars:,}")
    
    with col3:
        sel_words = len(selected_text.split()) if selected_text else 0
        st.metric("🎯 선택 단어수", f"{sel_words:,}")
    
    with col4:
        sel_chars = len(selected_text) if selected_text else 0
        st.metric("✂️ 선택 글자수", f"{sel_chars:,}")

def _insert_template():
    """템플릿 삽입"""
    st.session_state.show_template_options = True
    st.rerun()

def _render_template_options():
    """템플릿 선택 옵션"""
    st.markdown("---")
    st.markdown("#### 📋 문서 템플릿 선택")
    
    templates = {
        "business_proposal": {
            "name": "사업 제안서",
            "content": """# 사업 제안서

## 1. 제안 개요
- 제안 목적:
- 제안 범위:
- 예상 효과:

## 2. 현황 분석
- 현재 상황:
- 문제점 분석:
- 개선 필요사항:

## 3. 제안 내용
- 주요 제안사항:
- 구현 방법:
- 기대 효과:

## 4. 실행 계획
- 추진 일정:
- 소요 자원:
- 위험 관리:

## 5. 결론
- 요약:
- 기대 효과:
- 승인 요청사항:
"""
        },
        "meeting_minutes": {
            "name": "회의록", 
            "content": """# 회의록

## 회의 정보
- 일시: 
- 장소:
- 참석자:
- 주관:

## 안건
1. 
2. 
3. 

## 논의 내용

### 안건 1: 
- 논의 사항:
- 결정 사항:
- 액션 아이템:

### 안건 2:
- 논의 사항:
- 결정 사항:  
- 액션 아이템:

## 차기 회의
- 일정:
- 안건:
"""
        },
        "project_report": {
            "name": "프로젝트 보고서",
            "content": """# 프로젝트 보고서

## 프로젝트 개요
- 프로젝트명:
- 기간:
- 담당자:

## 진행 현황
- 전체 진척도: %
- 주요 성과:
- 완료된 업무:

## 주요 이슈 및 해결방안
- 이슈 1:
  - 내용:
  - 해결방안:
- 이슈 2:
  - 내용:
  - 해결방안:

## 향후 계획
- 단기 계획:
- 중장기 계획:
- 필요 자원:

## 결론 및 건의사항
"""
        }
    }
    
    selected_template = st.selectbox(
        "템플릿을 선택하세요:",
        options=list(templates.keys()),
        format_func=lambda x: templates[x]["name"]
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📝 템플릿 적용", type="primary"):
            template_content = templates[selected_template]["content"]
            st.session_state.document_content = template_content
            st.session_state.show_template_options = False
            st.success(f"✅ {templates[selected_template]['name']} 템플릿이 적용되었습니다!")
            st.rerun()
    
    with col2:
        if st.button("❌ 취소"):
            st.session_state.show_template_options = False
            st.rerun()

def _save_document(title: str, content: str):
    """문서 저장"""
    try:
        doc_manager = st.session_state.get('doc_manager')
        if doc_manager:
            result = doc_manager.save_generated_document(
                content=content,
                title=title,
                metadata={
                    "created_from": "enhanced_document_creation",
                    "word_count": len(content.split()),
                    "char_count": len(content),
                    "created_at": datetime.now().isoformat()
                }
            )
            
            if result['success']:
                st.success(f"✅ '{title}' 문서가 저장되었습니다!")
                # 저장 후 현재 문서 정보 업데이트
                st.session_state.last_saved_title = title
                st.session_state.last_saved_time = datetime.now().strftime("%H:%M")
            else:
                st.error(f"❌ 저장 실패: {', '.join(result['errors'])}")
        else:
            st.error("문서 관리 서비스를 사용할 수 없습니다.")
    
    except Exception as e:
        st.error(f"문서 저장 중 오류: {str(e)}")

def _reset_document():
    """문서 초기화"""
    st.session_state.document_content = ""
    st.session_state.selected_text = ""
    st.session_state.current_document_title = ""
    st.session_state.analysis_in_progress = False
    
    # AI 관련 상태도 초기화
    if st.session_state.get('ai_panel_open', False):
        _close_ai_panel()
    
    st.success("🔄 새 문서로 초기화되었습니다!")
    st.rerun()

def _close_ai_panel():
    """AI 패널 닫기"""
    st.session_state.ai_panel_open = False
    st.session_state.analysis_mode = None
    st.session_state.analysis_text = ""
    st.session_state.analysis_in_progress = False
    st.session_state.auto_start_analysis = False
    st.rerun()

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