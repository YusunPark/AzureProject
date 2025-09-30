"""
ai_analysis_ui.py

개선된 AI 분석 기능 UI - 4단계 프로세스 표시
- 진행 상황 표시, 분석 취소, 결과/레퍼런스 확인, 문서 삽입 등
"""
import streamlit as st
from services.ai_analysis_orchestrator_refactored import AIAnalysisOrchestrator
from core.utils import show_message

def ai_analysis_page():
    """AI 분석 메인 페이지"""
    st.title("🤖 AI 문서 분석")
    st.markdown("### 새로운 4단계 AI 분석 프로세스")
    st.markdown("**1단계:** 프롬프트 고도화 → **2단계:** 검색 쿼리 생성 → **3단계:** 병렬 검색 → **4단계:** 최종 분석")
    
    # 분석 설정 섹션
    st.markdown("---")
    st.markdown("#### 🔧 분석 설정")
    
    # 사용자 입력
    user_input = st.text_area(
        "분석 목적/질문 입력:",
        placeholder="예: 이 문서의 핵심 내용을 요약하고, 개선점과 실행 방안을 제시해주세요.",
        height=100,
        help="구체적이고 명확한 질문일수록 더 정확한 분석 결과를 얻을 수 있습니다."
    )
    
    # 분석 모드 선택
    col1, col2 = st.columns(2)
    with col1:
        mode = st.radio(
            "분석 모드 선택:",
            ["전체 문서 분석", "선택 텍스트 분석"],
            help="전체 문서: 현재 열린 문서 전체를 분석\n선택 텍스트: 지정한 텍스트만 분석"
        )
    
    with col2:
        # 분석 타입 (향후 확장을 위한 옵션)
        analysis_type = st.selectbox(
            "분석 유형:",
            ["종합 분석", "요약 분석", "개선점 분석"],
            help="분석의 초점을 선택합니다"
        )
    
    # 선택 텍스트 입력 (선택 모드일 때)
    selection = ""
    if mode == "선택 텍스트 분석":
        selection = st.text_area(
            "분석할 텍스트 입력:",
            placeholder="분석할 텍스트를 여기에 입력하거나 붙여넣기 하세요...",
            height=150
        )
    
    # 분석 실행 섹션
    st.markdown("---")
    st.markdown("#### 🚀 분석 실행")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if st.button("🤖 AI 분석 시작", use_container_width=True, type="primary"):
            # 입력 유효성 검사
            if not user_input or not user_input.strip():
                show_message("error", "분석 목적이나 질문을 입력해주세요.")
                return
            
            if mode == "선택 텍스트 분석" and (not selection or not selection.strip()):
                show_message("error", "분석할 텍스트를 입력해주세요.")
                return
                
            # AI 분석 실행
            _run_enhanced_ai_analysis(user_input.strip(), mode, selection.strip() if selection else None, analysis_type)
    
    with col2:
        if st.button("🔄 새로고침", use_container_width=True):
            st.rerun()
    
    with col3:
        if st.button("🗑️ 초기화", use_container_width=True):
            _clear_analysis_state()
            st.rerun()
    
    # 분석 결과 표시 섹션
    _display_analysis_results()

def _run_enhanced_ai_analysis(user_input: str, mode: str, selection: str = None, analysis_type: str = "종합 분석"):
    """개선된 AI 분석 실행"""
    try:
        # 분석 모드 설정
        analysis_mode = "selection" if mode == "선택 텍스트 분석" else "full"
        
        # 오케스트레이터 초기화 및 분석 실행
        orchestrator = AIAnalysisOrchestrator(mode=analysis_mode)
        
        st.markdown("---")
        st.markdown("### 🔄 AI 분석 진행 상황")
        
        # 4단계 분석 실행 (진행 상황이 자동으로 표시됨)
        analysis_result = orchestrator.run_complete_analysis(
            user_input=user_input,
            selection=selection
        )
        
        # 성공 메시지
        st.balloons()  # 성공 축하 애니메이션
        show_message("success", "🎉 AI 분석이 성공적으로 완료되었습니다!")
        
    except Exception as e:
        show_message("error", f"분석 중 오류가 발생했습니다: {str(e)}")
        with st.expander("🔍 오류 상세 정보 (개발자용)"):
            st.exception(e)

