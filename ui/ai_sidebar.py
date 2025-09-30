"""
AI Sidebar UI Component - Enhanced 4-step Analysis Process
새로운 요구사항에 맞춘 AI 분석 사이드바
"""
import streamlit as st
from state.session_state import session_state
from services.ai_analysis_orchestrator_refactored import AIAnalysisOrchestrator
from core.utils import show_message

def render_ai_sidebar():
    """AI sidebar panel with enhance        # 사용자 안내
        st.info("💡 메인 페이지의 문서 내용을 확인해보세요! 분석 결과가 추가되었습니다.")
        st.warning("⚠️ 내용이 보이지 않으면 브라우저 새로고침(F5)을 해보세요.")
        
        return True
            
    except Exception as e:
        st.error(f"❌ 문서 삽입 실패: {str(e)}")
        print(f"[ERROR] 삽입 실패: {str(e)}")
        return Falseanalysis process"""
    if not st.session_state.get('ai_panel_open', False):
        return
    
    st.markdown("## 🤖 AI 문서 분석")
    st.markdown("*4단계 AI 분석 프로세스*")
    st.markdown("---")
    
    # 분석 모드 표시 (자동 설정됨)
    analysis_mode = st.session_state.get('analysis_mode', 'manual')
    if analysis_mode == 'full_document':
        st.info("📄 **전체 문서 분석 모드**")
        analysis_text = st.session_state.get('document_content', '')
    elif analysis_mode == 'selected_text':
        st.info("🎯 **선택된 텍스트 분석 모드**")
        analysis_text = st.session_state.get('selected_text', '')
    else:
        st.info("⚙️ **수동 분석 모드**")
        analysis_text = None
    
    # 분석 대상 텍스트 미리보기
    if analysis_text:
        with st.expander("📝 분석 대상 텍스트 미리보기"):
            preview_text = analysis_text[:500]
            if len(analysis_text) > 500:
                preview_text += "... (더보기)"
            st.markdown(f"```\n{preview_text}\n```")
            st.caption(f"전체 길이: {len(analysis_text):,}자 | {len(analysis_text.split()):,}단어")
    
    # 분석 목적/질문 입력 (선택사항)
    user_input = st.text_area(
        "🎯 분석 목적 및 질문 (선택사항):",
        placeholder="🔹 특별한 분석 요청이 있으면 입력하세요\n🔹 비워두면 기본 종합 분석을 수행합니다\n\n예시:\n- 특정 관점에서 분석해주세요\n- 특정 부분에 집중해서 분석해주세요\n- 특정 목적을 위한 개선점을 찾아주세요",
        height=120,
        key="ai_sidebar_user_input",
        help="입력하지 않아도 기본적인 문서 분석이 자동으로 수행됩니다."
    )
    
    # 기본 분석 질문 미리보기
    if not user_input or not user_input.strip():
        default_query = _get_default_analysis_query(analysis_mode or 'manual')
        with st.expander("🔍 기본 분석 질문 미리보기"):
            st.markdown(f"**현재 사용될 기본 질문:**\n{default_query}")
            st.caption("위 질문으로 분석이 진행됩니다. 다른 질문을 원하시면 위 입력창에 작성해주세요.")
    
    # 자동 시작 분석인 경우 바로 실행 (기본 질문 사용)
    if st.session_state.get('auto_start_analysis', False):
        st.session_state.auto_start_analysis = False
        if analysis_text:
            # 사용자 입력이 없으면 기본 분석 질문 사용
            default_query = _get_default_analysis_query(analysis_mode)
            final_query = user_input.strip() if user_input.strip() else default_query
            _execute_analysis(final_query, analysis_text, analysis_mode)
    
    # 수동 분석 시작 버튼
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 AI 분석 실행", key="ai_sidebar_analyze", use_container_width=True):
            # 분석 대상 텍스트 확인
            target_text = analysis_text
            if not target_text:
                # 수동 모드에서는 현재 문서 내용 사용
                target_text = st.session_state.get('document_content', '')
                if not target_text:
                    st.error("❌ 분석할 내용이 없습니다. 문서를 작성해주세요.")
                    return
            
            # 사용자 입력이 없으면 기본 분석 질문 사용
            default_query = _get_default_analysis_query(analysis_mode or 'manual')
            final_query = user_input.strip() if user_input.strip() else default_query
            
            if not final_query:
                st.error("❌ 분석 질문을 생성할 수 없습니다.")
                return
            
            _execute_analysis(final_query, target_text, analysis_mode or 'manual')
    
    with col2:
        if st.button("❌ 패널 닫기", key="close_ai_panel_sidebar", use_container_width=True):
            _close_ai_panel()
    
    # 분석 결과 표시 영역
    _render_analysis_results()

