# app.py
import streamlit as st
import time
import json

import textwrap
from typing import List, Dict

st.set_page_config(page_title="AI 문서 맥락 추천 (Prototype)", layout="wide")

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
# 목업 추천 데이터
# -------------------------
recommendations = [
    {
        "title": "AI 기반 문서 자동화 도구의 ROI 분석",
        "summary": "기업에서 AI 문서 도구 도입 시 평균 35% 생산성 향상과 연간 $50,000 비용 절감 효과를 보여주는 최신 연구 결과입니다.",
        "full_content": """
        <h3>AI 문서 자동화 도구의 ROI 분석</h3>
        <p><strong>주요 발견사항:</strong></p>
        <ul>
            <li>평균 35% 생산성 향상</li>
            <li>연간 $50,000 비용 절감</li>
            <li>문서 작성 시간 40% 단축</li>
            <li>오류율 60% 감소</li>
        </ul>
        <p><strong>구현 권장사항:</strong> 단계적 도입을 통해 사용자 적응도를 높이고, 충분한 교육을 제공하여 최대 효과를 달성할 수 있습니다.</p>
        """,
        "source": "McKinsey & Company",
        "type": "research"
    },
    {
        "title": "문서 작성 효율성 향상을 위한 베스트 프랙티스",
        "summary": "구조화된 문서 템플릿과 AI 어시스턴트를 활용한 효과적인 문서 작성 방법론과 실무 적용 사례를 제시합니다.",
        "full_content": """
        <h3>문서 작성 효율성 향상 방법론</h3>
        <p><strong>핵심 전략:</strong></p>
        <ol>
            <li>표준화된 템플릿 활용</li>
            <li>AI 어시스턴트 통합</li>
            <li>실시간 협업 도구 사용</li>
            <li>자동화된 검토 프로세스</li>
        </ol>
        <p>이러한 방법론을 통해 문서 품질을 유지하면서도 작성 시간을 대폭 단축할 수 있습니다.</p>
        """,
        "source": "Harvard Business Review",
        "type": "article"
    }
]


# -------------------------
# 초기 문서 텍스트
# -------------------------
DEFAULT_DOCUMENT = """# 프로젝트 제안서

## 1. 프로젝트 개요
본 프로젝트는 인공지능 기반의 문서 작성 도구를 개발하여 업무 효율성을 극대화하는 것을 목표로 합니다. 기존의 문서 편집기에 AI 기능을 통합하여 사용자가 더욱 효과적으로 문서를 작성할 수 있도록 지원합니다.

## 2. 주요 기능
AI 문서 맥락 추천 시스템은 사용자가 작성 중인 내용을 분석하여 관련성 높은 자료와 정보를 실시간으로 제안합니다. 이를 통해 작성자는 보다 풍부하고 정확한 내용으로 문서를 완성할 수 있습니다.

## 3. 기대 효과
이 시스템을 도입함으로써 문서 작성 시간을 30% 단축하고, 정보의 정확성을 크게 향상시킬 수 있을 것으로 예상됩니다.
"""

