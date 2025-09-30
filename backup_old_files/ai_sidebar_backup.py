"""
향상된 AI 사이드바 UI 컴포넌트
"""
import streamlit as st
from state.session_state import session_state
from services.enhanced_ai_analysis_service import EnhancedAIAnalysisService, render_analysis_popup

def render_ai_sidebar()        with col1:
            if st.button("📝 요약만 삽입", key="insert_summary_only"):
                try:
                    # 첫 번째 섹션만 추출 (## 이전까지 또는 첫 200자)
                    summary_lines = final_analysis.split('\n\n')
                    if len(summary_lines) > 0:
                        summary = summary_lines[0][:200] + ("..." if len(summary_lines[0]) > 200 else "")
                    else:
                        summary = final_analysis[:200] + ("..." if len(final_analysis) > 200 else "")
                    
                    _insert_to_document(summary, "AI 분석 요약")
                except Exception as e:
                    st.error(f"요약 삽입 실패: {e}")
        
        with col2:
            if st.button("📄 전체 결과 삽입", key="insert_full_result"):
                try:
                    _insert_to_document(final_analysis, "AI 분석 전체")
                except Exception as e:
                    st.error(f"전체 삽입 실패: {e}")향상된 AI 사이드바 패널 렌더링"""
    if not st.session_state.get('ai_panel_open', False):
        return
    
    st.markdown("## 🤖 AI 문서 분석")
    
    # 현재 분석 모드 표시
    analysis_mode = st.session_state.get('analysis_mode', 'manual')
    
    if analysis_mode == "full_document":
        st.success("📄 **전체 문서 분석 모드**")
        st.caption("문서 전체 내용을 기반으로 AI 분석을 진행합니다.")
    elif analysis_mode == "selected_text":
        st.success("🎯 **선택 텍스트 분석 모드**") 
        st.caption("선택된 텍스트 부분만을 대상으로 AI 분석을 진행합니다.")
    else:
        st.info("⚙️ **수동 분석 모드**")
        st.caption("사용자가 직접 분석 옵션을 설정할 수 있습니다.")
    
    # 자동 분석 시작 (버튼 클릭으로 진입한 경우)
    if st.session_state.get('auto_start_analysis', False) and st.session_state.get('analysis_text'):
        st.session_state.auto_start_analysis = False  # 중복 실행 방지
        analysis_text = st.session_state.analysis_text
        
        st.info(f"🚀 분석을 자동 시작합니다... (길이: {len(analysis_text)}자)")
        _start_enhanced_analysis(analysis_text)
    
    # 수동 분석 설정 (manual 모드이거나 자동 분석이 없는 경우)
    if analysis_mode == 'manual' or not st.session_state.get('analysis_text'):
        _render_manual_analysis_settings()
    
    # 현재 분석 대상 정보 표시
    _render_current_analysis_info()
    
    # 분석 결과 표시
    _render_enhanced_analysis_results()
    
    # 팝업 결과 렌더링
    render_analysis_popup()
    
    # 패널 제어 버튼
    _render_panel_controls()

def _render_manual_analysis_settings():
    """수동 분석 설정 렌더링"""
    st.markdown("---")
    st.markdown("### 🔧 분석 설정")
    
    # 분석 대상 선택
    manual_mode = st.radio(
        "분석 대상 선택:",
        ["직접 입력", "전체 문서", "선택된 텍스트"],
        key="manual_analysis_mode"
    )
    
    analysis_input = ""
    
    if manual_mode == "직접 입력":
        analysis_input = st.text_area(
            "분석할 내용을 입력하세요:",
            placeholder="분석하고 싶은 내용을 직접 입력하세요...",
            height=150,
            key="manual_analysis_input"
        )
    
    elif manual_mode == "전체 문서":
        analysis_input = st.session_state.get('document_content', '')
        if analysis_input:
            st.success(f"📄 전체 문서 준비됨 ({len(analysis_input.split())} 단어, {len(analysis_input)} 글자)")
            # 미리보기
            preview = analysis_input[:200] + ("..." if len(analysis_input) > 200 else "")
            st.text_area("문서 미리보기:", value=preview, height=100, disabled=True)
        else:
            st.warning("📭 문서 내용이 없습니다. 왼쪽에서 문서를 작성해주세요.")
    
    else:  # 선택된 텍스트
        analysis_input = st.session_state.get('selected_text', '')
        if analysis_input:
            st.success(f"🎯 선택된 텍스트 준비됨 ({len(analysis_input.split())} 단어, {len(analysis_input)} 글자)")
            st.text_area("선택된 텍스트:", value=analysis_input, height=100, disabled=True)
        else:
            st.warning("📭 선택된 텍스트가 없습니다. 왼쪽에서 텍스트를 선택해주세요.")
    
    # 분석 시작 버튼
    if st.button("🚀 수동 분석 시작", type="primary", use_container_width=True):
        if analysis_input and analysis_input.strip():
            _start_enhanced_analysis(analysis_input.strip())
        else:
            st.error("❌ 분석할 내용을 입력하거나 선택해주세요.")

def _render_current_analysis_info():
    """현재 분석 대상 정보 표시"""
    analysis_text = st.session_state.get('analysis_text', '')
    
    if analysis_text:
        st.markdown("---")
        st.markdown("### 📊 현재 분석 대상")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("단어 수", f"{len(analysis_text.split()):,}")
        with col2:
            st.metric("글자 수", f"{len(analysis_text):,}")
        
        # 텍스트 미리보기
        preview = analysis_text[:150] + ("..." if len(analysis_text) > 150 else "")
        st.text_area("분석 대상 미리보기:", value=preview, height=80, disabled=True)
        
        # 다른 텍스트로 분석하기 버튼
        if st.button("🔄 다른 내용 분석", key="change_analysis_target"):
            st.session_state.analysis_text = ""
            st.session_state.analysis_mode = "manual"
            st.rerun()

def _start_enhanced_analysis(analysis_text: str):
    """향상된 AI 분석 시작"""
    st.markdown("---")
    st.markdown("## 🔄 AI 분석 진행")
    
    # 분석 시작 정보
    st.info(f"🎯 분석 시작: {len(analysis_text)} 글자, {len(analysis_text.split())} 단어")
    
    # 분석 서비스 초기화 및 실행
    try:
        analysis_service = EnhancedAIAnalysisService()
        
        # 4단계 순차 분석 실행
        with st.container():
            results = analysis_service.run_step_by_step_analysis(analysis_text)
            
            # 분석 완료 상태 업데이트
            if results['completed_steps'] == 4:
                st.session_state.analysis_in_progress = False
                st.success("🎉 모든 분석 단계가 성공적으로 완료되었습니다!")
                st.balloons()
            else:
                st.warning(f"⚠️ 분석이 {results['completed_steps']}/4 단계까지만 완료되었습니다.")
                if results.get('error'):
                    st.error(f"오류: {results['error']}")
    
    except Exception as e:
        st.session_state.analysis_in_progress = False
        st.error(f"❌ 분석 중 오류 발생: {str(e)}")
        
        # 오류 상세 정보
        with st.expander("🔍 오류 상세 정보"):
            st.code(f"""
