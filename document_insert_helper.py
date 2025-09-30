"""
문서 삽입 기능 개선 - 대안적 접근법
st.rerun() 없이 동작하는 삽입 기능
"""
import streamlit as st
from datetime import datetime

def improved_insert_content_to_document(content: str, content_type: str):
    """개선된 문서 삽입 함수 - st.rerun() 사용하지 않음"""
    try:
        # 현재 문서 내용 가져오기
        current_content = st.session_state.get('document_content', '')
        
        # 타임스탬프 생성
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 삽입할 내용 구성
        insert_content = f"\n\n## {content_type} ({timestamp})\n\n{content}\n\n"
        new_content = current_content + insert_content
        
        # 세션 상태 업데이트
        st.session_state.document_content = new_content
        
        # 즉시 성공 메시지 (rerun 없이)
        st.success(f"✅ {content_type} 삽입 완료!")
        st.info(f"📝 {len(insert_content):,}자가 추가되었습니다")
        
        # 삽입된 내용 미리보기
        with st.expander("📄 삽입된 내용 미리보기"):
            st.markdown(insert_content)
        
        # 사용자에게 새로고침 안내
        st.info("💡 **메인 페이지에서 F5키를 눌러 새로고침하거나, 문서 내용 영역을 클릭해보세요.**")
        
        return True
        
    except Exception as e:
        st.error(f"❌ 삽입 실패: {str(e)}")
        return False

# 메인 페이지용 동기화 함수
def sync_document_content():
    """문서 내용 동기화"""
    # 세션 상태와 widget 간 동기화
    session_content = st.session_state.get('document_content', '')
    
    # 새로운 키를 사용하여 강제 업데이트
    update_key = f"doc_editor_{hash(session_content) % 10000}"
    
    return session_content, update_key

if __name__ == "__main__":
    st.write("이 파일은 문서 삽입 기능 개선을 위한 헬퍼 함수들입니다.")