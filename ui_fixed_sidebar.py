"""
AI 사이드바의 개선된 삽입 함수 - 별도 파일로 생성
"""
import streamlit as st
from datetime import datetime

def insert_content_to_document_improved(content: str, content_type: str):
    """문서에 내용 삽입 - 개선된 안정적 버전"""
    try:
        # 현재 문서 내용 가져오기
        current_content = st.session_state.get('document_content', '')
        if current_content is None:
            current_content = ''
        
        # 타임스탬프 생성
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 삽입할 내용 구성
        insert_content = f"\n\n## 📋 {content_type} ({timestamp})\n\n{content}\n\n"
        new_content = current_content + insert_content
        
        # 세션 상태 업데이트 (가장 중요!)
        st.session_state.document_content = new_content
        
        # 삽입 성공 표시 (rerun 없이)
        st.success(f"✅ {content_type} 삽입 완료!")
        st.info(f"📝 추가된 내용: {len(insert_content):,}자")
        
        # 삽입된 내용 미리보기
        with st.expander("📄 삽입된 내용 미리보기 (클릭해서 확인)"):
            st.markdown(insert_content)
        
        # 시각적 피드백
        st.balloons()
        
        # 사용자 안내 (핵심!)
        st.markdown("""
        ### 🎯 **다음 단계:**
        1. **메인 페이지로 이동**하세요 (사이드바 외부 클릭)
        2. **문서 내용 영역**에서 새로운 분석 결과를 확인하세요
        3. 만약 내용이 보이지 않으면 **브라우저 새로고침(F5)**을 해보세요
        """)
        
        print(f"[DEBUG] 삽입 완료 - {len(insert_content):,}자 추가됨")
        
        return True
        
    except Exception as e:
        st.error(f"❌ 문서 삽입 실패: {str(e)}")
        print(f"[ERROR] 삽입 실패: {str(e)}")
        return False