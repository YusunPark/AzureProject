"""
CSS 스타일 관리 - 애플리케이션 전체 스타일 정의
"""
import streamlit as st

def load_app_styles():
    """애플리케이션 CSS 스타일 로드"""
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
    
    /* 진행 상태 스타일 */
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
    </style>
    """, unsafe_allow_html=True)

def apply_editor_font_style(font_size: int):
    """편집기 폰트 스타일 적용"""
    st.markdown(f"""
    <style>
    .stTextArea textarea {{
        font-size: {font_size}px !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1.6;
    }}
    </style>
    """, unsafe_allow_html=True)