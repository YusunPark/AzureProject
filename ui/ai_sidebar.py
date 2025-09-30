"""
AI 사이드바 UI 컴포넌트
"""
import streamlit as st
from state.session_state import session_state
from services.ai_analysis_service import AIAnalysisService

def render_ai_sidebar():
    """AI 사이드바 패널 렌더링"""
    if not st.session_state.ai_panel_open:
        return
    
    st.markdown("## 🤖 AI 문서 어시스턴트")
    
    # 삽입 성공 메시지 표시 (이전 세션에서 설정된 경우)
    if st.session_state.get('insert_success_message'):
        st.info(st.session_state.insert_success_message)
        # 메시지 표시 후 클리어 (다음 렌더링에서는 보이지 않음)
        del st.session_state.insert_success_message
    
    # 검색 모드 선택
    search_mode = st.radio(
        "검색 모드 선택:",
        ["전체 문서 기반", "선택된 텍스트 기반"],
        key="search_mode"
    )
    
    # 선택된 텍스트 기반일 때 텍스트 선택 인터페이스 표시
    if search_mode == "선택된 텍스트 기반":
        from ui.text_selection import create_text_selection_input
        create_text_selection_input()
    
    # AI 분석 시작 버튼
    if st.button("🚀 AI 분석 시작"):
        _handle_ai_analysis_start(search_mode)
    
    # 분석 완료 후 결과 표시
    if st.session_state.analysis_state == 'completed':
        _render_analysis_results()
    
    # 패널 닫기 버튼
    if st.button("❌ 패널 닫기", key="close_panel"):
        session_state.toggle_ai_panel()
        st.rerun()

def _handle_ai_analysis_start(search_mode):
    """AI 분석 시작 처리"""
    # 분석 상태 초기화 및 기존 결과 클리어
    st.session_state.analysis_state = 'analyzing'
    st.session_state.enhanced_prompt = None
    st.session_state.internal_search_results = []
    st.session_state.external_search_results = []
    st.session_state.analysis_result = None
    
    # 분석 쿼리 결정
    if search_mode == "선택된 텍스트 기반":
        search_query = st.session_state.selected_text
    else:
        search_query = st.session_state.document_content
    
    # 디버깅 정보 표시
    _show_debug_info(search_mode, search_query)
    
    if search_query and search_query.strip():
        st.success("✅ 분석을 시작합니다...")
        analysis_service = AIAnalysisService()
        analysis_service.run_enhanced_analysis_process(search_query.strip())
        st.session_state.analysis_state = 'completed'
    else:
        st.error("❌ 분석할 내용이 없습니다. 문서에 내용을 입력하거나 텍스트를 선택해주세요.")
        _render_test_analysis_button()
        st.session_state.analysis_state = 'idle'

def _show_debug_info(search_mode, search_query):
    """디버깅 정보 표시"""
    with st.expander("🔍 디버그 정보"):
        st.write(f"- 검색 모드: {search_mode}")
        st.write(f"- 선택된 텍스트: {st.session_state.get('selected_text', 'None')}")
        st.write(f"- 문서 내용 길이: {len(str(st.session_state.get('document_content', '')))}")
        st.write(f"- 최종 쿼리 길이: {len(str(search_query)) if search_query else 0}")

def _render_test_analysis_button():
    """테스트 분석 버튼 렌더링"""
    if st.button("📝 테스트용 샘플 내용으로 분석하기"):
        test_query = "AI와 머신러닝을 활용한 비즈니스 프로세스 개선 방안에 대해 분석해주세요."
        st.info(f"테스트 쿼리로 분석합니다: {test_query}")
        analysis_service = AIAnalysisService()
        analysis_service.run_enhanced_analysis_process(test_query)

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