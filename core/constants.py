"""
애플리케이션 상수 정의
"""

# UI 관련 상수
class UIConstants:
    """UI 관련 상수 클래스"""
    
    # 페이지 뷰 타입
    VIEW_HOME = "home"
    VIEW_TRAINING_UPLOAD = "training_upload"
    VIEW_DOCUMENT_CREATE = "document_create"
    VIEW_AI_ANALYSIS = "ai_analysis"
    VIEW_DOCUMENT_MANAGE = "document_manage"
    VIEW_CREATE = "create"
    VIEW_EDITOR = "editor"
    
    # 분석 상태
    ANALYSIS_IDLE = "idle"
    ANALYSIS_ANALYZING = "analyzing"
    ANALYSIS_COMPLETED = "completed"
    ANALYSIS_ERROR = "error"
    
    # 검색 모드
    SEARCH_MODE_FULL = "전체 문서 기반"
    SEARCH_MODE_SELECTED = "선택된 텍스트 기반"
    
    # 편집기 설정
    DEFAULT_EDITOR_HEIGHT = 400
    DEFAULT_FONT_SIZE = 14
    EDITOR_HEIGHTS = [300, 400, 500, 600, 700, 800]
    FONT_SIZES = [12, 14, 16, 18, 20]
    
    # 컬럼 레이아웃
    LAYOUT_MAIN_SIDEBAR = [2, 1]
    LAYOUT_THREE_EQUAL = [1, 1, 1]
    LAYOUT_EDITOR_AI = [3, 1]

class MessageConstants:
    """메시지 관련 상수 클래스"""
    
    # 성공 메시지
    SUCCESS_DOCUMENT_SAVED = "✅ 문서가 성공적으로 저장되었습니다!"
    SUCCESS_ANALYSIS_COMPLETED = "✅ AI 분석이 완료되었습니다!"
    SUCCESS_UPLOAD_COMPLETED = "✅ 문서 업로드가 완료되었습니다!"
    
    # 오류 메시지
    ERROR_NO_CONTENT = "❌ 분석할 내용이 없습니다."
    ERROR_SAVE_FAILED = "❌ 문서 저장에 실패했습니다."
    ERROR_UPLOAD_FAILED = "❌ 문서 업로드에 실패했습니다."
    ERROR_CONNECTION_FAILED = "❌ 서비스 연결에 실패했습니다."
    
    # 경고 메시지
    WARNING_NO_CONTENT = "⚠️ 내용이 없습니다."
    WARNING_SERVICE_UNAVAILABLE = "⚠️ 서비스를 사용할 수 없습니다."
    
    # 정보 메시지
    INFO_LOADING = "📥 로딩 중..."
    INFO_PROCESSING = "🔄 처리 중..."
    INFO_NO_DOCUMENTS = "📝 아직 문서가 없습니다."

class StyleConstants:
    """스타일 관련 상수 클래스"""
    
    # 색상 팔레트
    PRIMARY_COLOR = "#8b5cf6"
    PRIMARY_HOVER = "#7c3aed"
    SUCCESS_COLOR = "#28a745"
    WARNING_COLOR = "#ffc107"
    ERROR_COLOR = "#dc3545"
    INFO_COLOR = "#17a2b8"
    BACKGROUND_COLOR = "#ffffff"
    CARD_BACKGROUND = "#f8f9fa"
    BORDER_COLOR = "#e5e7eb"
    
    # 공간 설정
    CARD_PADDING = "15px"
    SECTION_MARGIN = "10px 0"
    CONTAINER_PADDING = "20px"
    
    # 그라데이션
    GRADIENT_PURPLE = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
    GRADIENT_BLUE = "linear-gradient(135deg, #74b9ff 0%, #0984e3 100%)"
    
class ConfigConstants:
    """설정 관련 상수 클래스"""
    
    # 파일 관련
    MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
    SUPPORTED_FILE_TYPES = [".docx", ".pdf", ".txt", ".md", ".py", ".js", ".html", ".css", ".json", ".csv"]
    
    # 성능 관련
    CACHE_TTL = 300  # 5분
    MAX_SEARCH_RESULTS = 20
    MAX_CONTENT_LENGTH = 50000
    
    # AI 관련
    MAX_TOKENS = 1000
    DEFAULT_TEMPERATURE = 0.7
    ANALYSIS_TIMEOUT = 30  # 30초
    
    # 페이지네이션
    ITEMS_PER_PAGE = 10
    MAX_PREVIEW_LENGTH = 200

class EndpointConstants:
    """API 엔드포인트 상수 클래스"""
    
    # Azure 서비스 API 버전
    SEARCH_API_VERSION = "2019-05-06"
    STORAGE_API_VERSION = "2020-04-08"
    OPENAI_API_VERSION = "2024-12-01-preview"
    
    # 인덱스 이름
    SEARCH_INDEX_NAME = "company-documents"
    GENERATED_DOCS_CONTAINER = "generated-documents"
    TRAINING_DOCS_CONTAINER = "training-documents"