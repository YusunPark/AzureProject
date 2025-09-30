"""
CSS 스타일 정의 및 로드 - 개선된 버전
"""
import streamlit as st
from core.constants import StyleConstants

def load_app_styles():
    """애플리케이션 CSS 스타일 로드"""
    st.markdown(_get_main_styles(), unsafe_allow_html=True)
    st.markdown(_get_component_styles(), unsafe_allow_html=True)
    st.markdown(_get_utility_styles(), unsafe_allow_html=True)

def _get_main_styles() -> str:
    """메인 레이아웃 스타일"""
    return f"""
    <style>
    /* 전체 배경 및 기본 색상 */
    .main {{
        background-color: {StyleConstants.BACKGROUND_COLOR};
    }}
    
    .block-container {{
        padding-top: 1rem;
        padding-bottom: 0rem;
    }}
    
    /* 사이드바 스타일 */
    .ai-sidebar {{
        background-color: #fafafa;
        border-left: 1px solid {StyleConstants.BORDER_COLOR};
        padding: {StyleConstants.CONTAINER_PADDING};
        height: 100vh;
        overflow-y: auto;
    }}
    
    /* AI 액센트 색상 */
    .ai-accent {{
        color: {StyleConstants.PRIMARY_COLOR};
        font-weight: 600;
    }}
    
    .ai-background {{
        background-color: #f3f4f6;
    }}
    </style>
    """

def _get_component_styles() -> str:
    """컴포넌트별 스타일"""
    return f"""
    <style>
    /* 버튼 스타일 */
    .stButton > button {{
        background-color: {StyleConstants.PRIMARY_COLOR};
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.2s ease;
    }}
    
    .stButton > button:hover {{
        background-color: {StyleConstants.PRIMARY_HOVER};
        transform: translateY(-1px);
    }}
    
    /* 네비게이션 카드 */
    .nav-card {{
        background: {StyleConstants.GRADIENT_PURPLE};
        border-radius: 12px;
        padding: {StyleConstants.CONTAINER_PADDING};
        color: white;
        text-align: center;
        margin: {StyleConstants.SECTION_MARGIN};
        cursor: pointer;
        transition: transform 0.2s;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }}
    
    .nav-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }}
    
    .nav-card h3 {{
        margin: 0;
        font-size: 1.2rem;
    }}
    
    .nav-card p {{
        margin: 5px 0 0 0;
        opacity: 0.9;
        font-size: 0.9rem;
    }}
    
    /* 문서 카드 */
    .doc-card {{
        background: white;
        border: 1px solid {StyleConstants.BORDER_COLOR};
        border-radius: 8px;
        padding: {StyleConstants.CARD_PADDING};
        margin: {StyleConstants.SECTION_MARGIN};
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        transition: all 0.2s ease;
    }}
    
    .doc-card:hover {{
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        transform: translateY(-1px);
    }}
    
    .doc-title {{
        font-weight: 600;
        color: #1f2937;
        margin-bottom: 8px;
    }}
    
    .doc-summary {{
        color: #6b7280;
        font-size: 14px;
        margin-bottom: 8px;
    }}
    
    .doc-source {{
        color: {StyleConstants.PRIMARY_COLOR};
        font-size: 12px;
        font-style: italic;
    }}
    </style>
    """

def _get_utility_styles() -> str:
    """유틸리티 스타일"""
    return f"""
    <style>
    /* 상태 표시 */
    .status-card {{
        background: {StyleConstants.CARD_BACKGROUND};
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: {StyleConstants.CARD_PADDING};
        margin: {StyleConstants.SECTION_MARGIN};
    }}
    
    .status-good {{ 
        border-left: 4px solid {StyleConstants.SUCCESS_COLOR}; 
    }}
    .status-warning {{ 
        border-left: 4px solid {StyleConstants.WARNING_COLOR}; 
    }}
    .status-error {{ 
        border-left: 4px solid {StyleConstants.ERROR_COLOR}; 
    }}
    
    /* 편집기 스타일 */
    .stTextArea textarea {{
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1.6;
        border-radius: 8px;
        border: 1px solid {StyleConstants.BORDER_COLOR};
    }}
    
    /* 통계 카드 스타일 */
    .metric-card {{
        background: {StyleConstants.CARD_BACKGROUND};
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 12px;
        margin: 4px 0;
        text-align: center;
    }}
    
    .metric-value {{
        font-size: 1.5rem;
        font-weight: bold;
        color: {StyleConstants.PRIMARY_COLOR};
    }}
    
    .metric-label {{
        font-size: 0.8rem;
        color: #6c757d;
        margin-top: 4px;
    }}
    
    /* 진행 표시 */
    .progress-container {{
        background: {StyleConstants.CARD_BACKGROUND};
        border-radius: 8px;
        padding: {StyleConstants.CARD_PADDING};
        margin: {StyleConstants.SECTION_MARGIN};
    }}
    
    /* 알림 스타일 */
    .notification {{
        padding: 12px 16px;
        border-radius: 6px;
        margin: 8px 0;
        border-left: 4px solid;
    }}
    
    .notification-success {{
        background-color: #d4edda;
        border-color: {StyleConstants.SUCCESS_COLOR};
        color: #155724;
    }}
    
    .notification-warning {{
        background-color: #fff3cd;
        border-color: {StyleConstants.WARNING_COLOR};
        color: #856404;
    }}
    
    .notification-error {{
        background-color: #f8d7da;
        border-color: {StyleConstants.ERROR_COLOR};
        color: #721c24;
    }}
    </style>
    """

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

def apply_custom_theme():
    """사용자 정의 테마 적용"""
    st.markdown("""
    <style>
    /* 다크 테마 지원 */
    @media (prefers-color-scheme: dark) {
        .main {
            background-color: #1e1e1e;
            color: #ffffff;
        }
        
        .status-card {
            background: #2d2d2d;
            border-color: #404040;
            color: #ffffff;
        }
        
        .doc-card {
            background: #2d2d2d;
            border-color: #404040;
            color: #ffffff;
        }
    }
    
    /* 반응형 디자인 */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        
        .nav-card {
            padding: 15px;
        }
        
        .doc-card {
            padding: 12px;
        }
    }
    </style>
    """, unsafe_allow_html=True)