def _display_analysis_results():
    """분석 결과 표시"""
    # 세션 상태에서 분석 결과 확인
    if st.session_state.get("ai_analysis_result"):
        st.markdown("---")
        st.markdown("## 📊 AI 분석 결과")
        
        # 결과 미리보기
        result = st.session_state["ai_analysis_result"]
        
        # 탭으로 결과 구분
        tab1, tab2, tab3 = st.tabs(["📋 분석 결과", "📚 참고 자료", "⚙️ 설정"])
        
        with tab1:
            st.markdown(result)
            
            # 문서 삽입 버튼
            col1, col2 = st.columns(2)
            with col1:
                if st.button("� 문서에 삽입", use_container_width=True):
                    _insert_result_to_document(result)
            
            with col2:
                if st.button("📋 클립보드 복사", use_container_width=True):
                    st.write("클립보드 복사 기능은 브라우저에서 지원됩니다.")
        
        with tab2:
            _display_references_tab()
            
        with tab3:
            st.markdown("#### 분석 설정 요약")
            st.json({
                "분석_모드": st.session_state.get("last_analysis_mode", "N/A"),
                "분석_시간": st.session_state.get("last_analysis_time", "N/A"),
                "참고자료_수": {
                    "사내문서": len(st.session_state.get("ai_analysis_references", {}).get("internal", [])),
                    "외부자료": len(st.session_state.get("ai_analysis_references", {}).get("external", []))
                }
            })

def _display_references_tab():
    """참고 자료 탭 표시"""
    references = st.session_state.get("ai_analysis_references", {"internal": [], "external": []})
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📁 사내 문서")
        internal_refs = references.get("internal", [])
        if internal_refs:
            for i, ref in enumerate(internal_refs, 1):
                with st.expander(f"{i}. {ref.get('title', 'N/A')}"):
                    st.markdown(f"**내용:** {ref.get('content', 'N/A')[:200]}...")
                    st.markdown(f"**점수:** {ref.get('relevance_score', 'N/A')}")
        else:
            st.info("사내 문서가 없습니다.")
    
    with col2:
        st.markdown("### 🌐 외부 자료")
        external_refs = references.get("external", [])
        if external_refs:
            for i, ref in enumerate(external_refs, 1):
                with st.expander(f"{i}. {ref.get('title', 'N/A')}"):
                    st.markdown(f"**내용:** {ref.get('content', 'N/A')[:200]}...")
                    if ref.get('url'):
                        st.markdown(f"**링크:** [{ref.get('title', 'N/A')}]({ref.get('url')})")
        else:
            st.info("외부 자료가 없습니다.")

def _insert_result_to_document(result: str):
    """분석 결과를 문서에 삽입"""
    if 'document_content' in st.session_state:
        current_content = st.session_state.document_content
        insert_content = f"\n\n## 🤖 AI 분석 결과\n\n{result}\n\n"
        st.session_state.document_content = current_content + insert_content
        show_message("success", "✅ 분석 결과가 문서에 삽입되었습니다!")
        st.rerun()
    else:
        show_message("warning", "활성 문서가 없습니다. 먼저 문서를 생성하거나 열어주세요.")

def _clear_analysis_state():
    """분석 상태 초기화"""
    keys_to_clear = [
        "ai_analysis_result",
        "ai_analysis_references", 
        "ai_analysis_progress",
        "ai_analysis_status",
        "last_analysis_hash",
        "last_analysis_mode",
        "last_analysis_time"
    ]
    
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    
    show_message("info", "🧹 분석 상태가 초기화되었습니다.")
