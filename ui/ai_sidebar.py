"""
Enhanced AI Sidebar UI Component
"""
import streamlit as st
from state.session_state import session_state
from services.enhanced_ai_analysis_service import EnhancedAIAnalysisService, render_analysis_popup

def render_ai_sidebar():
    """Enhanced AI sidebar panel rendering"""
    if not st.session_state.get('ai_panel_open', False):
        return
    
    st.markdown("## 🤖 AI 문서 분석")
    
    # Display current analysis mode
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
    
    # Auto start analysis (when entered via button click)
    if st.session_state.get('auto_start_analysis', False) and st.session_state.get('analysis_text'):
        st.session_state.auto_start_analysis = False  # Prevent duplicate execution
        analysis_text = st.session_state.analysis_text
        
        st.info(f"🚀 분석을 자동 시작합니다... (길이: {len(analysis_text)}자)")
        _start_enhanced_analysis(analysis_text)
    
    # Manual analysis settings (manual mode or no auto analysis)
    if analysis_mode == 'manual' or not st.session_state.get('analysis_text'):
        _render_manual_analysis_settings()
    
    # Display current analysis target info
    _render_current_analysis_info()
    
    # Display analysis results
    _render_enhanced_analysis_results()
    
    # Render popup results
    render_analysis_popup()
    
    # Panel control buttons
    _render_panel_controls()

def _render_manual_analysis_settings():
    """Manual analysis settings rendering"""
    st.markdown("---")
    st.markdown("### 🔧 분석 설정")
    
    # Analysis target selection
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
            preview = analysis_input[:200] + ("..." if len(analysis_input) > 200 else "")
            st.text_area("문서 미리보기:", value=preview, height=100, disabled=True)
        else:
            st.warning("📭 문서 내용이 없습니다. 왼쪽에서 문서를 작성해주세요.")
    
    else:  # Selected text
        analysis_input = st.session_state.get('selected_text', '')
        if analysis_input:
            st.success(f"🎯 선택된 텍스트 준비됨 ({len(analysis_input.split())} 단어, {len(analysis_input)} 글자)")
            st.text_area("선택된 텍스트:", value=analysis_input, height=100, disabled=True)
        else:
            st.warning("📭 선택된 텍스트가 없습니다. 왼쪽에서 텍스트를 선택해주세요.")
    
    # Start analysis button
    if st.button("🚀 수동 분석 시작", type="primary", use_container_width=True):
        if analysis_input and analysis_input.strip():
            _start_enhanced_analysis(analysis_input.strip())
        else:
            st.error("❌ 분석할 내용을 입력하거나 선택해주세요.")

def _render_current_analysis_info():
    """Display current analysis target info"""
    analysis_text = st.session_state.get('analysis_text', '')
    
    if analysis_text:
        st.markdown("---")
        st.markdown("### 📊 현재 분석 대상")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("단어 수", f"{len(analysis_text.split()):,}")
        with col2:
            st.metric("글자 수", f"{len(analysis_text):,}")
        
        preview = analysis_text[:150] + ("..." if len(analysis_text) > 150 else "")
        st.text_area("분석 대상 미리보기:", value=preview, height=80, disabled=True)
        
        if st.button("�� 다른 내용 분석", key="change_analysis_target"):
            st.session_state.analysis_text = ""
            st.session_state.analysis_mode = "manual"
            st.rerun()

def _start_enhanced_analysis(analysis_text):
    """Start enhanced AI analysis"""
    st.markdown("---")
    st.markdown("## 🔄 AI 분석 진행")
    
    st.info(f"🎯 분석 시작: {len(analysis_text)} 글자, {len(analysis_text.split())} 단어")
    
    try:
        analysis_service = EnhancedAIAnalysisService()
        
        with st.container():
            results = analysis_service.run_step_by_step_analysis(analysis_text)
            
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
        
        with st.expander("🔍 오류 상세 정보"):
            st.code(f"""
오류 메시지: {str(e)}
오류 타입: {type(e).__name__}
분석 텍스트 길이: {len(analysis_text)}
분석 모드: {st.session_state.get('analysis_mode', 'Unknown')}
            """)

def _render_enhanced_analysis_results():
    """Enhanced analysis results rendering"""
    if not st.session_state.get('analysis_completed', False):
        return
    
    st.markdown("---")
    st.markdown("## 📊 분석 결과")
    
    results = st.session_state.get('enhanced_analysis_results', {})
    
    if not results:
        st.info("분석 결과가 없습니다.")
        return
    
    completed_steps = results.get('completed_steps', 0)
    st.progress(completed_steps / 4)
    st.caption(f"분석 진행도: {completed_steps}/4 단계 완료")
    
    tabs = st.tabs(["🎯 최종 분석", "📋 단계별 결과", "📚 참고 자료", "💡 추천 액션"])
    
    with tabs[0]:
        _render_final_analysis_tab(results)
    
    with tabs[1]:
        _render_step_by_step_tab(results)
    
    with tabs[2]:
        _render_references_tab(results)
    
    with tabs[3]:
        _render_action_recommendations_tab(results)

def _render_final_analysis_tab(results):
    """Final analysis tab rendering"""
    final_analysis = results.get('step4_final_analysis')
    
    if final_analysis:
        preview = final_analysis[:150] + ("..." if len(final_analysis) > 150 else "")
        st.markdown("#### 📋 분석 결과 요약")
        st.markdown(preview)
        
        if len(final_analysis) > 150:
            if st.button("📖 전체 분석 결과 보기", key="view_full_analysis"):
                st.session_state[f'popup_content_final_analysis'] = {
                    'title': "최종 AI 분석 결과",
                    'content': final_analysis,
                    'type': "분석 결과",
                    'show': True
                }
                st.rerun()
        
        st.markdown("#### 🔧 문서 삽입 옵션")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📝 요약만 삽입", key="insert_summary_only"):
                try:
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
                    st.error(f"전체 삽입 실패: {e}")
    else:
        st.info("최종 분석 결과가 아직 생성되지 않았습니다.")