def _execute_analysis(user_input: str, analysis_text: str, mode: str):
    """AI 분석 실행"""
    st.session_state.analysis_in_progress = True
    
    # 분석 모드와 텍스트 결정
    if mode == 'selected_text':
        orchestrator_mode = "selection"
        selection = analysis_text
    elif mode == 'full_document':
        orchestrator_mode = "full"
        # 전체 문서 분석시에는 문서 내용을 selection으로 전달
        selection = analysis_text
    else:
        orchestrator_mode = "full"
        # 수동 모드에서는 현재 문서 내용 사용
        selection = st.session_state.get('document_content', '') or analysis_text
    
    orchestrator = AIAnalysisOrchestrator(mode=orchestrator_mode)
    
    try:
        st.markdown("---")
        st.markdown("### 🔄 AI 분석 진행 상황")
        
        # 4단계 분석 실행 - selection에 실제 분석할 텍스트 전달
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
        with st.expander("� 오류 상세 정보"):
            st.exception(e)

def _render_analysis_results():
    """분석 결과 렌더링 - 개선된 UI"""
    current_result = st.session_state.get('current_analysis_result')
    
    if not current_result:
        return
    
    st.markdown("---")
    
    # 4단계 프로세스를 접을 수 있는 토글로 구성
    process_collapsed = st.session_state.get('process_collapsed', True)  # 기본값: 접힌 상태
    
    # 토글 버튼
    if st.button(
        f"{'📂 4단계 프로세스 펼치기' if process_collapsed else '📁 4단계 프로세스 접기'}", 
        key="toggle_process_view",
        use_container_width=True
    ):
        st.session_state.process_collapsed = not process_collapsed
        st.rerun()
    
    # 4단계 프로세스 내용 (토글 상태에 따라 표시)
    if not process_collapsed:
        with st.container():
            st.markdown("### � AI 분석 4단계 프로세스")
            _display_step_details(current_result)
            st.markdown("---")
    
    # 메인 분석 결과 (항상 표시)
    st.markdown("### 🎯 최종 분석 결과")
    
    final_result = current_result.get('result', '')
    if final_result:
        # 결과 미리보기
        preview_length = 200
        preview_text = final_result[:preview_length]
        if len(final_result) > preview_length:
            preview_text += "..."
        
        # 결과 표시 영역
        result_container = st.container()
        with result_container:
            st.markdown("#### 📄 분석 요약")
            st.info(preview_text)
            
            # 액션 버튼들
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📖 전체 결과 보기", key="view_full_result", use_container_width=True):
                    _show_full_content_popup("AI 분석 결과", final_result)
            
            with col2:
                if st.button("📝 문서에 삽입", key="insert_result_to_doc", use_container_width=True):
                    _insert_content_to_document(final_result, "AI 분석 결과")
    
    # 레퍼런스 결과 표시
    _display_enhanced_references(current_result)

def _display_enhanced_references(analysis_result):
    """향상된 레퍼런스 표시 (150자 미리보기 + 전체보기 링크)"""
    internal_refs = analysis_result.get('internal_refs', [])
    external_refs = analysis_result.get('external_refs', [])
    
    # 디버깅 정보 추가
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
    
    st.markdown("#### 📚 참고 자료")
    
    # 사내 문서
    if internal_refs:
        st.markdown("**📁 사내 문서**")
        for i, ref in enumerate(internal_refs[:5], 1):
            title = ref.get('title', 'N/A')
            content = ref.get('content', '')
            
            # 제목 표시
            st.markdown(f"**{i}. {title}**")
            
            # 150자 미리보기
            if content:
                preview = content[:150]
                if len(content) > 150:
                    preview += "..."
                st.markdown(f"*{preview}*")
                
                # 전체보기 버튼
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
            
            # 제목과 출처 표시
            st.markdown(f"**{i}. {title}**")
            if source:
                st.caption(f"출처: {source}")
            
            # 150자 미리보기
            if content:
                preview = content[:150]
                if len(content) > 150:
                    preview += "..."
                st.markdown(f"*{preview}*")
                
                # 전체보기 버튼
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
    """전체 내용을 새 창에서 보기 (모달 형태)"""
    # Streamlit에서는 실제 새 창을 열 수 없으므로 확장 가능한 영역으로 표시
    with st.expander(f"📄 {title} - 전체 내용", expanded=True):
        st.markdown(content)
        
        # 복사 버튼 (다운로드 형태)
        st.download_button(
            label="📋 텍스트 복사",
            data=content,
            file_name=f"{title.replace(':', '_')}.txt",
            mime="text/plain",
            key=f"download_{hash(title)}"
        )

