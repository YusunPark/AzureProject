"""
예외 처리 클래스들
"""

class BaseAppException(Exception):
    """애플리케이션 기본 예외 클래스"""
    
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class ServiceConnectionException(BaseAppException):
    """서비스 연결 예외"""
    
    def __init__(self, service_name: str, details: str = None):
        message = f"{service_name} 서비스 연결 실패"
        if details:
            message += f": {details}"
        super().__init__(message, "SERVICE_CONNECTION_ERROR")

class DocumentProcessingException(BaseAppException):
    """문서 처리 예외"""
    
    def __init__(self, operation: str, details: str = None):
        message = f"문서 {operation} 처리 실패"
        if details:
            message += f": {details}"
        super().__init__(message, "DOCUMENT_PROCESSING_ERROR")

class AIAnalysisException(BaseAppException):
    """AI 분석 예외"""
    
    def __init__(self, stage: str, details: str = None):
        message = f"AI 분석 {stage} 단계 실패"
        if details:
            message += f": {details}"
        super().__init__(message, "AI_ANALYSIS_ERROR")

class ValidationException(BaseAppException):
    """데이터 검증 예외"""
    
    def __init__(self, field: str, details: str = None):
        message = f"{field} 검증 실패"
        if details:
            message += f": {details}"
        super().__init__(message, "VALIDATION_ERROR")

class ConfigurationException(BaseAppException):
    """설정 오류 예외"""
    
    def __init__(self, config_key: str, details: str = None):
        message = f"설정 오류: {config_key}"
        if details:
            message += f" - {details}"
        super().__init__(message, "CONFIGURATION_ERROR")

def handle_exception(e: Exception, context: str = "작업") -> str:
    """통일된 예외 처리 함수"""
    if isinstance(e, BaseAppException):
        return f"❌ {e.message}"
    elif "timeout" in str(e).lower():
        return f"⏰ {context} 시간 초과: 네트워크 상태를 확인해주세요"
    elif "permission" in str(e).lower() or "unauthorized" in str(e).lower():
        return f"🔐 {context} 권한 오류: 인증 정보를 확인해주세요"
    elif "network" in str(e).lower() or "connection" in str(e).lower():
        return f"🌐 {context} 네트워크 오류: 인터넷 연결을 확인해주세요"
    else:
        return f"❌ {context} 중 오류가 발생했습니다: {str(e)}"