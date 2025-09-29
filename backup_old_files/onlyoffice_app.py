# app_onlyoffice.py
import streamlit as st
import json
import time

st.set_page_config(page_title="AI 문서 맥락 추천 (OnlyOffice 연동)", layout="wide")

# -------------------------
# OnlyOffice 설정
# -------------------------
DEFAULT_DOC_URL = "https://documentserver.onlyoffice.com/sample.docx"
DEFAULT_DOC_KEY = "unique_doc_001"

if "onlyoffice_config" not in st.session_state:
    st.session_state.onlyoffice_config = {
        "document": {
            "title": "프로젝트 제안서",
            "url": DEFAULT_DOC_URL,
            "fileType": "docx",
            "key": DEFAULT_DOC_KEY
        },
        "editorConfig": {
            "callbackUrl": "",  # 문서 저장 후 호출 URL
            "mode": "edit",
            "lang": "ko"
        }
    }

# -------------------------
# 목업 추천 데이터
# -------------------------
recommendations = [
    {"title": "AI 자동화 ROI 분석", "summary": "문서 자동화 도구의 생산성 효과", "source": "McKinsey"},
    {"title": "문서 작성 베스트 프랙티스", "summary": "효율적인 작성 전략 소개", "source": "Harvard"}
]

# -------------------------
# 사이드바: AI 추천
# -------------------------
with st.sidebar:
    st.markdown("### AI 추천 패널")
    selected_text = st.text_area("선택된 텍스트 (수동 입력 가능)", height=80)

    if st.button("선택 텍스트 기반 AI 추천"):
        st.success(f"AI 추천 실행 (선택된 텍스트): {selected_text[:100]}...")

    st.markdown("---")
    st.markdown("추천 문서")
    for idx, rec in enumerate(recommendations):
        st.markdown(f"**{rec['title']}**")
        st.markdown(f"{rec['summary']}")
        st.markdown(f"출처: {rec['source']}")
        if st.button(f"문서에 삽입 - {idx}", key=f"insert_{idx}"):
            # 삽입 시 시뮬레이션: OnlyOffice API 연동 예시
            st.session_state.last_insert = f"{rec['title']} | {rec['summary']} | {rec['source']}"
            st.success(f"추천 문서 '{rec['title']}'가 문서에 삽입되었습니다.")
        st.markdown("---")

# -------------------------
# 메인: OnlyOffice iframe
# -------------------------
col_main, col_dummy = st.columns([3, 0.1])
with col_main:
    st.markdown("### 문서 편집 영역 (OnlyOffice Editor)")
    iframe_code = f"""
    <iframe src="https://documentserver.onlyoffice.com/web-apps/apps/api/documents/api.js?config={json.dumps(st.session_state.onlyoffice_config)}"
        width="100%" height="600px" frameborder="0"></iframe>
    """
    st.components.v1.html(iframe_code, height=600)

    # 삽입된 추천 문서 표시 (시뮬레이션)
    if "last_insert" in st.session_state:
        st.markdown("#### 최근 삽입 내용 (시뮬레이션)")
        st.info(st.session_state.last_insert)