오류 메시지: {str(e)}
오류 타입: {type(e).__name__}
분석 텍스트 길이: {len(analysis_text)}
분석 모드: {st.session_state.get('analysis_mode', 'Unknown')}
            """)

def _render_enhanced_analysis_results():
    """향상된 분석 결과 렌더링"""
    if not st.session_state.get('analysis_completed', False):
        return
    
    st.markdown("---")
    st.markdown("## 📊 분석 결과")
    
    results = st.session_state.get('enhanced_analysis_results', {})
    
    if not results:
        st.info("분석 결과가 없습니다.")
        return
    
    # 분석 완료 상태 표시
    completed_steps = results.get('completed_steps', 0)
    st.progress(completed_steps / 4)
    st.caption(f"분석 진행도: {completed_steps}/4 단계 완료")
    
    # 탭으로 결과 구성
    tabs = st.tabs(["🎯 최종 분석", "📋 단계별 결과", "📚 참고 자료", "💡 추천 액션"])
    
    with tabs[0]:
        _render_final_analysis_tab(results)
    
    with tabs[1]:
        _render_step_by_step_tab(results)
    
    with tabs[2]:
        _render_references_tab(results)
    
    with tabs[3]:
        _render_action_recommendations_tab(results)

def _render_final_analysis_tab(results: dict):
    """최종 분석 탭 렌더링"""
    final_analysis = results.get('step4_final_analysis')
    
    if final_analysis:
        # 최종 분석 결과 표시 (150자 제한)
        preview = final_analysis[:150] + ("..." if len(final_analysis) > 150 else "")
        st.markdown("#### 📋 분석 결과 요약")
        st.markdown(preview)
        
        # 전체 결과 보기 버튼
        if len(final_analysis) > 150:
            if st.button("📖 전체 분석 결과 보기", key="view_full_analysis"):
                st.session_state[f'popup_content_final_analysis'] = {
                    'title': "최종 AI 분석 결과",
                    'content': final_analysis,
                    'type': "분석 결과",
                    'show': True
                }
                st.rerun()
        
        # 문서 삽입 옵션
        st.markdown("#### 🔧 문서 삽입 옵션")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📝 요약만 삽입", key="insert_summary_only"):
                # 첫 번째 섹션만 추출 (## 이전까지)
                summary = final_analysis.split('\n\n')[0]
                _insert_to_document(summary, "AI 분석 요약")
        
        with col2:
            if st.button("� 전체 결과 삽입", key="insert_full_result"):
                _insert_to_document(final_analysis, "AI 분석 전체")
    else:
        st.info("최종 분석 결과가 아직 생성되지 않았습니다.")

def _render_step_by_step_tab(results: dict):
    """단계별 결과 탭 렌더링"""
    st.markdown("#### 🔄 4단계 분석 과정")
    
    steps = [
        ("1단계", "step1_enhanced_prompt", "프롬프트 고도화"),
        ("2단계", "step2_search_queries", "검색 쿼리 생성"),
        ("3단계", "step3_internal_references", "사내 문서 검색"),
        ("3단계", "step3_external_references", "외부 레퍼런스 검색"),
        ("4단계", "step4_final_analysis", "최종 분석 생성")
    ]
    
    for step_name, step_key, step_desc in steps:
        step_data = results.get(step_key)
        
        if step_data:
            with st.expander(f"✅ {step_name}: {step_desc}"):
                if isinstance(step_data, (list, dict)):
                    if isinstance(step_data, list) and len(step_data) > 0:
                        st.write(f"결과 수: {len(step_data)}개")
                        for i, item in enumerate(step_data[:3], 1):  # 처음 3개만 표시
                            if isinstance(item, dict):
                                title = item.get('title', f'항목 {i}')
                                st.write(f"{i}. {title}")
                    elif isinstance(step_data, dict):
                        for key, value in step_data.items():
                            if isinstance(value, list):
                                st.write(f"**{key}**: {', '.join(value[:3])}")
                            else:
                                preview = str(value)[:100] + ("..." if len(str(value)) > 100 else "")
                                st.write(f"**{key}**: {preview}")
                else:
                    preview = str(step_data)[:200] + ("..." if len(str(step_data)) > 200 else "")
                    st.write(preview)
        else:
            with st.expander(f"⏳ {step_name}: {step_desc}"):
                st.write("아직 완료되지 않음")

def _render_references_tab(results: dict):
    """참고 자료 탭 렌더링 - 세로 배치로 변경"""
    internal_refs = results.get('step3_internal_references', [])
    external_refs = results.get('step3_external_references', [])
    
    # 사내 문서 (위쪽에 배치)
    st.markdown("#### 📁 사내 문서")
    if internal_refs:
        for i, ref in enumerate(internal_refs[:5], 1):
            title = ref.get('title', f'문서 {i}')
            summary = ref.get('summary', ref.get('content', ''))[:100]
            
            with st.expander(f"{i}. {title}"):
                st.write(f"**요약:** {summary}...")
                
                # 삽입 버튼들
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button(f"📝 요약 삽입", key=f"insert_internal_sum_{i}"):
                        _insert_to_document(ref.get('summary', ''), f"사내문서 {i} 요약")
                with col_b:
                    if st.button(f"📄 전체 삽입", key=f"insert_internal_full_{i}"):
                        _insert_to_document(ref.get('content', ''), f"사내문서 {i}")
    else:
        st.info("관련 사내 문서가 없습니다.")
    
    st.markdown("---")  # 구분선 추가
    
    # 외부 자료 (아래쪽에 배치)
    st.markdown("#### 🌐 외부 자료")
    if external_refs:
        for i, ref in enumerate(external_refs[:5], 1):
            title = ref.get('title', f'자료 {i}')
            summary = ref.get('summary', ref.get('content', ''))[:100]
            
            with st.expander(f"{i}. {title}"):
                st.write(f"**요약:** {summary}...")
                
                if ref.get('url'):
                    st.markdown(f"🔗 [원문 링크]({ref['url']})")
                
                # 삽입 버튼들
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button(f"📝 요약 삽입", key=f"insert_external_sum_{i}"):
                        _insert_to_document(ref.get('summary', ''), f"외부자료 {i} 요약")
                with col_b:
                    if st.button(f"📄 전체 삽입", key=f"insert_external_full_{i}"):
                        _insert_to_document(ref.get('content', ''), f"외부자료 {i}")
    else:
        st.info("관련 외부 자료가 없습니다.")

def _render_action_recommendations_tab(results: dict):
    """추천 액션 탭 렌더링"""
    st.markdown("#### 💡 추천 액션")
    
    final_analysis = results.get('step4_final_analysis', '')
    
    if final_analysis:
        # 실행 가능한 제안사항 추출 (간단한 파싱)
        if "실행 가능한 제안사항" in final_analysis:
            suggestions_section = final_analysis.split("실행 가능한 제안사항")[1].split("##")[0]
            st.markdown("**🎯 AI 추천 액션:**")
            st.markdown(suggestions_section[:300] + ("..." if len(suggestions_section) > 300 else ""))
    
    # 빠른 액션 버튼들
    st.markdown("#### ⚡ 빠른 액션")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📋 체크리스트 생성", key="create_checklist"):
            checklist_prompt = f"다음 분석을 바탕으로 실행 체크리스트를 만들어주세요:\n\n{final_analysis[:500]}"
            _request_additional_analysis(checklist_prompt, "체크리스트")
        
        if st.button("📊 요약 테이블 생성", key="create_summary_table"):
            table_prompt = f"다음 분석을 표 형태로 요약해주세요:\n\n{final_analysis[:500]}"
            _request_additional_analysis(table_prompt, "요약 테이블")
    
    with col2:
        if st.button("🔍 추가 질문 생성", key="generate_questions"):
            questions_prompt = f"다음 분석을 보고 추가로 고려할 질문들을 만들어주세요:\n\n{final_analysis[:500]}"
            _request_additional_analysis(questions_prompt, "추가 질문")
        
        if st.button("📈 개선 방안 생성", key="generate_improvements"):
            improve_prompt = f"다음 분석을 바탕으로 구체적인 개선 방안을 제시해주세요:\n\n{final_analysis[:500]}"
            _request_additional_analysis(improve_prompt, "개선 방안")

def _render_panel_controls():
    """패널 제어 버튼들"""
    st.markdown("---")
    st.markdown("### 🎛️ 패널 제어")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 새 분석", key="new_analysis", use_container_width=True):
            # 분석 상태 초기화
            st.session_state.analysis_text = ""
            st.session_state.analysis_mode = "manual"
            st.session_state.analysis_completed = False
            st.session_state.enhanced_analysis_results = {}
            st.rerun()
    
    with col2:
        if st.button("❌ 패널 닫기", key="close_ai_panel", use_container_width=True):
            _close_ai_panel()

def _insert_to_document(content: str, content_type: str):
    """분석 결과를 문서에 삽입 - 개선된 버전"""
    if not content or not content.strip():
        st.warning("⚠️ 삽입할 내용이 없습니다.")
        return
    
    try:
        # 현재 문서 내용 가져오기
        current_content = st.session_state.get('document_content', '')
        
        # 구분선과 헤더 추가
        separator = "\n\n---\n\n" if current_content.strip() else ""
        timestamp = __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M")
        header = f"[{content_type} 삽입 | {timestamp}]"
        
        # 내용 정리 (너무 긴 경우 요약)
        clean_content = content.strip()
        if len(clean_content) > 2000:
            clean_content = clean_content[:2000] + f"\n\n[원본 길이: {len(content)}자, 표시: 2000자로 제한됨]"
        
        # 새로운 내용 생성
        new_content = current_content + separator + header + "\n\n" + clean_content
        
        # 세션 상태 업데이트 (여러 방법으로 시도)
        st.session_state.document_content = new_content
        st.session_state['document_content'] = new_content  # 추가 보장
        
        # 메인 편집기에도 직접 반영 (가능한 경우)
        if 'main_document_editor' in st.session_state:
            st.session_state['main_document_editor'] = new_content
        
        # 성공 메시지
        st.success(f"✅ {content_type}가 문서에 삽입되었습니다!")
        st.info(f"📝 삽입된 내용 길이: {len(clean_content):,}자")
        
        # 삽입 완료 메시지를 세션에 저장 (다음 렌더링에서 표시)
        st.session_state.insert_success_message = f"✅ {content_type} 삽입 완료"
        
        # 강제로 페이지 새로고침하여 변경사항 반영
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ 문서 삽입 중 오류 발생: {str(e)}")
        st.error(f"오류 상세: {type(e).__name__}")
        
        # 오류 상황에서도 기본적인 삽입 시도
        try:
            st.session_state.document_content = (st.session_state.get('document_content', '') + 
                                               f"\n\n[오류로 인한 단순 삽입]\n{content[:500]}...")
            st.warning("⚠️ 일부 내용만 삽입되었습니다.")
        except Exception as e2:
            st.error(f"❌ 복구 삽입도 실패: {str(e2)}")

def _request_additional_analysis(prompt: str, analysis_type: str):
    """추가 분석 요청"""
    st.info(f"🔄 {analysis_type} 생성 중...")
    
    try:
        from utils.ai_service import AIService
        ai_service = AIService()
        
        result = ai_service.get_ai_response(prompt)
        
        # 결과를 팝업으로 표시
        st.session_state[f'popup_content_{analysis_type}'] = {
            'title': f'{analysis_type} 생성 결과',
            'content': result,
            'type': analysis_type,
            'show': True
        }
        
        st.success(f"✅ {analysis_type}가 생성되었습니다!")
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ {analysis_type} 생성 실패: {str(e)}")

def _close_ai_panel():
    """AI 패널 닫기"""
    st.session_state.ai_panel_open = False
    st.session_state.analysis_mode = None
    st.session_state.analysis_text = ""
    st.session_state.analysis_in_progress = False
    st.session_state.auto_start_analysis = False
    st.rerun()

def _handle_ai_analysis_start(search_mode):
    """AI 분석 시작 처리"""
    st.info(f"🔍 AI 분석 시작 - 모드: {search_mode}")
    
    # 분석 상태 초기화 및 기존 결과 클리어
    st.session_state.analysis_state = 'analyzing'
    st.session_state.enhanced_prompt = None
    st.session_state.internal_search_results = []
    st.session_state.external_search_results = []
    st.session_state.analysis_result = None
    
    # 분석 쿼리 결정
    search_query = None
    query_source = "알 수 없음"
    
    if search_mode == "직접 입력":
        search_query = st.session_state.get('direct_search_query', '').strip()
        query_source = "직접 입력"
    elif search_mode == "선택된 텍스트 기반":
        search_query = st.session_state.get('selected_text', '').strip()
        query_source = "선택된 텍스트"
    elif search_mode == "전체 문서 기반":
        # 여러 소스에서 문서 내용 시도
        search_query = st.session_state.get('document_content', '').strip()
        if not search_query:
            search_query = st.session_state.get('main_document_editor', '').strip()
        query_source = "문서 전체"
    
    # 쿼리 길이 체크 및 요약 (너무 긴 경우)
    if search_query and len(search_query) > 2000:
        st.warning(f"⚠️ 문서가 너무 깁니다 ({len(search_query)}자). 처음 2000자로 제한합니다.")
        search_query = search_query[:2000] + "..."
    
    # 디버깅 정보 표시
    _show_debug_info(search_mode, search_query)
    
    st.info(f"📊 쿼리 소스: {query_source}, 길이: {len(search_query) if search_query else 0}자")
    
    if search_query and len(search_query.strip()) > 0:
        st.success(f"✅ 분석 시작! (쿼리: '{search_query[:50]}...')")
        
        # 실시간 진행 표시 - 새 분석 시스템 사용
        with st.status("🚀 AI 분석 진행 중...", expanded=True) as status:
            try:
                # 새로운 향상된 분석 서비스 사용
                _start_enhanced_analysis(search_query.strip())
                
                status.update(label="✅ 분석 완료!", state="complete")
                st.session_state.analysis_state = 'completed'
                st.balloons()
                
            except Exception as e:
                status.update(label="❌ 분석 실패", state="error")
                st.error(f"❌ 분석 중 오류: {str(e)}")
                st.error(f"오류 타입: {type(e).__name__}")
                
                # 상세 오류 정보
                with st.expander("🔍 상세 오류 정보"):
                    st.code(f"""