# -------------------------
# CSS 스타일 (툴바, 카드, 하이라이트 등)
# -------------------------
st.markdown(
    """
    <style>
    /* 툴바 */
    .top-toolbar {
        background-color: #f7f7f7;
        height: 50px;
        display: flex;
        align-items: center;
        padding: 0 12px;
        border-bottom: 1px solid #e5e7eb;
    }
    .toolbar-left, .toolbar-center, .toolbar-right {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .toolbar-left { flex: 1; }
    .toolbar-center { flex: 1; justify-content: center; }
    .toolbar-right { flex: 1; justify-content: flex-end; }

    .ai-button {
        background-color: #8b5cf6;
        color: white;
        padding: 8px 12px;
        border-radius: 6px;
        border: none;
        cursor: pointer;
        font-weight: 600;
    }
    .ai-button:hover { opacity: 0.9; }

    /* 문서 컨테이너 */
    .doc-container {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        max-width: 800px;
        margin: 16px auto;
        border: 1px solid #e5e7eb;
    }

    /* 추천 카드 */
    .rec-card {
        background-color: white;
        border: 1px solid #e5e7eb;
        border-radius: 6px;
        padding: 12px;
        margin-bottom: 12px;
    }

    .rec-title { font-weight: 700; font-size: 15px; color: #1f2937; }
    .rec-summary { font-size: 13px; color: #374151; margin-top: 6px; }
    .rec-meta { font-size: 12px; color: #6b7280; margin-top: 8px; }

    /* 하이라이트 (삽입 시) */
    .insert-highlight { background-color: #fef3c7; padding: 2px 4px; border-radius: 4px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------
# 세션 상태 초기화
# -------------------------
if "document_text" not in st.session_state:
    st.session_state.document_text = DEFAULT_DOCUMENT
if "analysis_log" not in st.session_state:
    st.session_state.analysis_log = []
if "recommendations" not in st.session_state:
    st.session_state.recommendations = recommendations
if "selected_text" not in st.session_state:
    st.session_state.selected_text = ""
if "last_insertion" not in st.session_state:
    st.session_state.last_insertion = {"text": "", "timestamp": 0}

# -------------------------
# 상단 툴바 (st.columns 활용)
# -------------------------
with st.container():
    st.markdown(
        """
        <div class="top-toolbar">
            <div class="toolbar-left">
                <button onclick="return false;">저장</button>
                <button onclick="return false;">실행취소</button>
                <button onclick="return false;">다시실행</button>
            </div>
            <div class="toolbar-center">
                <button onclick="return false;">굵게</button>
                <button onclick="return false;">기울임</button>
                <button onclick="return false;">밑줄</button>
                <button onclick="return false;">정렬</button>
            </div>
            <div class="toolbar-right">
                <button class="ai-button" id="ai_run_button">AI 추천 실행</button>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Note: The HTML button above is visual only. 실제 동작은 아래의 Streamlit 버튼으로 처리합니다.

# -------------------------
# 메인 레이아웃: columns으로 메인/사이드 구성 (비율로 대체)
# -------------------------
col_main, col_sidebar = st.columns([3, 1])

# -------------------------
# 메인: 문서 에디터 (이전)
# -------------------------
# with col_main:
#     st.markdown('<div class="doc-container">', unsafe_allow_html=True)

#     st.markdown("### 문서 편집 영역")
#     # text area
#     doc_text = st.text_area(
#         label="문서 내용 (편집 가능)",
#         value=st.session_state.document_text,
#         height=600,
#         key="text_area_main"
#     )
#     # 문서 저장 (session_state 동기화)
#     st.session_state.document_text = doc_text

#     st.markdown("</div>", unsafe_allow_html=True)

#     # 미리보기 영역 (삽입 하이라이트 표시용)
#     st.markdown("#### 문서 미리보기 (삽입 하이라이트 표시)")
#     # 하이라이트가 있으면 표시, 없으면 일반 마크다운
#     if st.session_state.last_insertion["text"]:
#         inserted = st.session_state.last_insertion["text"]
#         # 하이라이트를 텍스트 끝에 추가해서 보여주기 (프로토타입)
#         preview_html = st.session_state.document_text.replace(
#             inserted,
#             f'<span class="insert-highlight">{inserted}</span>'
#         ) if inserted in st.session_state.document_text else st.session_state.document_text + f"<p><span class='insert-highlight'>{inserted}</span></p>"
#         st.markdown(preview_html, unsafe_allow_html=True)
#     else:
#         st.markdown(st.session_state.document_text)


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



# -------------------------
# 사이드 패널 (우측 패널 흉내)
# -------------------------
with col_sidebar:
    # 고정 폭 스타일(브라우저 폭에 따라 다름)
    st.markdown("### AI 추천 사이드 패널")
    st.markdown("패널 너비: 320px (디자인 기준)")

    # 검색 모드 배지 (텍스트)
    st.markdown("검색 모드: 전체 문서 기반 또는 선택된 텍스트 기반")

    # 선택된 텍스트 입력 (사용자가 수동으로 선택 텍스트를 붙여넣을 수 있도록)
    st.markdown("선택된 텍스트 (최대 3줄):")
    selected_text_input = st.text_area("선택 텍스트 입력", value=st.session_state.selected_text, height=80, key="selected_text_input")
    st.session_state.selected_text = selected_text_input.strip()

    # 버튼: 전체 문서 기반 실행 / 선택 텍스트 기반 실행
    if st.button("AI 추천 실행 (전체 문서 기반)"):
        mode = "전체 문서 기반"
        target_text = st.session_state.document_text
        st.session_state.analysis_log = []
        run_analysis = True
        st.session_state.current_mode = mode
        st.session_state.analysis_target = target_text
    elif st.button("선택된 텍스트로 AI 추천"):
        mode = "선택 텍스트 기반"
        target_text = st.session_state.selected_text or st.session_state.document_text
        st.session_state.analysis_log = []
        run_analysis = True
        st.session_state.current_mode = mode
        st.session_state.analysis_target = target_text
    else:
        run_analysis = False

    # AI 사고 과정 표시 공간
    st.markdown("---")
    st.markdown("AI 분석 진행 상태:")
    status_box = st.empty()

    # 분석 시뮬레이션 단계
    analysis_steps = [
        "선택된 텍스트 분석 중...",
        "관련 키워드 추출 중...",
        "데이터베이스에서 관련 문서 검색 중...",
        "AI 모델로 관련성 점수 계산 중...",
        "최적의 추천 결과 생성 중..."
    ]

    # 분석 실행
    if run_analysis:
        # 단계별 시뮬레이션 (각 단계 0.6초 ~ 1.0초)
        status_lines = []
        for i, step in enumerate(analysis_steps):
            status_lines.append(f"진행: {step}")
            status_box.markdown("\n".join(status_lines))
            # 단계 수행 시간(시뮬레이션)
            time.sleep(0.6 + (i * 0.1))
        # 완료 상태
        status_lines = [s.replace("진행:", "완료:") for s in status_lines]
        status_box.markdown("\n".join(status_lines))
        # 추천 결과 갱신 (모의 데이터)
        st.session_state.recommendations = recommendations  # 실제 연동시에는 API 결과를 넣을 것
        st.success("AI 추천 완료: {}개의 추천을 찾았습니다.".format(len(st.session_state.recommendations)))

    # 분석 로그(토글)
    if st.checkbox("AI 사고 과정 보기"):
        st.markdown("분석 대상 모드: {}".format(st.session_state.get("current_mode", "미지정")))
        st.markdown("분석 대상(일부):")
        sample = st.session_state.get("analysis_target", "")[:240].replace("\n", " ")
        st.markdown(f"> {sample if sample else '없음'}")

    st.markdown("---")
    st.markdown("추천 문서 목록:")

    # 추천 카드 표시
    for idx, rec in enumerate(st.session_state.recommendations):
        with st.container():
            st.markdown('<div class="rec-card">', unsafe_allow_html=True)
            st.markdown(f"<div class='rec-title'>{rec['title']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='rec-summary'>{rec['summary']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='rec-meta'>출처: {rec['source']} | 유형: {rec['type']}</div>", unsafe_allow_html=True)

            # 버튼들: 열기 / 문서에 삽입 (placeholder 동작)
            col_a, col_b = st.columns([1, 1])
            with col_a:
                if st.button(f"열기 - {idx}", key=f"open_{idx}"):
                    st.info(f"플레이스홀더: '{rec['title']}' 문서를 새 창에서 여는 동작을 여기에 연결하세요.")
            with col_b:
                if st.button(f"문서에 삽입 - {idx}", key=f"insert_{idx}"):
                    # 문서 끝에 삽입 (제약: cursor 위치 제어 불가)
                    insert_text = f"\n\n[추천 삽입] {rec['title']}\n{rec['summary']}\n출처: {rec['source']}\n"
                    st.session_state.document_text = st.session_state.document_text + insert_text
                    st.session_state.text_area_main = st.session_state.document_text  # textarea 동기화
                    # 하이라이트 효과 시뮬레이션: last_insertion 저장 후 3초후 해제
                    st.session_state.last_insertion["text"] = insert_text.strip()
                    st.session_state.last_insertion["timestamp"] = time.time()
                    st.success("문서에 삽입되었습니다. (문서 끝에 삽입됨 — 실제 편집기 연동 시 커서 위치로 삽입 가능)")
                    # 3초 후 하이라이트 제거 (비동기 불가하므로 바로 표시 후 sleep)
                    time.sleep(3)
                    st.session_state.last_insertion["text"] = ""
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("개인정보 안내:")
    st.markdown("개인정보는 안전하게 보호되며, 분석 목적으로만 사용됩니다.")

# -------------------------``
# 하단: 디버그 / 상태 정보 (개발용)
# -------------------------
with st.expander("개발용 상태 정보 (디버그)"):
    st.write("현재 세션 문서 길이:", len(st.session_state.document_text))
    st.write("선택된 텍스트:", st.session_state.selected_text or "(없음)")
    st.write("추천 개수:", len(st.session_state.recommendations))
    st.write("마지막 삽입:", st.session_state.last_insertion)

# -------------------------
# 추가 설명 (주의)
# -------------------------
st.markdown(
    """
    **주의 및 구현 힌트 (개발자용)**  
    1. 이 프로토타입은 Streamlit 한계로 인해 커서 위치 제어와 텍스트 실제 선택 범위 하이라이트를 완전하게 구현하지 않습니다.  
    2. OnlyOffice 플러그인으로 통합할 때는 OnlyOffice 편집기 API(편집기 내 커서 위치, 범위 선택, 문서 구성요소 삽입 등)를 사용하여 정확한 삽입과 하이라이트를 적용해야 합니다.  
    3. 실제 AI 연결 시에는 Azure OpenAI 또는 내부 엔드포인트를 호출하고, 결과를 `st.session_state.recommendations` 형태로 넣어 표시하면 됩니다.  
    """
)
