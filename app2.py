import streamlit as st
import time
import textwrap
from html import escape

# ---------------------------
# Settings
# ---------------------------
st.set_page_config(page_title="OnlyOffice 스타일 AI 문서 추천 (Streamlit POC)", layout="wide")

PRIMARY_COLOR = "#8b5cf6"  # AI accent
TOOLBAR_BG = "#f7f7f7"
PAGE_BG = "#f8f9fa"
SIDEBAR_BG = "#fafafa"
DOC_CONTAINER_MAX_WIDTH = 800

# ---------------------------
# Mock data (목업 데이터)
# ---------------------------
recommendations = [
    {
        "title": "AI 기반 문서 자동화 도구의 ROI 분석",
        "summary": "기업에서 AI 문서 도구 도입 시 평균 35% 생산성 향상과 연간 $50,000 비용 절감 효과를 보여주는 최신 연구 결과입니다.",
        "full_content": textwrap.dedent("""
            AI 문서 자동화 도구의 ROI 분석\n\n주요 발견사항:\n- 평균 35% 생산성 향상\n- 연간 $50,000 비용 절감\n- 문서 작성 시간 40% 단축\n- 오류율 60% 감소\n\n구현 권장사항: 단계적 도입을 통해 사용자 적응도를 높이고, 충분한 교육을 제공하여 최대 효과를 달성할 수 있습니다.
        """),
        "source": "McKinsey & Company",
        "type": "research",
    },
    {
        "title": "문서 작성 효율성 향상을 위한 베스트 프랙티스",
        "summary": "구조화된 문서 템플릿과 AI 어시스턴트를 활용한 효과적인 문서 작성 방법론과 실무 적용 사례를 제시합니다.",
        "full_content": textwrap.dedent("""
            문서 작성 효율성 향상 방법론\n\n핵심 전략:\n1. 표준화된 템플릿 활용\n2. AI 어시스턴트 통합\n3. 실시간 협업 도구 사용\n4. 자동화된 검토 프로세스\n\n이러한 방법론을 통해 문서 품질을 유지하면서도 작성 시간을 대폭 단축할 수 있습니다.
        """),
        "source": "Harvard Business Review",
        "type": "article",
    }
]

# ---------------------------
# Utility functions
# ---------------------------

def local_css(css: str):
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def init_state():
    if 'doc_content' not in st.session_state:
        st.session_state.doc_content = (
            "# 새 문서\n\n이 영역에서 문서를 편집하세요. AI 추천 기능을 사용하려면 텍스트를 선택하거나 하단의 '선택된 텍스트 붙여넣기'에 내용을 넣고 '선택된 텍스트로 AI 추천'을 누르세요.\n\n예시: 문서 개요, 요구사항, 회의 메모 등"
        )
    if 'selected_text' not in st.session_state:
        st.session_state.selected_text = ''
    if 'panel_open' not in st.session_state:
        st.session_state.panel_open = True
    if 'analysis_steps' not in st.session_state:
        st.session_state.analysis_steps = []
    if 'recommendations' not in st.session_state:
        st.session_state.recommendations = []
    if 'highlight' not in st.session_state:
        st.session_state.highlight = False


# ---------------------------
# Inject CSS for layout and styling
# ---------------------------
local_css(f"""
[data-testid='stAppViewContainer'] {{
  background-color: {PAGE_BG};
}}
header .decoration {{display:none}}
.css-1d391kg {{padding-top: 0rem}}

/* 툴바 스타일 */
.toolbar-bg {{
  background: {TOOLBAR_BG};
  height: 50px;
  display: flex;
  align-items: center;
  padding: 8px 16px;
  border-bottom: 1px solid #e5e7eb;
}}

.toolbar-button {{
  border-radius: 6px;
  padding: 6px 10px;
  margin-right: 8px;
  border: 1px solid #e5e7eb;
  background: white;
  font-weight: 500;
}}

.ai-button {{
  background: {PRIMARY_COLOR};
  color: white;
  border-radius: 6px;
  padding: 8px 12px;
  font-weight: 600;
  border: none;
}}

/* 문서 컨테이너 */
.doc-container {{
  background: white;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
  padding: 24px;
  border-radius: 8px;
  max-width: {DOC_CONTAINER_MAX_WIDTH}px;
  margin: 24px auto;
  border: 1px solid #e5e7eb;
}}

/* 사이드바 너비 강제 지정 */
[data-testid='stSidebar'] > div:first-child {{
  width: 320px !important;
}}

.sidebar-style {{
  background: {SIDEBAR_BG};
  padding: 12px;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
}}

.card {{
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 12px;
  margin-bottom: 10px;
}}

.highlight-temp {{
  background-color: #fef3c7;
  padding: 8px;
  border-radius: 4px;
}}
""")