def _insert_content_to_document(content: str, content_type: str):
    """문서에 내용 삽입 - 디버깅 강화 버전"""
    try:
        # 문서 내용이 있는지 확인
        current_content = st.session_state.get('document_content', '')
        
        if current_content is None:
            current_content = ''
        
        # 현재 시간 추가로 중복 방지
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # 삽입할 내용 구성
        insert_content = f"\n\n## {content_type} ({timestamp})\n\n{content}\n\n"
        new_content = current_content + insert_content
        
        # 디버깅 정보
        print(f"[DEBUG] 삽입 시작 - 기존 길이: {len(current_content)}, 삽입 길이: {len(insert_content)}")
        
        # 세션 상태에 새 내용 저장
        st.session_state.document_content = new_content
        
        # 삽입 완료 플래그 설정 - 지속적으로 유지되도록
        st.session_state.insert_completed = True
        st.session_state.insert_success_message = f"✅ {content_type}가 문서에 삽입되었습니다!"
        st.session_state.inserted_content_length = len(insert_content)
        st.session_state.last_insert_timestamp = timestamp
        st.session_state.force_textarea_update = True  # textarea 강제 업데이트
        
        # 즉시 피드백 제공
        st.success("✅ 문서에 삽입 완료!")
        st.info(f"📝 추가된 내용: {len(insert_content):,}자")
        
        # 디버깅 정보 표시
        with st.expander("🔍 삽입 상세 정보 (디버깅)"):
            st.write(f"- 기존 문서 길이: {len(current_content):,}자")
            st.write(f"- 삽입된 내용 길이: {len(insert_content):,}자")
            st.write(f"- 최종 문서 길이: {len(new_content):,}자")
            st.write(f"- 세션 상태 키: {list(st.session_state.keys())}")
        
        print(f"[DEBUG] 삽입 완료 - 최종 길이: {len(new_content)}")
        
        # 성공 피드백 - rerun 없이
        st.balloons()  # 성공 시각적 피드백
        
        # 메인 페이지에서 확인할 수 있도록 안내
        st.info("� **메인 페이지의 문서 내용을 확인해보세요!** 분석 결과가 추가되었습니다.")
            
    except Exception as e:
        error_msg = f"❌ 문서 삽입 중 오류: {str(e)}"
        st.error(error_msg)
        print(f"[ERROR] 삽입 실패: {str(e)}")
        # 오류 상세 정보를 세션에 저장
        st.session_state.insert_error_message = f"삽입 실패: {str(e)}"

def _get_default_analysis_query(mode: str) -> str:
    """분석 모드에 따른 기본 질문 생성"""
    if mode == 'full_document':
        return "이 문서의 핵심 내용을 요약하고, 주요 포인트와 개선점을 분석해주세요. 관련된 참고 자료나 추가 정보도 함께 제공해주세요."
    elif mode == 'selected_text':
        return "선택된 텍스트 내용을 분석하고, 핵심 의미와 개선 방향을 제시해주세요. 관련 참고 자료도 찾아주세요."
    else:
        return "제공된 문서 내용을 종합적으로 분석하고, 주요 인사이트와 개선점을 도출해주세요."

def _close_ai_panel():
    """AI 패널 닫기"""
    st.session_state.ai_panel_open = False
    st.session_state.analysis_mode = None
    st.session_state.analysis_text = ""
    st.session_state.analysis_in_progress = False
    st.session_state.auto_start_analysis = False
    st.session_state.current_analysis_result = None
    st.rerun()

def render_analysis_popup():
    """Analysis result popup (compatibility function)"""
    # 새로운 사이드바 방식으로 통합됨
    pass