"""
AI Sidebar UI Component - Enhanced 4-step Analysis Process
새로운 요구사항에 맞춘 AI 분석 사이드바
"""
import streamlit as st
from state.session_state import session_state
from services.ai_analysis_orchestrator_refactored import AIAnalysisOrchestrator
from core.utils import show_message

def render_ai_sidebar():
    """AI sidebar panel with enhanced analysis process"""
    if not st.session_state.get('ai_panel_open', False):
        return

    with st.sidebar:
        # 헤더
        st.markdown("## 🤖 AI 분석")
        
        # 분석 모드 표시
        mode = st.session_state.get('analysis_mode', 'unknown')
        mode_text = {
            'full_document': '📄 전체 문서',
            'selected_text': '📝 선택 텍스트',
            'custom': '🎯 사용자 정의'
        }.get(mode, '🔍 일반 분석')
        
        st.info(f"**분석 모드**: {mode_text}")
        
        # 닫기 버튼
        if st.button("❌ 분석 패널 닫기", use_container_width=True):
            _close_ai_panel()
            st.rerun()
        
        # 분석 취소 버튼 (진행 중일 때만)
        if st.session_state.get('analysis_in_progress', False):
            if st.button("🛑 분석 중단", use_container_width=True):
                st.session_state.analysis_in_progress = False
                st.warning("분석이 중단되었습니다.")
                st.rerun()
        
        # 분석 실행
        if st.session_state.get('auto_start_analysis', False):
            _run_ai_analysis()
        
        # 분석 결과 표시
        _render_analysis_results()

def _run_ai_analysis():
    """AI 분석 실행"""
    # 분석할 텍스트 준비
    user_input = st.session_state.get('analysis_text', '')
    selection = st.session_state.get('selected_text', '')
    
    # 오케스트레이터 모드 결정
    mode = st.session_state.get('analysis_mode', 'full_document')
    orchestrator_mode = 'selected_text' if mode == 'selected_text' else 'full_document'
    
    if not user_input and not selection:
        st.error("❌ 분석할 내용이 없습니다.")
        st.session_state.analysis_in_progress = False
        return
    
    # 분석 실행
    st.session_state.analysis_in_progress = True
    st.session_state.auto_start_analysis = False
    
    orchestrator = AIAnalysisOrchestrator(mode=orchestrator_mode)
    
    try:
        st.markdown("---")
        st.markdown("### 🔄 AI 분석 진행 상황")
        
        # 4단계 분석 실행
        analysis_result = orchestrator.run_complete_analysis(
            user_input=user_input,
            selection=selection
        )
        
        # 분석 완료 처리
        if analysis_result and analysis_result.get('result'):
            st.session_state.analysis_in_progress = False
            st.session_state.current_analysis_result = analysis_result
            st.session_state.ai_analysis_result = analysis_result['result']
            
            # 분석 완료 알림
            st.success("🎉 **AI 분석이 완료되었습니다!**")
            st.balloons()
            
        else:
            st.error("❌ 분석 결과를 생성하지 못했습니다.")
            st.session_state.analysis_in_progress = False
            
    except Exception as e:
        st.error(f"❌ 분석 중 오류가 발생했습니다: {str(e)}")
        st.session_state.analysis_in_progress = False
        with st.expander("🔍 오류 상세 정보"):
            st.exception(e)

def _render_analysis_results():
    """분석 결과 렌더링"""
    current_result = st.session_state.get('current_analysis_result')
    
    if not current_result:
        return
    
    st.markdown("---")
    
    # 분석 진행 과정 토글
    show_progress = st.session_state.get('show_analysis_progress', False)
    
    if st.button(
        f"{'📂 분석 진행 과정 보기' if not show_progress else '📁 분석 진행 과정 접기'}", 
        key="toggle_progress_view",
        use_container_width=True,
        type="secondary"
    ):
        st.session_state.show_analysis_progress = not show_progress
        st.rerun()
    
    # 분석 진행 과정 표시
    if show_progress:
        st.markdown("### 📊 AI 분석 4단계 프로세스")
        _display_step_details(current_result)
        st.markdown("---")
    
    # 메인 분석 결과 강조 표시
    st.markdown("---")
    st.markdown("## 🎯 **최종 분석 결과**")
    
    final_result = current_result.get('result', '')
    if final_result:
        # 결과를 박스로 강조
        with st.container():
            st.markdown("""
            <div style="background-color: #f0f8ff; padding: 20px; border-radius: 10px; border-left: 5px solid #1f77b4;">
            """, unsafe_allow_html=True)
            
            st.markdown("### 📄 **분석 결과**")
            
            if len(final_result) > 300:
                preview_text = final_result[:300] + "..."
                st.markdown(preview_text)
                
                if st.checkbox("전체 결과 보기", key="show_full_result"):
                    st.markdown(final_result)
            else:
                st.markdown(final_result)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # 액션 버튼들
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📖 **상세 결과 팝업**", key="view_full_result", use_container_width=True, type="secondary"):
                    _show_full_content_popup("AI 분석 결과", final_result)
            
            with col2:
                if st.button("📝 **문서에 삽입**", key="insert_result_to_doc", use_container_width=True, type="primary"):
                    _insert_content_to_document(final_result, "AI 분석 결과")
    
    # 레퍼런스 결과 표시
    _display_enhanced_references(current_result)