# ---------------------------
# Initialize session state
# ---------------------------
init_state()

# ---------------------------
# Top toolbar (st.columns used inside a container)
# ---------------------------
with st.container():
    st.markdown('<div class="toolbar-bg">', unsafe_allow_html=True)
    cols = st.columns([1, 2, 1])
    with cols[0]:
        # Left: 저장, 실행취소, 다시실행 (텍스트로만)
        st.markdown('<div style="display:flex; gap:6px">', unsafe_allow_html=True)
        if st.button('저장'):
            st.success('문서가 저장되었습니다.')
        if st.button('실행 취소'):
            st.info('실행 취소')
        if st.button('다시 실행'):
            st.info('다시 실행')
        st.markdown('</div>', unsafe_allow_html=True)
    with cols[1]:
        # Center: 텍스트 서식 버튼들
        st.markdown('<div style="display:flex; gap:6px; justify-content:center">', unsafe_allow_html=True)
        if st.button('굵게'):
            st.session_state.doc_content += '\n**굵은 텍스트 예시**'
        if st.button('기울임'):
            st.session_state.doc_content += '\n*기울임 텍스트 예시*'
        if st.button('밑줄'):
            st.session_state.doc_content += '\n_밑줄 예시_'
        if st.button('정렬: 가운데'):
            st.session_state.doc_content += '\n<center>가운데 정렬 예시</center>'
        st.markdown('</div>', unsafe_allow_html=True)
    with cols[2]:
        # Right: AI 추천 버튼
        if st.button('✨ AI 추천'):
            st.session_state.panel_open = True
            st.experimental_rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------
# Main content + Sidebar
# ---------------------------
main_col, side_col = st.columns([3, 1])

with main_col:
    st.markdown('<div class="doc-container">', unsafe_allow_html=True)
    st.markdown('''
    <div style="font-size:18px; font-weight:700; color:#1f2937; margin-bottom:8px">문서 편집 영역</div>
    <div style="font-size:12px; color:#6b7280; margin-bottom:12px">이 에디터는 POC 수준의 텍스트 편집기입니다. 자세한 에디터 기능은 실제 OnlyOffice 통합 시 확장하세요.</div>
    ''', unsafe_allow_html=True)

    doc_text = st.text_area('문서 내용', value=st.session_state.doc_content, height=600, key='doc_area')
    st.session_state.doc_content = doc_text

    # 선택된 텍스트 수동 입력 (브라우저에서 텍스트를 드래그로 선택하는 기능을 Streamlit에서 직접 감지하기 어려움)
    st.markdown('''
    <div style="margin-top:12px">
    <div style="font-size:14px; font-weight:600; color:#1f2937">선택된 텍스트 (직접 붙여넣기)</div>
    <div style="font-size:12px; color:#6b7280; margin-bottom:6px">에디터에서 드래그 후 복사하여 아래에 붙여넣고 '선택된 텍스트로 AI 추천'을 누르세요.</div>
    </div>
    ''', unsafe_allow_html=True)
    selected_manual = st.text_area('선택된 텍스트 직접 붙여넣기 (최대 3줄)', value=st.session_state.selected_text, height=80)
    st.session_state.selected_text = selected_manual

    # Insert position 옵션 (간단한 시뮬레이션)
    st.markdown('문서에 추천 내용을 삽입할 위치 선택 (숫자 입력 - 0이면 맨 뒤에 추가):')
    insert_pos = st.number_input('삽입 위치 (문자 인덱스)', min_value=0, value=len(st.session_state.doc_content), step=1)

    st.markdown('</div>', unsafe_allow_html=True)