오류 메시지: {str(e)}
오류 타입: {type(e).__name__}
검색 모드: {search_mode}
쿼리 길이: {len(search_query) if search_query else 0}
                    """)
                
                st.session_state.analysis_state = 'error'
                _render_test_analysis_button()
    else:
        # 구체적인 오류 안내
        st.error(f"❌ 분석할 내용이 없습니다")
        
        if search_mode == "직접 입력":
            st.warning("💡 위의 텍스트 영역에 분석하고 싶은 내용을 입력해주세요.")
        elif search_mode == "선택된 텍스트 기반":
            st.warning("💡 먼저 텍스트를 선택하거나 아래 탭에서 텍스트를 입력해주세요.")
        elif search_mode == "전체 문서 기반":
            st.warning("💡 문서 편집 영역에 내용을 먼저 작성해주세요.")
            
            # 문서 편집 안내
            st.info("""
            📝 **문서 작성 방법:**
            1. 왼쪽 문서 편집 영역에 내용을 입력하세요
            2. 내용이 입력되면 자동으로 분석 가능해집니다
            3. 또는 '직접 입력' 모드를 사용해보세요
            """)
        
        st.session_state.analysis_state = 'idle'
        _render_test_analysis_button()

def _show_debug_info(search_mode, search_query):
    """디버깅 정보 표시"""
    with st.expander("🔍 디버그 정보"):
        st.write(f"- 검색 모드: {search_mode}")
        st.write(f"- 직접 입력: '{st.session_state.get('direct_search_query', 'None')}'")
        st.write(f"- 선택된 텍스트: '{str(st.session_state.get('selected_text', 'None'))[:50]}...'")
        st.write(f"- 문서 내용 길이: {len(str(st.session_state.get('document_content', '')))}")
        st.write(f"- 최종 쿼리: '{str(search_query)[:100] if search_query else 'None'}...'")
        st.write(f"- 최종 쿼리 길이: {len(str(search_query)) if search_query else 0}")
        
        # 세션 상태 전체 확인 (AI 관련만)
        ai_keys = [k for k in st.session_state.keys() if any(x in k.lower() for x in ['ai', 'search', 'analysis', 'query', 'text'])]
        if ai_keys:
            st.write("- AI 관련 세션 키들:")
            for key in ai_keys[:10]:  # 처음 10개만 표시
                value = str(st.session_state.get(key, ''))[:30]
                st.write(f"  • {key}: '{value}...'")

def _render_test_analysis_button():
    """테스트 분석 버튼 렌더링"""
    st.markdown("### 🧪 테스트 옵션")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📝 샘플 분석", key="test_sample"):
            test_query = "AI와 머신러닝을 활용한 비즈니스 프로세스 개선 방안"
            st.info(f"테스트 쿼리: {test_query}")
            _start_enhanced_analysis(test_query)
    
    with col2:
        if st.button("🏠 재개발 분석", key="test_redevelopment"):
            test_query = "재개발"
            st.info(f"테스트 쿼리: {test_query}")
            _start_enhanced_analysis(test_query)
    
    # 현재 선택된 텍스트로 분석 (있는 경우)
    if st.session_state.get('selected_text'):
        st.markdown("---")
        current_text = st.session_state.selected_text.strip()
        st.markdown(f"**현재 선택된 텍스트로 분석하기:**")
        st.code(current_text[:100] + ("..." if len(current_text) > 100 else ""))
        
        if st.button("🎯 선택된 텍스트로 분석 실행", key="test_selected"):
            st.info(f"선택된 텍스트로 분석: '{current_text}'")
            _start_enhanced_analysis(current_text)
    
    # 현재 문서 내용으로 분석 (있는 경우)
    document_content = st.session_state.get('document_content', '').strip()
    if not document_content:
        document_content = st.session_state.get('main_document_editor', '').strip()
    
    if document_content:
        st.markdown("---")
        st.markdown(f"**현재 문서 내용으로 분석하기:**")
        preview_text = document_content[:200] + ("..." if len(document_content) > 200 else "")
        st.code(preview_text)
        st.caption(f"문서 길이: {len(document_content):,}자")
        
        if st.button("📄 문서 전체로 분석 실행", key="test_document"):
            st.info(f"문서 전체로 분석 시작 (길이: {len(document_content)}자)")
            
            # 긴 문서는 요약해서 분석
            if len(document_content) > 2000:
                analysis_text = document_content[:2000] + f"\n\n[원문 길이: {len(document_content)}자 - 처음 2000자만 분석]"
                st.warning("⚠️ 문서가 길어서 처음 2000자만 분석합니다.")
            else:
                analysis_text = document_content
            
            _start_enhanced_analysis(analysis_text)
    
    # 빠른 테스트용 버튼들
    st.markdown("---")
    st.markdown("**⚡ 빠른 테스트:**")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🏠 재개발 키워드 분석", key="quick_redevelopment"):
            quick_query = "재개발 프로젝트 관련 정보와 투자 가이드"
            st.info(f"빠른 분석: {quick_query}")
            _start_enhanced_analysis(quick_query)
    
    with col2:
        if st.button("📋 일반 문서 작성 분석", key="quick_general"):
            quick_query = "문서 작성 및 비즈니스 분석 방법"
            st.info(f"빠른 분석: {quick_query}")
            _start_enhanced_analysis(quick_query)

def _render_analysis_results():
    """분석 결과 렌더링"""
    # 강화된 분석 결과 요약 표시
    if hasattr(st.session_state, 'analysis_result') and st.session_state.analysis_result:
        _show_enhanced_analysis_summary()
    
    # 탭 방식 결과 표시
    tabs = st.tabs(["🎯 분석 결과", "📚 문서 추천", "✨ 문장 다듬기", "🏗️ 구조화"])
    
    with tabs[0]:
        _render_main_analysis_tab()
    
    with tabs[1]:
        _render_recommendations_tab()
    
    with tabs[2]:
        _render_text_refinement_tab()
    
    with tabs[3]:
        _render_structuring_tab()

def _show_enhanced_analysis_summary():
    """강화된 분석 결과 요약 표시"""
    st.markdown("### 🎯 분석 결과 요약")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        internal_count = len(st.session_state.get('internal_search_results', []))
        st.metric("📁 사내 문서", f"{internal_count}개")
        if internal_count > 0:
            st.caption("Azure AI Search로 검색됨")
    
    with col2:
        external_count = len(st.session_state.get('external_search_results', []))
        st.metric("🌐 외부 레퍼런스", f"{external_count}개")
        if external_count > 0:
            st.caption("Tavily 검색으로 발견됨")
    
    with col3:
        st.metric("📋 분석 완료", "✅")
        st.caption("AI 종합 분석 완료")

def _render_main_analysis_tab():
    """메인 분석 탭 렌더링"""
    if hasattr(st.session_state, 'analysis_result') and st.session_state.analysis_result:
        result = st.session_state.analysis_result
        st.markdown("#### 🎯 AI 분석 결과")
        st.markdown(result.get('content', '분석 결과가 없습니다.'))
        
        # 결과 삽입 버튼
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📝 요약 삽입", key="insert_main_summary"):
                content_to_insert = result.get('content', '')
                if content_to_insert:
                    _insert_content_to_document(content_to_insert, "AI분석 요약", 600)
                else:
                    st.warning("⚠️ 삽입할 분석 결과가 없습니다.")
        with col2:
            if st.button("📋 전체 삽입", key="insert_main_full"):
                content_to_insert = result.get('content', '')
                if content_to_insert:
                    _insert_content_to_document(content_to_insert, "AI분석 전체", 1500)
                else:
                    st.warning("⚠️ 삽입할 분석 결과가 없습니다.")
    else:
        st.info("분석 결과가 없습니다. AI 분석을 실행해주세요.")

def _render_recommendations_tab():
    """문서 추천 탭 렌더링"""
    st.markdown("### 📚 추천 문서")
    
    # 사내 문서 결과 표시
    internal_docs = st.session_state.get('internal_search_results', [])
    if internal_docs:
        st.markdown("#### 📁 사내 문서")
        for i, doc in enumerate(internal_docs[:3]):
            with st.expander(f"📄 {doc.get('title', '제목 없음')} (관련도: {doc.get('relevance_score', 0):.1f}/1.0)"):
                st.markdown(f"**📋 요약:** {doc.get('summary', 'N/A')}")
                
                # 출처 정보 토글
                if st.toggle(f"🔍 출처 상세보기", key=f"toggle_internal_{i}"):
                    st.markdown("**📍 출처 정보:**")
                    st.markdown(f"- **검색 유형:** {doc.get('search_type', 'N/A')}")
                    st.markdown(f"- **출처:** {doc.get('source_detail', 'N/A')}")
                    st.markdown(f"- **문서 ID:** {doc.get('id', 'N/A')}")
                    if doc.get('url'):
                        st.markdown(f"- **URL:** [{doc.get('url')}]({doc.get('url')})")
                
                # 내용 미리보기 토글
                if st.toggle(f"📖 내용 미리보기", key=f"preview_internal_{i}"):
                    content_preview = doc.get('content', '')[:500] + ('...' if len(doc.get('content', '')) > 500 else '')
                    st.markdown(f"```\n{content_preview}\n```")
                
                # 삽입 버튼
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button(f"📝 요약 삽입", key=f"insert_internal_summary_{i}"):
                        _insert_content_to_document(doc.get('summary', ''), "사내문서 요약", 500)
                with col2:
                    if st.button(f"� 일부 삽입", key=f"insert_internal_partial_{i}"):
                        _insert_content_to_document(doc.get('content', ''), "사내문서 발췌", 800)
                with col3:
                    if st.button(f"📋 전체 삽입", key=f"insert_internal_full_{i}"):
                        _insert_content_to_document(doc.get('content', ''), "사내문서 전체", 2000)
    else:
        st.info("📭 사내 문서 검색 결과가 없습니다.")
    
    # 외부 문서 결과 표시
    external_docs = st.session_state.get('external_search_results', [])
    if external_docs:
        st.markdown("#### 🌐 외부 레퍼런스")
        for i, doc in enumerate(external_docs[:3]):
            with st.expander(f"📄 {doc.get('title', '제목 없음')} (관련도: {doc.get('relevance_score', 0):.1f}/1.0)"):
                st.markdown(f"**📋 요약:** {doc.get('summary', 'N/A')}")
                
                # 출처 정보 토글
                if st.toggle(f"🔍 출처 상세보기", key=f"toggle_external_{i}"):
                    st.markdown("**📍 출처 정보:**")
                    st.markdown(f"- **검색 유형:** {doc.get('search_type', 'N/A')}")
                    st.markdown(f"- **출처 상세:** {doc.get('source_detail', 'N/A')}")
                    if doc.get('url'):
                        st.markdown(f"- **원문 링크:** [{doc.get('url')}]({doc.get('url')})")
                
                # 내용 미리보기 토글
                if st.toggle(f"📖 내용 미리보기", key=f"preview_external_{i}"):
                    content_preview = doc.get('content', '')[:500] + ('...' if len(doc.get('content', '')) > 500 else '')
                    st.markdown(f"```\n{content_preview}\n```")
                
                # 삽입 버튼
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button(f"📝 요약 삽입", key=f"insert_external_summary_{i}"):
                        _insert_content_to_document(doc.get('summary', ''), "외부자료 요약", 500)
                with col2:
                    if st.button(f"� 일부 삽입", key=f"insert_external_partial_{i}"):
                        _insert_content_to_document(doc.get('content', ''), "외부자료 발췌", 800)
                with col3:
                    if st.button(f"📋 전체 삽입", key=f"insert_external_full_{i}"):
                        _insert_content_to_document(doc.get('content', ''), "외부자료 전체", 2000)
    else:
        st.info("📭 외부 레퍼런스 검색 결과가 없습니다.")

def _render_text_refinement_tab():
    """문장 다듬기 탭 렌더링"""
    if st.session_state.selected_text:
        st.markdown("### ✨ 문장 다듬기")
        st.markdown(f"**선택된 텍스트:** {st.session_state.selected_text[:100]}...")
        
        # 다듬기 스타일 선택
        style_options = {
            "clear": "명확성 개선",
            "professional": "전문성 강화", 
            "concise": "간결성 개선"
        }
        
        for style_key, style_name in style_options.items():
            if st.button(f"✏️ {style_name}", key=f"refine_{style_key}"):
                from utils.ai_service import AIService
                ai_service = AIService()
                refined_text = ai_service.refine_text(st.session_state.selected_text, style_key)
                
                st.markdown(f"**{style_name} 결과:**")
                st.markdown(f"```\n{refined_text}\n```")
                
                if st.button(f"적용", key=f"apply_{style_key}"):
                    if refined_text:
                        _insert_content_to_document(refined_text, f"문장다듬기({style_name})", 800)
    else:
        st.info("텍스트를 선택하면 문장 다듬기 기능을 사용할 수 있습니다.")

def _render_structuring_tab():
    """구조화 탭 렌더링"""
    if st.session_state.selected_text:
        st.markdown("### 🏗️ 내용 구조화")
        st.markdown(f"**선택된 텍스트:** {st.session_state.selected_text[:100]}...")
        
        # 구조화 타입 선택
        structure_options = {
            "outline": "목차 형식",
            "steps": "단계별 가이드",
            "qa": "Q&A 형식"
        }
        
        for struct_key, struct_name in structure_options.items():
            if st.button(f"📋 {struct_name}", key=f"struct_{struct_key}"):
                from utils.ai_service import AIService
                ai_service = AIService()
                structured_content = ai_service.structure_content(st.session_state.selected_text, struct_key)
                
                st.markdown(f"**{struct_name} 결과:**")
                st.markdown(structured_content)
                
                if st.button(f"구조 적용", key=f"apply_struct_{struct_key}"):
                    if structured_content:
                        _insert_content_to_document(structured_content, f"구조화({struct_name})", 1000)
    else:
        st.info("텍스트를 선택하면 구조화 기능을 사용할 수 있습니다.")

def _insert_content_to_document(content, content_type="일반", max_length=1000):
    """문서에 내용 삽입 (길이 제한 포함)"""
    if not content or not content.strip():
        st.warning("⚠️ 삽입할 내용이 없습니다.")
        return
    
    # 내용 길이 확인 및 제한
    content = content.strip()
    original_length = len(content)
    
    if len(content) > max_length:
        content = content[:max_length] + f"\n\n[원본 길이: {original_length:,}자 / 표시: {max_length:,}자로 제한됨]"
        truncated = True
    else:
        truncated = False
    
    # 현재 문서 내용 가져오기
    current_content = st.session_state.get('document_content', '')
    
    # 구분선과 메타데이터 추가
    separator = "\n\n---\n\n" if current_content.strip() else ""
    timestamp = __import__('datetime').datetime.now().strftime("%H:%M")
    header = f"[{content_type} | {timestamp}]"
    
    new_content = current_content + separator + header + "\n\n" + content
    
    # 세션 상태 업데이트
    st.session_state.document_content = new_content
    
    # 성공 메시지를 즉시 표시 (잘린 경우 알림 포함)
    if truncated:
        st.success(f"✅ {content_type}이 삽입되었습니다! (길이 제한: {max_length:,}자)")
    else:
        st.success(f"✅ {content_type}이 문서에 삽입되었습니다!")
    
    # 세션 상태에도 저장해서 다음 렌더링에서도 보이도록
    st.session_state.insert_success_message = f"✅ {content_type} 삽입 완료"