def _display_enhanced_references(analysis_result):
    """향상된 레퍼런스 표시"""
    internal_refs = analysis_result.get('internal_refs', [])
    external_refs = analysis_result.get('external_refs', [])
    
    # 디버깅 정보
    with st.expander("🔍 레퍼런스 디버깅 정보", expanded=False):
        st.write(f"내부 레퍼런스 수: {len(internal_refs)}")
        st.write(f"외부 레퍼런스 수: {len(external_refs)}")
        if internal_refs:
            st.write("내부 레퍼런스 첫 번째 항목:", internal_refs[0])
        if external_refs:
            st.write("외부 레퍼런스 첫 번째 항목:", external_refs[0])
    
    if not internal_refs and not external_refs:
        st.warning("📭 검색된 참고 자료가 없습니다.")
        return
    
    # 참고 자료를 접을 수 있게 만들기
    with st.expander("📚 **참고 자료** (클릭해서 펼치기/접기)", expanded=False):
        # 사내 문서
        if internal_refs:
            st.markdown("**📁 사내 문서**")
            for i, ref in enumerate(internal_refs[:5], 1):
                title = ref.get('title', 'N/A')
                content = ref.get('content', '')
                
                st.markdown(f"**{i}. {title}**")
                
                if content:
                    preview = content[:150]
                    if len(content) > 150:
                        preview += "..."
                    st.markdown(f"*{preview}*")
                    
                    if st.button(f"📄 전체 내용 보기", key=f"view_internal_{i}"):
                        _show_full_content_popup(f"사내 문서: {title}", content)
                
                st.markdown("---")
        
        # 외부 자료
        if external_refs:
            st.markdown("**🌐 외부 자료**")
            for i, ref in enumerate(external_refs[:5], 1):
                title = ref.get('title', 'N/A')
                content = ref.get('content', '')
                source = ref.get('source_detail', '')
                
                st.markdown(f"**{i}. {title}**")
                if source:
                    st.caption(f"출처: {source}")
                
                if content:
                    preview = content[:150]
                    if len(content) > 150:
                        preview += "..."
                    st.markdown(f"*{preview}*")
                    
                    if st.button(f"🌐 전체 내용 보기", key=f"view_external_{i}"):
                        _show_full_content_popup(f"외부 자료: {title}", content)
                
                st.markdown("---")

def _display_step_details(analysis_result):
    """단계별 상세 결과 표시"""
    st.markdown("**1단계: 프롬프트 고도화**")
    enhanced_prompt = analysis_result.get('enhanced_prompt', 'N/A')
    st.markdown(f"```\n{enhanced_prompt}\n```")
    
    st.markdown("**2단계: 검색 쿼리 생성**")
    queries = analysis_result.get('queries', {})
    st.markdown(f"- 사내 검색: `{queries.get('internal', 'N/A')}`")
    st.markdown(f"- 외부 검색: `{queries.get('external', 'N/A')}`")
    
    st.markdown("**3단계: 레퍼런스 검색 결과**")
    internal_count = len(analysis_result.get('internal_refs', []))
    external_count = len(analysis_result.get('external_refs', []))
    st.markdown(f"- 사내 문서: {internal_count}개")
    st.markdown(f"- 외부 자료: {external_count}개")

def _show_full_content_popup(title: str, content: str):
    """전체 내용 팝업 표시"""
    st.markdown(f"### {title}")
    st.markdown(content)

def _insert_content_to_document(content: str, content_type: str):
    """문서에 내용 삽입"""
    try:
        # 현재 문서 내용 가져오기
        current_content = st.session_state.get('document_content', '')
        if current_content is None:
            current_content = ''
        
        # 타임스탬프 생성
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 삽입할 내용 구성
        insert_content = f"\n\n## 📋 {content_type} ({timestamp})\n\n{content}\n\n"
        new_content = current_content + insert_content
        
        # 세션 상태 업데이트 (가장 중요!)
        st.session_state.document_content = new_content
        
        # 삽입 성공 표시
        st.success(f"✅ {content_type} 삽입 완료!")
        st.info(f"📝 추가된 내용: {len(insert_content):,}자")
        
        # 삽입된 내용 미리보기
        with st.expander("📄 삽입된 내용 미리보기 (클릭해서 확인)"):
            st.markdown(insert_content)
        
        # 시각적 피드백
        st.balloons()
        
        # 사용자 안내
        st.info("💡 메인 페이지의 문서 내용을 확인해보세요! 분석 결과가 추가되었습니다.")
        st.warning("⚠️ 내용이 보이지 않으면 브라우저 새로고침(F5)을 해보세요.")
        
        print(f"[DEBUG] 삽입 완료 - {len(insert_content):,}자 추가됨")
        
        return True
        
    except Exception as e:
        st.error(f"❌ 문서 삽입 실패: {str(e)}")
        print(f"[ERROR] 삽입 실패: {str(e)}")
        return False

def _close_ai_panel():
    """AI 패널 닫기"""
    st.session_state.ai_panel_open = False
    st.session_state.analysis_mode = None
    st.session_state.analysis_text = ""
    st.session_state.analysis_in_progress = False
    st.session_state.auto_start_analysis = False
    st.session_state.current_analysis_result = None

def render_analysis_popup():
    """Analysis result popup (compatibility function)"""
    # 새로운 사이드바 방식으로 통합됨
    pass