with side_col:
    st.sidebar.markdown('<div class="sidebar-style">', unsafe_allow_html=True)
    st.sidebar.markdown('### AI 추천 패널')
    mode = st.sidebar.selectbox('검색 모드 선택', ('전체 문서 기반 검색', '선택된 텍스트 기반 검색'))
    st.sidebar.markdown('**선택된 텍스트:**')
    display_selected = st.session_state.selected_text or '(선택된 텍스트 없음 — 직접 붙여넣기 사용)'
    st.sidebar.markdown(f'<div style="background:#f3f4f6; padding:8px; border-radius:6px; max-height:72px; overflow:auto">{escape(display_selected)}</div>', unsafe_allow_html=True)

    # 분석 버튼
    if st.sidebar.button('선택된 텍스트로 AI 추천'):
        st.session_state.analysis_steps = []
        st.session_state.recommendations = []
        st.session_state.panel_open = True
        # perform simulated analysis below
        st.experimental_rerun()

    # Simulate analysis progress and display
    st.sidebar.markdown('---')
    st.sidebar.markdown('AI 분석 진행 상태:')

    progress_placeholder = st.sidebar.empty()
    steps = [
        '선택된 텍스트 분석 중...'
        , '관련 키워드 추출 중...'
        , '데이터베이스에서 관련 문서 검색 중...'
        , 'AI 모델로 관련성 점수 계산 중...'
        , '최적의 추천 결과 생성 중...'
    ]

    # If analysis_steps empty but user requested earlier, run simulation
    if 'analysis_requested' not in st.session_state:
        st.session_state.analysis_requested = False

    if st.session_state.selected_text and st.sidebar.button('AI 분석 시뮬레이션 시작'):
        st.session_state.analysis_requested = True
        st.session_state.analysis_steps = []
        st.session_state.recommendations = []
        st.experimental_rerun()

    # If analysis requested then simulate step-by-step
    if st.session_state.analysis_requested:
        for i, s in enumerate(steps):
            progress_placeholder.markdown(f'- {s}')
            st.session_state.analysis_steps.append({'step': s, 'status': 'in_progress' if i < len(steps)-1 else 'done'})
            time.sleep(0.6)
        # after simulation set recommendations
        st.session_state.recommendations = recommendations
        st.session_state.analysis_requested = False
        st.experimental_rerun()

    # show last statuses if available
    if st.session_state.analysis_steps:
        for i, step_item in enumerate(st.session_state.analysis_steps):
            status = '완료' if step_item.get('status') == 'done' else '진행중'
            st.sidebar.markdown(f"- {step_item['step']}  ({status})")
    else:
        st.sidebar.markdown('- 분석이 아직 실행되지 않았습니다.')

    st.sidebar.markdown('---')
    st.sidebar.markdown('추천 문서')

    # show recommendation cards
    if st.session_state.recommendations:
        for idx, rec in enumerate(st.session_state.recommendations):
            st.sidebar.markdown(f"<div class='card'>", unsafe_allow_html=True)
            st.sidebar.markdown(f"**{escape(rec['title'])}**")
            st.sidebar.markdown(f"{escape(rec['summary'])[:150]}...")
            st.sidebar.markdown(f"출처: {escape(rec['source'])}")
            open_key = f'open_{idx}'
            insert_key = f'insert_{idx}'
            if st.sidebar.button(f'열기 - {idx+1}', key=open_key):
                # show full content in a modal-like area (just expand in main area)
                st.session_state.temp_open = rec
                st.experimental_rerun()
            if st.sidebar.button(f'문서에 삽입 - {idx+1}', key=insert_key):
                # perform insertion simulation
                content_to_insert = rec['full_content']
                doc = st.session_state.doc_content
                pos = min(int(insert_pos), len(doc))
                new_doc = doc[:pos] + '\n\n' + content_to_insert + '\n\n' + doc[pos:]
                st.session_state.doc_content = new_doc
                # highlight simulation
                st.session_state.highlight = True
                st.experimental_rerun()
            st.sidebar.markdown('</div>', unsafe_allow_html=True)
    else:
        st.sidebar.markdown('_추천 문서가 없습니다. 분석을 실행하세요._')

    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    st.sidebar.markdown('---')
    st.sidebar.markdown('개인정보는 안전하게 보호되며, 분석 목적으로만 사용됩니다.')

# ---------------------------
# If user opened a recommendation, show it in main area
# ---------------------------
if 'temp_open' in st.session_state and st.session_state.temp_open:
    rec = st.session_state.temp_open
    st.markdown('---')
    st.markdown(f"### {rec['title']}")
    st.markdown(f"출처: {rec['source']}")
    st.markdown('---')
    st.markdown(rec['full_content'])
    if st.button('닫기'):
        st.session_state.temp_open = None
        st.experimental_rerun()

# ---------------------------
# Highlight effect simulation
# ---------------------------
if st.session_state.highlight:
    # show a temporary highlighted note near the editor
    st.markdown('<div class="highlight-temp">추천 문서가 문서에 삽입되었습니다. 3초 후 하이라이트가 사라집니다.</div>', unsafe_allow_html=True)
    time.sleep(3)
    st.session_state.highlight = False
    st.experimental_rerun()

# ---------------------------
# Footer / usage tips
# ---------------------------
st.markdown('''
---
**사용 팁 (POC):**
- 에디터에서 텍스트를 드래그 후 복사하여 '선택된 텍스트 직접 붙여넣기'에 넣으세요.
- '선택된 텍스트로 AI 추천' 또는 'AI 분석 시뮬레이션 시작'으로 추천을 실행하세요.
- 실제 OnlyOffice 통합 시에는 에디터의 selection/커서 위치를 브리지로 전달하여 삽입 위치를 정확히 제어합니다.
''')