def _render_step_by_step_tab(results):
    """Step by step results tab rendering"""
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
                        for i, item in enumerate(step_data[:3], 1):
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

def _render_references_tab(results):
    """References tab rendering - changed to vertical layout"""
    internal_refs = results.get('step3_internal_references', [])
    external_refs = results.get('step3_external_references', [])
    
    # Internal documents (top)
    st.markdown("#### 📁 사내 문서")
    if internal_refs:
        for i, ref in enumerate(internal_refs[:5], 1):
            title = ref.get('title', f'문서 {i}')
            summary = ref.get('summary', ref.get('content', ''))[:100]
            
            with st.expander(f"{i}. {title}"):
                st.write(f"**요약:** {summary}...")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button(f"📝 요약 삽입", key=f"insert_internal_sum_{i}"):
                        _insert_to_document(ref.get('summary', ''), f"사내문서 {i} 요약")
                with col_b:
                    if st.button(f"📄 전체 삽입", key=f"insert_internal_full_{i}"):
                        _insert_to_document(ref.get('content', ''), f"사내문서 {i}")
    else:
        st.info("관련 사내 문서가 없습니다.")
    
    st.markdown("---")
    
    # External materials (bottom)
    st.markdown("#### 🌐 외부 자료")
    if external_refs:
        for i, ref in enumerate(external_refs[:5], 1):
            title = ref.get('title', f'자료 {i}')
            summary = ref.get('summary', ref.get('content', ''))[:100]
            
            with st.expander(f"{i}. {title}"):
                st.write(f"**요약:** {summary}...")
                
                if ref.get('url'):
                    st.markdown(f"🔗 [원문 링크]({ref['url']})")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button(f"📝 요약 삽입", key=f"insert_external_sum_{i}"):
                        _insert_to_document(ref.get('summary', ''), f"외부자료 {i} 요약")
                with col_b:
                    if st.button(f"📄 전체 삽입", key=f"insert_external_full_{i}"):
                        _insert_to_document(ref.get('content', ''), f"외부자료 {i}")
    else:
        st.info("관련 외부 자료가 없습니다.")

def _render_action_recommendations_tab(results):
    """Action recommendations tab rendering"""
    st.markdown("#### 💡 추천 액션")
    
    final_analysis = results.get('step4_final_analysis', '')
    
    if final_analysis:
        if "실행 가능한 제안사항" in final_analysis:
            suggestions_section = final_analysis.split("실행 가능한 제안사항")[1].split("##")[0]
            st.markdown("**🎯 AI 추천 액션:**")
            st.markdown(suggestions_section[:300] + ("..." if len(suggestions_section) > 300 else ""))
    
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
    """Panel control buttons"""
    st.markdown("---")
    st.markdown("### 🎛️ 패널 제어")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 새 분석", key="new_analysis", use_container_width=True):
            st.session_state.analysis_text = ""
            st.session_state.analysis_mode = "manual"
            st.session_state.analysis_completed = False
            st.session_state.enhanced_analysis_results = {}
            st.rerun()
    
    with col2:
        if st.button("❌ 패널 닫기", key="close_ai_panel", use_container_width=True):
            _close_ai_panel()

def _insert_to_document(content, content_type):
    """Insert analysis results to document - improved version"""
    if not content or not content.strip():
        st.warning("⚠️ 삽입할 내용이 없습니다.")
        return
    
    try:
        current_content = st.session_state.get('document_content', '')
        
        separator = "\n\n---\n\n" if current_content.strip() else ""
        timestamp = __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M")
        header = f"[{content_type} 삽입 | {timestamp}]"
        
        clean_content = content.strip()
        if len(clean_content) > 2000:
            clean_content = clean_content[:2000] + f"\n\n[원본 길이: {len(content)}자, 표시: 2000자로 제한됨]"
        
        new_content = current_content + separator + header + "\n\n" + clean_content
        
        st.session_state.document_content = new_content
        st.session_state['document_content'] = new_content
        
        # 다른 편집기 키들도 업데이트 (존재하는 경우)
        editor_keys = ['document_content_main_editor', 'document_editor_main_content', 'app_enhanced_main_editor']
        for key in editor_keys:
            if key in st.session_state:
                st.session_state[key] = new_content
        
        st.success(f"✅ {content_type}가 문서에 삽입되었습니다!")
        st.info(f"📝 삽입된 내용 길이: {len(clean_content):,}자")
        
        st.session_state.insert_success_message = f"✅ {content_type} 삽입 완료"
        
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ 문서 삽입 중 오류 발생: {str(e)}")
        st.error(f"오류 상세: {type(e).__name__}")
        
        try:
            st.session_state.document_content = (st.session_state.get('document_content', '') + 
                                               f"\n\n[오류로 인한 단순 삽입]\n{content[:500]}...")
            st.warning("⚠️ 일부 내용만 삽입되었습니다.")
        except Exception as e2:
            st.error(f"❌ 복구 삽입도 실패: {str(e2)}")

def _request_additional_analysis(prompt, analysis_type):
    """Request additional analysis"""
    st.info(f"🔄 {analysis_type} 생성 중...")
    
    try:
        from utils.ai_service import AIService
        ai_service = AIService()
        
        result = ai_service.get_ai_response(prompt)
        
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
    """Close AI panel"""
    st.session_state.ai_panel_open = False
    st.session_state.analysis_mode = None
    st.session_state.analysis_text = ""
    st.session_state.analysis_in_progress = False
    st.session_state.auto_start_analysis = False
    st.rerun()
