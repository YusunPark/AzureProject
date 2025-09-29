# app_text_editor.py
import streamlit as st
import time
import json
import random
from datetime import datetime
from typing import Dict, List, Any

# 필요한 서비스들 import
from utils.ai_service import AIService

# 페이지 설정
st.set_page_config(
    page_title="AI 문서 작성 어시스턴트",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS 스타일 정의
def load_css():
    st.markdown("""
    <style>
    /* 전체 배경 및 기본 색상 */
    .main {
        background-color: #ffffff;
    }
    
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
    }
    
    /* 사이드바 스타일 */
    .ai-sidebar {
        background-color: #fafafa;
        border-left: 1px solid #e5e7eb;
        padding: 20px;
        height: 100vh;
        overflow-y: auto;
    }
    
    /* AI 액센트 색상 */
    .ai-accent {
        color: #8b5cf6;
        font-weight: 600;
    }
    
    .ai-background {
        background-color: #f3f4f6;
    }
    
    /* 버튼 스타일 */
    .stButton > button {
        background-color: #8b5cf6;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    
    .stButton > button:hover {
        background-color: #7c3aed;
    }
    
    /* 프로그레스 스타일 */
    .progress-step {
        display: flex;
        align-items: center;
        margin: 8px 0;
        padding: 8px;
        border-radius: 4px;
        background-color: #f8f9fa;
    }
    
    .progress-step.completed {
        background-color: #dcfce7;
        color: #166534;
    }
    
    .progress-step.current {
        background-color: #fef3c7;
        color: #92400e;
    }
    
    .progress-step.pending {
        background-color: #f1f5f9;
        color: #64748b;
    }
    
    /* 문서 카드 */
    .doc-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .doc-title {
        font-weight: 600;
        color: #1f2937;
        margin-bottom: 8px;
    }
    
    .doc-summary {
        color: #6b7280;
        font-size: 14px;
        margin-bottom: 8px;
    }
    
    .doc-source {
        color: #8b5cf6;
        font-size: 12px;
        font-style: italic;
    }
    
    /* 편집기 스타일 */
    .stTextArea textarea {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1.6;
        border-radius: 8px;
        border: 1px solid #e5e7eb;
    }
    
    /* 통계 카드 스타일 */
    .metric-card {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 12px;
        margin: 4px 0;
        text-align: center;
    }
    
    .metric-value {
        font-size: 1.5rem;
        font-weight: bold;
        color: #8b5cf6;
    }
    
    .metric-label {
        font-size: 0.8rem;
        color: #6c757d;
        margin-top: 4px;
    }
    </style>
    """, unsafe_allow_html=True)

# 더미 데이터 생성
def generate_dummy_data():
    return {
        "documents": [
            {
                "id": 1,
                "title": "AI와 머신러닝의 미래 전망",
                "summary": "인공지능 기술의 발전 방향과 산업에 미치는 영향에 대한 종합적 분석",
                "content": "인공지능 기술은 빠르게 발전하고 있으며, 특히 대규모 언어 모델과 생성형 AI의 등장으로...",
                "source": "AI Research Journal, 2024",
                "relevance_score": 0.95,
                "keywords": ["AI", "머신러닝", "미래", "기술"]
            },
            {
                "id": 2,
                "title": "디지털 트랜스포메이션 가이드",
                "summary": "기업의 디지털 전환 과정에서 고려해야 할 핵심 요소들",
                "content": "디지털 트랜스포메이션은 단순한 기술 도입이 아니라 조직 문화의 변화를 포함하는...",
                "source": "Business Innovation Review, 2024",
                "relevance_score": 0.88,
                "keywords": ["디지털", "혁신", "비즈니스", "전환"]
            },
            {
                "id": 3,
                "title": "효과적인 문서 작성 방법론",
                "summary": "명확하고 설득력 있는 문서 작성을 위한 실용적 가이드",
                "content": "좋은 문서는 명확한 구조와 논리적 흐름을 가져야 합니다. 먼저 목적을 명확히 하고...",
                "source": "Writing Excellence Handbook, 2023",
                "relevance_score": 0.82,
                "keywords": ["문서작성", "커뮤니케이션", "구조화", "방법론"]
            }
        ]
    }

# 세션 상태 초기화
def init_session_state():
    if 'ai_panel_open' not in st.session_state:
        st.session_state.ai_panel_open = False
    if 'selected_text' not in st.session_state:
        st.session_state.selected_text = ""
    if 'document_content' not in st.session_state:
        st.session_state.document_content = ""
    if 'analysis_state' not in st.session_state:
        st.session_state.analysis_state = 'idle'
    if 'dummy_data' not in st.session_state:
        st.session_state.dummy_data = generate_dummy_data()
    if 'search_results' not in st.session_state:
        st.session_state.search_results = []
    if 'current_view' not in st.session_state:
        st.session_state.current_view = "create"
    if 'current_document' not in st.session_state:
        st.session_state.current_document = None
    if 'ai_results' not in st.session_state:
        st.session_state.ai_results = {}
    if 'current_user_type' not in st.session_state:
        st.session_state.current_user_type = "general"
    if 'last_analysis' not in st.session_state:
        st.session_state.last_analysis = None
    if 'analysis_text' not in st.session_state:
        st.session_state.analysis_text = ""
    if 'analysis_user_type' not in st.session_state:
        st.session_state.analysis_user_type = "general"
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []
    if 'saved_templates' not in st.session_state:
        st.session_state.saved_templates = {}
    if 'current_action_plan' not in st.session_state:
        st.session_state.current_action_plan = None

# AI 분석 진행 상태 표시
def show_analysis_progress():
    steps = [
        ("✅", "텍스트 내용 분석", "completed"),
        ("✅", "사용자 맞춤 키워드 추출", "completed"),
        ("🔄", "관련 전문 자료 검색 중", "current"),
        ("⏳", "AI 기반 구조화 분석", "pending"),
        ("⏳", "실행 가능한 결과 생성", "pending")
    ]
    
    st.markdown("### 🤖 AI 전문 분석 진행 중")
    st.markdown("*기획자와 보고서 작성자를 위한 맞춤형 분석을 수행합니다.*")
    
    progress_container = st.empty()
    
    for i, (icon, text, status) in enumerate(steps):
        progress_html = ""
        for j, (s_icon, s_text, s_status) in enumerate(steps):
            if j <= i:
                if j == i and status == "current":
                    progress_html += f'<div class="progress-step current">{s_icon} {s_text}... (진행중)</div>'
                else:
                    progress_html += f'<div class="progress-step completed">{s_icon} {s_text}... (완료)</div>'
            else:
                progress_html += f'<div class="progress-step pending">{s_icon} {s_text}... (대기중)</div>'
        
        progress_container.markdown(progress_html, unsafe_allow_html=True)
        time.sleep(0.8)
    
    # 완료 상태
    final_html = ""
    for icon, text, _ in steps:
        final_html += f'<div class="progress-step completed">✅ {text}... (완료)</div>'
    
    progress_container.markdown(final_html, unsafe_allow_html=True)
    st.success("🎉 AI 전문 분석이 완료되었습니다! 아래에서 결과를 확인하세요.")

# 문서 추천 결과 표시
def show_recommendations(search_query="", user_type="general"):
    st.markdown("### 📚 전문 자료 추천")
    
    # 사용자 타입별 안내 메시지
    type_messages = {
        "planner": "기획자를 위한 실행 가능한 전략 자료와 계획 수립 가이드를 제공합니다.",
        "reporter": "보고서 작성자를 위한 데이터 분석 자료와 구조화된 정보를 제공합니다.",  
        "general": "선택하신 내용과 관련된 유용한 정보와 자료를 제공합니다."
    }
    
    st.info(f"💡 {type_messages.get(user_type, type_messages['general'])}")
    
    try:
        # AI 서비스 초기화
        ai_service = AIService()
        
        # 검색 쿼리가 있으면 사용자 타입별 맞춤 검색 수행
        if search_query:
            with st.spinner("AI가 전문 자료를 검색하고 분석하고 있습니다..."):
                # 텍스트 분석 (사용자 타입별)
                analysis_result = ai_service.analyze_text(search_query, user_type)
                keywords = analysis_result.get("keywords", [])
                
                # 관련 문서 검색 (사용자 타입별)
                docs = ai_service.search_related_documents(search_query, keywords, user_type)
                
                # 분석 결과 세션에 저장
                st.session_state.last_analysis = analysis_result
                
                # 분석 기록에 추가
                import datetime
                analysis_record = {
                    'timestamp': datetime.datetime.now().strftime("%m-%d %H:%M"),
                    'user_type': user_type,
                    'text_length': len(search_query),
                    'keywords_count': len(keywords)
                }
                if 'analysis_history' not in st.session_state:
                    st.session_state.analysis_history = []
                st.session_state.analysis_history.append(analysis_record)
                
                # 최대 10개만 유지
                if len(st.session_state.analysis_history) > 10:
                    st.session_state.analysis_history = st.session_state.analysis_history[-10:]
                
        else:
            # 기본 문서 표시
            docs = ai_service.search_related_documents("일반적인 업무 가이드", [], user_type)
        
        if not docs:
            st.warning("검색된 전문 자료가 없습니다. 다른 키워드로 시도해보세요.")
            return
        
        # 사용자 타입별 문서 표시
        for i, doc in enumerate(docs):
            doc_type = doc.get('document_type', '일반')
            
            with st.expander(f"📄 {doc['title']} | {doc_type} (관련도: {doc.get('relevance_score', 0.5):.0%})"):
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**📋 요약:** {doc['summary']}")
                    st.markdown(f"**🔗 출처:** {doc.get('source', '출처 불명')}")
                    
                    if doc.get('keywords'):
                        keywords_display = ', '.join(doc['keywords'][:5])
                        st.markdown(f"**🏷️ 키워드:** {keywords_display}")
                    
                    # 내용 미리보기
                    content_preview = doc['content'][:300] + "..." if len(doc['content']) > 300 else doc['content']
                    st.markdown("**📖 내용 미리보기:**")
                    st.markdown(f"```\n{content_preview}\n```")
                
                with col2:
                    st.markdown("**📝 활용 옵션**")
                    
                    if st.button(f"📝 전체 삽입", key=f"insert_full_{i}"):
                        insert_content_to_document(f"\n\n## {doc['title']}\n\n{doc['content']}\n\n*출처: {doc.get('source', '출처 불명')}*")
                    
                    if st.button(f"📋 요약만 삽입", key=f"insert_summary_{i}"):
                        insert_content_to_document(f"\n\n**{doc['title']}**\n{doc['summary']}\n*출처: {doc.get('source', '출처 불명')}*")
                    
                    if st.button(f"🔗 링크 삽입", key=f"insert_link_{i}"):
                        source_url = doc.get('source', '')
                        if source_url.startswith('http'):
                            insert_content_to_document(f"\n\n참고 자료: [{doc['title']}]({source_url})")
                        else:
                            insert_content_to_document(f"\n\n참고 자료: {doc['title']} ({source_url})")
    
    except Exception as e:
        st.error(f"전문 자료 검색 중 오류가 발생했습니다: {str(e)}")
        st.info("💡 현재는 데모 모드로 작동하고 있습니다. Azure OpenAI와 Tavily API 키를 설정하면 실제 AI 분석이 가능합니다.")
        
        # 오류 발생시 더미 데이터 사용
        ai_service = AIService()
        docs = ai_service.search_related_documents(search_query or "샘플", [], user_type)
        
        for i, doc in enumerate(docs):
            with st.expander(f"📄 {doc['title']} (샘플 데이터)"):
                st.markdown(f"**요약:** {doc['summary']}")
                st.markdown(f"**출처:** {doc['source']}")
                if st.button(f"📝 문서에 삽입", key=f"dummy_insert_{i}"):
                    insert_content_to_document(f"\n\n## {doc['title']}\n\n{doc['content']}")

# 전문 분석 결과 표시
def show_professional_analysis(analysis_result: Dict[str, Any]):
    """사용자 타입별 전문 분석 결과 표시"""
    if not analysis_result:
        st.info("분석할 텍스트를 선택하고 AI 분석을 시작해주세요.")
        return
    
    user_type = analysis_result.get('user_type', 'general')
    analysis = analysis_result.get('analysis', {})
    
    st.markdown(f"### 🎯 전문 분석 결과 ({user_type.upper()})")
    
    if user_type == "planner":
        st.markdown("#### 💡 기획자 관점 분석")
        
        if analysis.get("insights"):
            with st.expander("🔍 핵심 인사이트", expanded=True):
                st.markdown(analysis["insights"])
                if st.button("💼 인사이트 삽입", key="insert_insights"):
                    insert_content_to_document(f"\n\n## 핵심 인사이트\n{analysis['insights']}")
        
        if analysis.get("action_items"):
            with st.expander("📋 실행 액션 아이템"):
                st.markdown(analysis["action_items"])
                if st.button("🚀 액션 아이템 삽입", key="insert_actions"):
                    insert_content_to_document(f"\n\n## 실행 액션 아이템\n{analysis['action_items']}")
        
        if analysis.get("risks"):
            with st.expander("⚠️ 위험요소 및 대안"):
                st.markdown(analysis["risks"])
                if st.button("⚠️ 위험 분석 삽입", key="insert_risks"):
                    insert_content_to_document(f"\n\n## 위험요소 및 대안\n{analysis['risks']}")
        
        if analysis.get("stakeholders"):
            with st.expander("👥 이해관계자 고려사항"):
                st.markdown(analysis["stakeholders"]) 
                if st.button("👥 이해관계자 분석 삽입", key="insert_stakeholders"):
                    insert_content_to_document(f"\n\n## 이해관계자 고려사항\n{analysis['stakeholders']}")
    
    elif user_type == "reporter":
        st.markdown("#### 📊 보고서 작성자 관점 분석")
        
        if analysis.get("key_message"):
            with st.expander("🎯 핵심 메시지", expanded=True):
                st.markdown(analysis["key_message"])
                if st.button("📝 핵심 메시지 삽입", key="insert_key_message"):
                    insert_content_to_document(f"\n\n## 핵심 메시지\n{analysis['key_message']}")
        
        if analysis.get("data_points"):
            with st.expander("📈 주요 데이터 포인트"):
                st.markdown(analysis["data_points"])
                if st.button("📊 데이터 포인트 삽입", key="insert_data"):
                    insert_content_to_document(f"\n\n## 주요 데이터 포인트\n{analysis['data_points']}")
        
        if analysis.get("structure"):
            with st.expander("🏗️ 권장 보고서 구조"):
                st.markdown(analysis["structure"])
                if st.button("📋 구조 템플릿 삽입", key="insert_structure"):
                    insert_content_to_document(f"\n\n## 권장 보고서 구조\n{analysis['structure']}")
        
        if analysis.get("visualization"):
            with st.expander("📊 시각화 제안"):
                st.markdown(analysis["visualization"])
                if st.button("📈 시각화 가이드 삽입", key="insert_viz"):
                    insert_content_to_document(f"\n\n## 시각화 제안\n{analysis['visualization']}")
    
    else:
        st.markdown("#### 🔍 종합 분석")
        
        if analysis.get("topics_keywords"):
            with st.expander("🏷️ 주요 주제와 키워드", expanded=True):
                st.markdown(analysis["topics_keywords"])
                if st.button("🔖 키워드 삽입", key="insert_topics"):
                    insert_content_to_document(f"\n\n## 주요 주제와 키워드\n{analysis['topics_keywords']}")
        
        if analysis.get("summary"):
            with st.expander("📝 핵심 내용 요약"):
                st.markdown(analysis["summary"])
                if st.button("📋 요약 삽입", key="insert_summary"):
                    insert_content_to_document(f"\n\n## 핵심 내용 요약\n{analysis['summary']}")
        
        if analysis.get("improvements"):
            with st.expander("💡 개선 제안"):
                st.markdown(analysis["improvements"])
                if st.button("🔧 개선안 삽입", key="insert_improvements"):
                    insert_content_to_document(f"\n\n## 개선 제안\n{analysis['improvements']}")
    
    # 액션 플랜 생성 버튼
    st.markdown("---")
    if st.button("🚀 실행 계획 생성하기", key="generate_action_plan"):
        ai_service = AIService()
        with st.spinner("맞춤형 실행 계획을 생성하고 있습니다..."):
            action_plan = ai_service.generate_action_plan(analysis_result)
            st.session_state.current_action_plan = action_plan
            st.success("실행 계획이 생성되었습니다!")
    
    # 실행 계획 표시
    if hasattr(st.session_state, 'current_action_plan') and st.session_state.current_action_plan:
        with st.expander("📋 생성된 실행 계획", expanded=True):
            plan = st.session_state.current_action_plan.get('action_plan', '')
            st.markdown(plan)
            if st.button("📝 실행 계획 삽입", key="insert_action_plan"):
                insert_content_to_document(f"\n\n## 실행 계획\n{plan}")

# 문장 다듬기 기능
def show_text_refinement(selected_text, user_type="general"):
    st.markdown("### ✨ 전문 문장 다듬기")
    
    if not selected_text or not selected_text.strip():
        st.info("다듬을 텍스트를 선택해주세요.")
        return
    
    # 사용자 타입별 안내
    type_guides = {
        "planner": "기획자를 위한 실행력 있고 명확한 표현으로 다듬겠습니다.",
        "reporter": "보고서 작성자를 위한 객관적이고 설득력 있는 표현으로 다듬겠습니다.",
        "general": "더 명확하고 효과적인 표현으로 다듬겠습니다."
    }
    
    st.info(f"💡 {type_guides.get(user_type, type_guides['general'])}")
    
    try:
        ai_service = AIService()
        
        # 개선 스타일들
        refinement_styles = [
            ("clear", "명확성 개선", "복잡한 문장을 단순화하고 모호한 표현을 구체적으로 수정합니다.", "🔍"),
            ("professional", "전문성 강화", "해당 분야의 전문 용어와 정확한 표현을 사용하여 신뢰도를 높입니다.", "💼"),
            ("concise", "간결성 개선", "불필요한 수식어와 중복 표현을 제거하여 핵심만 남깁니다.", "⚡"),
            ("persuasive", "설득력 강화", "논리적 근거와 강력한 메시지로 임팩트를 높입니다.", "🎯")
        ]
        
        cols = st.columns(2)
        
        for i, (style_key, title, explanation, icon) in enumerate(refinement_styles):
            with cols[i % 2]:
                with st.expander(f"{icon} {title}", expanded=(i == 0)):
                    st.markdown(f"**개선 방향:** {explanation}")
                    
                    with st.spinner(f"{title} 버전을 생성하고 있습니다..."):
                        refined_text = ai_service.refine_text(selected_text, style_key, user_type)
                    
                    st.markdown("**개선된 내용:**")
                    st.markdown(f"""
                    <div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin: 10px 0;">
                    {refined_text.replace('\n', '<br>')}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        if st.button(f"📝 적용하기", key=f"refine_{style_key}"):
                            insert_content_to_document(f"\n\n{refined_text}")
                            st.success(f"{title} 적용 완료!")
                    
                    with col2:
                        if st.button(f"📋 비교하기", key=f"compare_{style_key}"):
                            st.markdown("**원본 vs 개선 비교:**")
                            st.markdown(f"**원본:** {selected_text}")
                            st.markdown(f"**개선:** {refined_text}")
    
    except Exception as e:
        st.error(f"문장 다듬기 중 오류가 발생했습니다: {str(e)}")
        st.info("💡 현재는 데모 모드로 작동하고 있습니다.")
        
        # 오류 발생시 더미 데이터 사용
        refined_versions = [
            {
                "title": "명확성 개선",
                "icon": "🔍",
                "content": f"[명확성 개선 버전]\n\n{selected_text}를 더 명확하고 이해하기 쉽게 표현했습니다.\n\n→ 핵심 내용을 구체적으로 설명하고 모호한 표현을 제거했습니다.",
                "explanation": "문장 구조를 단순화하고 모호한 표현을 구체적으로 수정했습니다."
            },
            {
                "title": "전문성 강화", 
                "icon": "💼",
                "content": f"[전문성 강화 버전]\n\n{selected_text}에 전문 용어와 정확한 표현을 적용했습니다.\n\n→ 해당 분야의 전문성을 높이고 신뢰도를 개선했습니다.",
                "explanation": "해당 분야의 전문 용어를 사용하여 신뢰도를 높였습니다."
            },
            {
                "title": "간결성 개선", 
                "icon": "⚡",
                "content": f"[간결성 개선 버전]\n\n{selected_text[:len(selected_text)//2]}...\n\n→ 불필요한 표현을 제거하고 핵심만 남겼습니다.",
                "explanation": "불필요한 수식어와 중복 표현을 제거했습니다."
            }
        ]
        
        cols = st.columns(2)
        for i, version in enumerate(refined_versions):
            with cols[i % 2]:
                with st.expander(f"{version['icon']} {version['title']} (데모)"):
                    st.markdown(f"**개선된 내용:**")
                    st.markdown(version['content'])
                    st.markdown(f"**개선 사유:** {version['explanation']}")
                    
                    if st.button(f"적용하기", key=f"dummy_refine_{i}"):
                        insert_content_to_document(version['content'])

# 구조화 기능
def show_structuring(selected_text, user_type="general"):
    st.markdown("### 🏗️ 스마트 내용 구조화")
    
    if not selected_text or not selected_text.strip():
        st.info("구조화할 텍스트를 선택해주세요.")
        return
    
    # 사용자 타입별 구조화 가이드
    type_guides = {
        "planner": "기획서와 제안서에 적합한 실행 중심의 구조로 정리합니다.",
        "reporter": "보고서와 분석서에 적합한 논리적이고 데이터 중심의 구조로 정리합니다.",
        "general": "읽기 쉽고 이해하기 좋은 논리적 구조로 정리합니다."
    }
    
    st.info(f"📋 {type_guides.get(user_type, type_guides['general'])}")
    
    try:
        ai_service = AIService()
        
        # 구조화 유형들 (사용자 타입별 맞춤)
        if user_type == "planner":
            structure_types = [
                ("outline", "기획 개요서", "목차와 소제목이 있는 체계적인 기획서 구조", "📋"),
                ("steps", "실행 단계", "순차적인 실행 단계와 액션 플랜 구조", "🔄"),
                ("presentation", "프레젠테이션", "발표용 슬라이드 구조로 정리", "📊"),
                ("summary", "요약 보고", "핵심 요약과 결론 중심 구조", "📄")
            ]
        elif user_type == "reporter":
            structure_types = [
                ("outline", "분석 보고서", "데이터 분석과 결론이 명확한 보고서 구조", "📊"),
                ("summary", "경영진 요약", "핵심 내용과 권고사항 중심 구조", "📋"),
                ("qa", "FAQ 형식", "질문과 답변으로 구성된 명확한 구조", "❓"),
                ("presentation", "발표 자료", "시각적 발표에 적합한 구조", "🎯")
            ]
        else:
            structure_types = [
                ("outline", "목차 형식", "체계적인 목차와 소제목으로 구성", "📚"),
                ("steps", "단계별 가이드", "순차적인 실행 단계로 구성", "📝"),
                ("qa", "Q&A 형식", "질문과 답변 형태로 구성", "💬"),
                ("summary", "요약 구조", "핵심 요약과 상세 내용으로 구성", "📄")
            ]
        
        cols = st.columns(2)
        
        for i, (structure_key, title, description, icon) in enumerate(structure_types):
            with cols[i % 2]:
                with st.expander(f"{icon} {title}", expanded=(i == 0)):
                    st.markdown(f"**구조 특징:** {description}")
                    
                    with st.spinner(f"{title} 구조로 변환하고 있습니다..."):
                        structured_content = ai_service.structure_content(selected_text, structure_key, user_type)
                    
                    st.markdown("**구조화된 내용:**")
                    st.markdown(structured_content)
                    
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        if st.button(f"📝 구조 적용", key=f"struct_{structure_key}"):
                            insert_content_to_document(f"\n\n{structured_content}")
                            st.success(f"{title} 구조 적용 완료!")
                    
                    with col2:
                        if st.button(f"📋 템플릿 저장", key=f"save_template_{structure_key}"):
                            # 템플릿으로 저장하는 기능 (세션 상태에 저장)
                            if 'saved_templates' not in st.session_state:
                                st.session_state.saved_templates = {}
                            st.session_state.saved_templates[f"{title}_template"] = structured_content
                            st.success(f"{title} 템플릿이 저장되었습니다!")
    
    except Exception as e:
        st.error(f"구조화 중 오류가 발생했습니다: {str(e)}")
        st.info("💡 현재는 데모 모드로 작동하고 있습니다.")
        
        # 오류 발생시 더미 데이터 사용
        if user_type == "planner":
            structures = [
                {
                    "title": "기획 개요서",
                    "icon": "📋",
                    "content": f"""# 프로젝트 기획서

## 1. 개요 및 배경
{selected_text[:100]}...

## 2. 목표 설정
- 핵심 목표 1
- 핵심 목표 2
- 핵심 목표 3

## 3. 실행 계획
### 3.1 1단계: 준비
- 현황 분석
- 리소스 확보

### 3.2 2단계: 실행
- 핵심 업무 수행
- 진행 모니터링

### 3.3 3단계: 평가
- 성과 측정
- 개선 방안

## 4. 예상 성과
- 정량적 성과
- 정성적 성과

## 5. 리스크 관리
- 주요 리스크
- 대응 방안"""
                },
                {
                    "title": "실행 단계", 
                    "icon": "🔄",
                    "content": f"""# 실행 단계별 가이드

## 🎯 프로젝트 개요
{selected_text[:50]}...

## 📋 1단계: 계획 수립
**목표:** 체계적인 실행 계획 완성
- [ ] 현황 분석 완료
- [ ] 목표 설정 및 우선순위 결정
- [ ] 팀 구성 및 역할 배정
- [ ] 일정 계획 수립

## 🚀 2단계: 실행 개시
**목표:** 계획된 업무의 본격적 시작
- [ ] 킥오프 미팅 진행
- [ ] 초기 작업 착수
- [ ] 진행 상황 모니터링 체계 구축

## 📊 3단계: 모니터링 및 조정
**목표:** 지속적인 성과 관리
- [ ] 주간/월간 진행 리포트
- [ ] 이슈 발생시 대응 방안 실행
- [ ] 필요시 계획 조정

## ✅ 4단계: 완료 및 평가
**목표:** 프로젝트 성공적 마무리
- [ ] 최종 결과물 검토
- [ ] 성과 평가 및 분석
- [ ] 교훈 정리 및 문서화"""
                }
            ]
        elif user_type == "reporter":
            structures = [
                {
                    "title": "분석 보고서",
                    "icon": "📊", 
                    "content": f"""# 분석 보고서

## Executive Summary
{selected_text[:100]}...

## 1. 분석 배경
### 1.1 목적
- 분석 목적 및 필요성
### 1.2 범위
- 분석 대상 및 기간

## 2. 분석 방법론
### 2.1 데이터 수집
- 수집 방법 및 출처
### 2.2 분석 기법
- 사용된 분석 도구 및 방법

## 3. 분석 결과
### 3.1 주요 발견사항
- 핵심 인사이트 1
- 핵심 인사이트 2
- 핵심 인사이트 3

### 3.2 데이터 분석
- 정량적 분석 결과
- 시각화 자료

## 4. 결론 및 권고사항
### 4.1 핵심 결론
- 주요 결론 요약
### 4.2 실행 권고안
- 단기 실행 과제
- 중장기 개선 방안

## 5. 부록
- 상세 데이터
- 참고 자료"""
                },
                {
                    "title": "경영진 요약",
                    "icon": "📋",
                    "content": f"""# 경영진 요약 보고서

## 🎯 핵심 메시지
{selected_text[:80]}...

## 📊 주요 지표
| 구분 | 현재 | 목표 | 차이 |
|------|------|------|------|
| 지표 1 | - | - | - |
| 지표 2 | - | - | - |
| 지표 3 | - | - | - |

## 💡 핵심 인사이트
1. **주요 발견사항 1**: 구체적 내용
2. **주요 발견사항 2**: 구체적 내용
3. **주요 발견사항 3**: 구체적 내용

## 🚀 권고 사항
### 즉시 실행 과제
- [ ] 우선순위 1순위 과제
- [ ] 우선순위 2순위 과제

### 중장기 전략
- 전략적 방향 1
- 전략적 방향 2

## ⚠️ 주의사항
- 리스크 요소 1
- 리스크 요소 2

## 📈 기대 효과
- 정량적 효과: 구체적 수치
- 정성적 효과: 예상 개선 사항"""
                }
            ]
        else:
            structures = [
                {
                    "title": "목차 형식",
                    "icon": "📚",
                    "content": f"""# 주제

## 1. 개요
{selected_text[:50]}...

## 2. 주요 내용
### 2.1 핵심 포인트 1
- 상세 내용 1-1
- 상세 내용 1-2

### 2.2 핵심 포인트 2  
- 상세 내용 2-1
- 상세 내용 2-2

### 2.3 핵심 포인트 3
- 상세 내용 3-1
- 상세 내용 3-2

## 3. 결론
- 요약 정리
- 향후 방향"""
                },
                {
                    "title": "단계별 가이드",
                    "icon": "📝",
                    "content": f"""# 단계별 실행 가이드

## 📋 시작하기 전에
{selected_text[:60]}...

## 1️⃣ 1단계: 준비
**목표**: 기본 준비 사항 완료
- 필요한 자료 준비
- 기본 환경 설정
- 관련자 협조 요청

## 2️⃣ 2단계: 실행
**목표**: 핵심 업무 수행
- 계획에 따른 순차 실행
- 중간 점검 및 조정
- 이슈 발생시 대응

## 3️⃣ 3단계: 검토
**목표**: 결과 확인 및 완성도 제고
- 결과물 품질 검토
- 미비점 보완
- 최종 확인

## ✅ 완료 체크리스트
- [ ] 모든 단계 완료 확인
- [ ] 결과물 최종 검토
- [ ] 관련자 승인 획득"""
                }
            ]
        
        cols = st.columns(2)
        for i, structure in enumerate(structures):
            with cols[i % 2]:
                with st.expander(f"{structure['icon']} {structure['title']} (데모)"):
                    st.markdown("**구조화된 내용:**")
                    st.markdown(structure['content'])
                    
                    if st.button(f"구조 적용", key=f"dummy_struct_{i}"):
                        insert_content_to_document(structure['content'])
                    
    # 저장된 템플릿 표시
    if hasattr(st.session_state, 'saved_templates') and st.session_state.saved_templates:
        st.markdown("---")
        st.markdown("### 💾 저장된 템플릿")
        
        template_names = list(st.session_state.saved_templates.keys())
        selected_template = st.selectbox("템플릿 선택:", ["선택하세요"] + template_names)
        
        if selected_template != "선택하세요":
            template_content = st.session_state.saved_templates[selected_template]
            with st.expander(f"📄 {selected_template} 미리보기"):
                st.markdown(template_content)
                if st.button(f"템플릿 적용", key="apply_saved_template"):
                    insert_content_to_document(f"\n\n{template_content}")
                    st.success("템플릿이 적용되었습니다!")

# 문서에 내용 삽입
def insert_content_to_document(content):
    # 현재 문서 내용에 삽입 (커서 위치는 더미로 처리)
    current_content = st.session_state.document_content
    
    # 삽입 위치 찾기 (실제로는 커서 위치)
    insert_position = len(current_content)  # 끝에 추가
    
    new_content = current_content + f"\n\n{content}"
    
    st.session_state.document_content = new_content
    
    # 삽입 완료 메시지
    st.success("✅ 내용이 문서에 삽입되었습니다!")
    time.sleep(0.5)

# AI 사이드바 패널
def render_ai_sidebar():
    if not st.session_state.ai_panel_open:
        return
    
    st.markdown("## 🤖 AI 전문 어시스턴트")
    st.markdown("---")
    
    # 사용자 타입 선택
    st.markdown("### 👤 사용자 타입 선택")
    user_type = st.radio(
        "어떤 업무를 주로 하시나요?",
        ["기획자 (Planner)", "보고서 작성자 (Reporter)", "일반 사용자 (General)"],
        key="user_type_selection",
        help="선택한 타입에 따라 AI가 맞춤형 분석과 추천을 제공합니다."
    )
    
    # 사용자 타입 매핑
    user_type_mapping = {
        "기획자 (Planner)": "planner",
        "보고서 작성자 (Reporter)": "reporter", 
        "일반 사용자 (General)": "general"
    }
    
    selected_user_type = user_type_mapping[user_type]
    st.session_state.current_user_type = selected_user_type
    
    # 타입별 설명
    type_descriptions = {
        "planner": "🎯 **기획자 모드**\n실행 가능한 계획, 액션 아이템, 리스크 분석에 특화된 AI 분석을 제공합니다.",
        "reporter": "📊 **보고서 작성자 모드**\n데이터 중심 분석, 논리적 구조, 시각화 제안에 특화된 AI 분석을 제공합니다.",
        "general": "📝 **일반 모드**\n종합적인 텍스트 분석과 개선 제안을 제공합니다."
    }
    
    st.info(type_descriptions[selected_user_type])
    
    st.markdown("---")
    
    # 검색 모드 선택
    st.markdown("### 🔍 분석 모드")
    search_mode = st.radio(
        "분석할 내용:",
        ["선택된 텍스트 기반", "전체 문서 기반"],
        key="search_mode",
        help="선택된 텍스트가 있으면 해당 텍스트를, 없으면 전체 문서를 분석합니다."
    )
    
    # 선택된 텍스트 표시
    if search_mode == "선택된 텍스트 기반" and st.session_state.selected_text:
        st.markdown("**📝 선택된 텍스트:**")
        text_preview = st.session_state.selected_text[:200] + "..." if len(st.session_state.selected_text) > 200 else st.session_state.selected_text
        st.markdown(f"""
        <div style="background-color: #f0f2f6; padding: 10px; border-radius: 5px; font-size: 12px;">
        {text_preview}
        </div>
        """, unsafe_allow_html=True)
        st.caption(f"총 {len(st.session_state.selected_text)}자")
    
    elif search_mode == "전체 문서 기반" and st.session_state.document_content:
        doc_preview = st.session_state.document_content[:150] + "..." if len(st.session_state.document_content) > 150 else st.session_state.document_content
        st.markdown("**📄 전체 문서 미리보기:**")
        st.markdown(f"""
        <div style="background-color: #f0f2f6; padding: 10px; border-radius: 5px; font-size: 12px;">
        {doc_preview}
        </div>
        """, unsafe_allow_html=True)
        st.caption(f"총 {len(st.session_state.document_content)}자")
    
    # AI 분석 시작 버튼
    st.markdown("---")
    
    # 텍스트가 있는지 확인
    analysis_text = ""
    if search_mode == "선택된 텍스트 기반":
        analysis_text = st.session_state.selected_text
    else:
        analysis_text = st.session_state.document_content
    
    if analysis_text and analysis_text.strip():
        if st.button("🚀 AI 전문 분석 시작", use_container_width=True, type="primary"):
            st.session_state.analysis_state = 'analyzing'
            st.session_state.analysis_text = analysis_text
            st.session_state.analysis_user_type = selected_user_type
            show_analysis_progress()
            st.session_state.analysis_state = 'completed'
            st.rerun()
    else:
        st.warning("분석할 텍스트가 없습니다. 문서를 작성하거나 텍스트를 선택해주세요.")
        st.button("🚀 AI 전문 분석 시작", use_container_width=True, disabled=True)
    
    # 분석 완료 후 결과 표시
    if st.session_state.analysis_state == 'completed':
        st.markdown("---")
        st.success("🎉 분석 완료!")
        
        tabs = st.tabs([
            "🎯 전문 분석", 
            "📚 자료 추천", 
            "✨ 문장 다듬기", 
            "🏗️ 구조화"
        ])
        
        with tabs[0]:
            # 전문 분석 결과 표시
            if hasattr(st.session_state, 'last_analysis') and st.session_state.last_analysis:
                show_professional_analysis(st.session_state.last_analysis)
            else:
                st.info("분석 결과가 없습니다. AI 분석을 다시 시작해주세요.")
        
        with tabs[1]:
            # 자료 추천
            search_query = st.session_state.get('analysis_text', '')
            user_type_for_search = st.session_state.get('analysis_user_type', 'general')
            show_recommendations(search_query, user_type_for_search)
        
        with tabs[2]:
            # 문장 다듬기
            if analysis_text:
                show_text_refinement(analysis_text, selected_user_type)
            else:
                st.info("다듬을 텍스트를 선택하거나 작성해주세요.")
        
        with tabs[3]:
            # 구조화
            if analysis_text:
                show_structuring(analysis_text, selected_user_type)
            else:
                st.info("구조화할 텍스트를 선택하거나 작성해주세요.")
    
    # 추가 도구들
    st.markdown("---")
    st.markdown("### 🛠️ 추가 도구")
    
    # 분석 기록 보기
    if st.button("📊 분석 기록", use_container_width=True):
        if hasattr(st.session_state, 'analysis_history') and st.session_state.analysis_history:
            st.markdown("**최근 분석 기록:**")
            for i, record in enumerate(st.session_state.analysis_history[-3:]):  # 최근 3개
                st.markdown(f"{i+1}. {record.get('timestamp', '')} - {record.get('user_type', '').upper()}")
        else:
            st.info("분석 기록이 없습니다.")
    
    # 설정 초기화
    if st.button("🔄 설정 초기화", use_container_width=True):
        st.session_state.analysis_state = 'idle'
        st.session_state.last_analysis = None
        if 'saved_templates' in st.session_state:
            del st.session_state.saved_templates
        st.success("설정이 초기화되었습니다!")
        time.sleep(1)
        st.rerun()
    
    # 도움말
    with st.expander("❓ 사용법 도움말"):
        st.markdown("""
        **AI 전문 어시스턴트 사용법:**
        
        1. **사용자 타입 선택**: 기획자/보고서 작성자/일반 중 선택
        2. **텍스트 선택**: 편집기에서 분석할 텍스트 입력 또는 선택
        3. **AI 분석 시작**: 맞춤형 전문 분석 실행
        4. **결과 활용**: 
           - 전문 분석: 핵심 인사이트와 권고사항
           - 자료 추천: 관련 전문 자료 검색
           - 문장 다듬기: 스타일별 텍스트 개선
           - 구조화: 문서 타입별 구조 변환
        
        **팁**: 사용자 타입에 따라 AI가 제공하는 분석과 추천이 달라집니다.
        """)
    
    st.markdown("---")
    st.caption("💡 Azure OpenAI 기반 전문 AI 어시스턴트")

# 문서 생성 인터페이스
def render_document_creation():
    """문서 생성 인터페이스 렌더링"""
    st.markdown("## 📝 AI 문서 작성 어시스턴트")
    st.markdown("---")
    
    # 상태 체크
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 새로운 문서를 시작하세요")
        st.markdown("텍스트 편집기에서 문서를 작성하고 AI 도구로 내용을 개선하세요.")
    
    with col2:
        st.markdown("#### 📊 문서 통계")
        if hasattr(st.session_state, 'document_content') and st.session_state.document_content:
            content = st.session_state.document_content.strip()
            if content:
                words = len(content.split())
                chars = len(content)
                lines = len(content.split('\n'))
                st.metric("단어 수", f"{words:,}")
                st.metric("문자 수", f"{chars:,}")
                st.metric("줄 수", f"{lines:,}")
            else:
                st.info("문서를 작성하면 통계가 표시됩니다.")
        else:
            st.info("문서를 작성하면 통계가 표시됩니다.")
    
    st.markdown("---")
    
    # 문서 생성 버튼들
    st.markdown("### 새 문서 생성")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 새 문서", key="create_text", use_container_width=True):
            doc_id = f"new_text_{int(time.time())}"
            st.session_state.current_document = {
                'id': doc_id,
                'type': 'text',
                'title': '새 문서'
            }
            st.session_state.document_content = ""
            st.session_state.current_view = "editor"
            st.rerun()
    
    with col2:
        if st.button("📋 템플릿 문서", key="create_template", use_container_width=True):
            doc_id = f"template_{int(time.time())}"
            st.session_state.current_document = {
                'id': doc_id,
                'type': 'template',
                'title': '템플릿 문서'
            }
            st.session_state.document_content = """# 제목

## 개요
이 문서의 목적과 개요를 작성하세요.

## 주요 내용

### 섹션 1
내용을 작성하세요.

### 섹션 2
내용을 작성하세요.

## 결론
결론을 작성하세요.
"""
            st.session_state.current_view = "editor"
            st.rerun()
    
    with col3:
        if st.button("📥 불러오기", key="load_document", use_container_width=True):
            st.session_state.show_file_upload = True
    
    # 파일 업로드 기능
    if getattr(st.session_state, 'show_file_upload', False):
        st.markdown("---")
        st.markdown("#### 📥 파일 불러오기")
        
        uploaded_file = st.file_uploader(
            "텍스트 파일을 선택하세요",
            type=['txt', 'md', 'py', 'js', 'html', 'css', 'json'],
            help="지원 형식: TXT, MD, PY, JS, HTML, CSS, JSON"
        )
        
        if uploaded_file is not None:
            try:
                content = uploaded_file.read().decode('utf-8')
                doc_id = f"uploaded_{int(time.time())}"
                st.session_state.current_document = {
                    'id': doc_id,
                    'type': 'uploaded',
                    'title': f'{uploaded_file.name}'
                }
                st.session_state.document_content = content
                st.session_state.current_view = "editor"
                st.session_state.show_file_upload = False
                st.success(f"✅ {uploaded_file.name} 파일이 로드되었습니다!")
                st.rerun()
            except Exception as e:
                st.error(f"파일 로드 중 오류: {str(e)}")
        
        if st.button("취소", key="cancel_upload"):
            st.session_state.show_file_upload = False
            st.rerun()

# 텍스트 편집기 렌더링
def render_document_editor():
    """텍스트 편집기 렌더링"""
    doc = st.session_state.current_document
    if not doc:
        st.error("문서 정보가 없습니다.")
        if st.button("← 문서 생성으로 돌아가기"):
            st.session_state.current_view = "create"
            st.rerun()
        return
    
    # 헤더
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"## {doc['title']}")
        st.caption(f"문서 ID: {doc['id']} | 타입: {doc['type'].upper()}")
    
    with col2:
        if st.button("🏠 새 문서 생성", use_container_width=True):
            st.session_state.current_view = "create"
            st.session_state.current_document = None
            st.rerun()
    
    with col3:
        if st.button("🤖 AI 패널 토글", use_container_width=True):
            st.session_state.ai_panel_open = not st.session_state.ai_panel_open
    
    st.markdown("---")
    
    # 툴바
    toolbar_col1, toolbar_col2, toolbar_col3, toolbar_col4, toolbar_col5 = st.columns(5)
    
    with toolbar_col1:
        if st.button("💾 저장", use_container_width=True):
            st.success("✅ 문서가 저장되었습니다!")
    
    with toolbar_col2:
        if st.button("📤 내보내기", use_container_width=True):
            # 문서 내용을 다운로드 링크로 제공
            if st.session_state.document_content:
                content = st.session_state.document_content
                st.download_button(
                    label="💾 TXT 다운로드",
                    data=content,
                    file_name=f"{doc['title']}.txt",
                    mime="text/plain"
                )
    
    with toolbar_col3:
        if st.button("📊 통계", use_container_width=True):
            if st.session_state.document_content:
                content = st.session_state.document_content
                words = len(content.split())
                chars = len(content)
                lines = len(content.split('\n'))
                st.info(f"📊 **문서 통계**\n- 단어: {words:,}개\n- 문자: {chars:,}개\n- 줄: {lines:,}개")
    
    with toolbar_col4:
        editor_height = st.selectbox("편집기 높이", [300, 400, 500, 600, 700, 800], index=3, key="editor_height")
    
    with toolbar_col5:
        font_size = st.selectbox("글꼴 크기", [12, 14, 16, 18, 20], index=1, key="font_size")
    
    # 텍스트 선택 시뮬레이션
    col1, col2 = st.columns([2, 1])
    
    
    with col1:
        # 메인 텍스트 편집기
        st.markdown("#### 📝 문서 편집")
        
        # CSS 스타일 적용
        st.markdown(f"""
        <style>
        .stTextArea textarea {{
            font-size: {font_size}px !important;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
        }}
        </style>
        """, unsafe_allow_html=True)
        
        # 문서 내용 편집
        document_content = st.text_area(
            "문서 내용:",
            value=st.session_state.get('document_content', ''),
            height=editor_height,
            key="main_document_editor",
            help="여기에 문서 내용을 작성하세요. AI 패널을 열어 도움을 받을 수 있습니다.",
            placeholder="여기에 문서 내용을 입력하세요..."
        )
        
        # 문서 내용 업데이트
        if document_content != st.session_state.get('document_content', ''):
            st.session_state.document_content = document_content

# 메인 애플리케이션
def main():
    # 세션 상태를 가장 먼저 초기화
    init_session_state()
    
    # CSS 로드
    load_css()
    
    # 뷰 선택에 따른 렌더링
    if st.session_state.current_view == "create":
        # 문서 생성 인터페이스
        render_document_creation()
        
    elif st.session_state.current_view == "editor":
        # 문서 편집기 인터페이스  
        if st.session_state.ai_panel_open:
            col1, col2 = st.columns([3, 1])
        else:
            col1, col2 = st.columns([1, 0.001])
        
        with col1:
            render_document_editor()
        
        # AI 사이드바
        with col2:
            if st.session_state.ai_panel_open:
                render_ai_sidebar()
                
                # 패널 닫기 버튼
                if st.button("❌ 패널 닫기", key="close_panel"):
                    st.session_state.ai_panel_open = False
                    st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()