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
    
    # 검색 모드 선택
    search_mode = st.radio(
        "검색 모드 선택:",
        ["전체 문서 기반", "선택된 텍스트 기반"],
        key="search_mode"
    )
    
    # 선택된 텍스트 표시
    if search_mode == "선택된 텍스트 기반" and st.session_state.selected_text:
        st.markdown("**선택된 텍스트:**")
        st.markdown(f"```\n{st.session_state.selected_text}\n```")
    
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
    if st.session_state.get('analysis_state') != 'analyzing':
        st.session_state.analysis_state = 'analyzing'
        
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
        else:
            st.error("❌ 분석할 내용이 없습니다. 문서에 내용을 입력하거나 텍스트를 선택해주세요.")
            _render_test_analysis_button()
        
        st.session_state.analysis_state = 'completed'

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
        if st.button("📝 문서에 삽입", key="insert_main_analysis"):
            _insert_content_to_document(result.get('content', ''))
            st.success("✅ 분석 결과가 문서에 삽입되었습니다!")
    else:
        st.info("분석 결과가 없습니다. AI 분석을 실행해주세요.")

def _render_recommendations_tab():
    """문서 추천 탭 렌더링"""
    st.markdown("### 📚 추천 문서")
    
    # 사내 문서 결과 표시
    internal_docs = st.session_state.get('internal_search_results', [])
    if internal_docs:
        st.markdown("#### 📁 사내 문서")
        for doc in internal_docs[:3]:
            with st.expander(f"📄 {doc.get('title', '제목 없음')}"):
                st.markdown(f"**요약:** {doc.get('summary', 'N/A')}")
                st.markdown(f"**출처:** {doc.get('source_detail', 'N/A')}")
                if st.button(f"📝 삽입", key=f"insert_internal_{doc.get('id')}"):
                    _insert_content_to_document(doc.get('content', ''))
    
    # 외부 문서 결과 표시
    external_docs = st.session_state.get('external_search_results', [])
    if external_docs:
        st.markdown("#### 🌐 외부 레퍼런스")
        for doc in external_docs[:3]:
            with st.expander(f"📄 {doc.get('title', '제목 없음')}"):
                st.markdown(f"**요약:** {doc.get('summary', 'N/A')}")
                st.markdown(f"**출처:** {doc.get('url', 'N/A')}")
                if st.button(f"📝 삽입", key=f"insert_external_{doc.get('id')}"):
                    _insert_content_to_document(doc.get('content', ''))

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
                    _insert_content_to_document(refined_text)
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
                    _insert_content_to_document(structured_content)
    else:
        st.info("텍스트를 선택하면 구조화 기능을 사용할 수 있습니다.")

def _insert_content_to_document(content):
    """문서에 내용 삽입"""
    current_content = st.session_state.document_content
    new_content = current_content + f"\n\n{content}"
    st.session_state.document_content = new_content