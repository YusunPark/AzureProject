"""
문서 삽입 테스트 스크립트
삽입 기능이 제대로 작동하는지 간단히 테스트합니다.
"""
import streamlit as st

def test_document_insertion():
    """문서 삽입 기능 테스트"""
    
    st.title("🧪 문서 삽입 기능 테스트")
    
    # 테스트용 문서 내용
    if 'test_document_content' not in st.session_state:
        st.session_state.test_document_content = "초기 문서 내용입니다.\n\n이 내용 아래에 AI 분석 결과가 삽입됩니다."
    
    # 현재 문서 내용 표시
    st.markdown("### 📄 현재 문서 내용:")
    current_content = st.text_area(
        "문서 내용",
        value=st.session_state.test_document_content,
        height=300,
        key="test_doc_editor"
    )
    
    # 문서 내용 동기화
    if current_content != st.session_state.test_document_content:
        st.session_state.test_document_content = current_content
    
    st.markdown("---")
    
    # 테스트용 AI 분석 결과
    test_analysis_result = """
### AI 분석 결과

**핵심 내용 요약:**
- 문서의 주요 목적과 내용을 분석했습니다
- 개선 가능한 부분들을 식별했습니다
- 추가 권장사항을 제시합니다

**개선점:**
1. 구조 개선
2. 내용 보완  
3. 가독성 향상

**참고 자료:**
- 관련 문서 1
- 관련 문서 2
"""
    
    st.markdown("### 🤖 테스트용 AI 분석 결과:")
    st.markdown(test_analysis_result)
    
    # 삽입 버튼
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📝 테스트 삽입", type="primary", use_container_width=True):
            # 간단한 삽입 로직
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            insert_content = f"\n\n## AI 분석 결과 ({timestamp})\n\n{test_analysis_result.strip()}\n\n"
            new_content = st.session_state.test_document_content + insert_content
            
            # 직접 업데이트
            st.session_state.test_document_content = new_content
            
            st.success(f"✅ 삽입 완료! ({len(insert_content):,}자 추가됨)")
            st.rerun()
    
    with col2:
        if st.button("🗑️ 내용 초기화", use_container_width=True):
            st.session_state.test_document_content = "초기 문서 내용입니다.\n\n이 내용 아래에 AI 분석 결과가 삽입됩니다."
            st.rerun()
    
    # 디버깅 정보
    with st.expander("🔍 디버깅 정보"):
        st.write(f"- 세션 상태 길이: {len(st.session_state.test_document_content):,}자")
        st.write(f"- Widget 값 길이: {len(current_content):,}자")
        st.write(f"- 동기화 상태: {'✅' if current_content == st.session_state.test_document_content else '❌'}")
        
        if st.button("📋 세션 상태 내용 보기"):
            st.text(st.session_state.test_document_content)

if __name__ == "__main__":
    test_document_insertion()