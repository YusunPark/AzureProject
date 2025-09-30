"""
공통 유틸리티 함수들
"""
import time
import hashlib
import re
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
import streamlit as st
from core.constants import MessageConstants, ConfigConstants

def show_message(message_type: str, message: str, key: Optional[str] = None):
    """통일된 메시지 표시 함수"""
    if message_type == "success":
        st.success(message, icon="✅")
    elif message_type == "error":
        st.error(message, icon="❌")
    elif message_type == "warning":
        st.warning(message, icon="⚠️")
    elif message_type == "info":
        st.info(message, icon="ℹ️")
    else:
        st.write(message)

def validate_content(content: str, min_length: int = 1) -> bool:
    """콘텐츠 유효성 검증"""
    return content and len(content.strip()) >= min_length

def sanitize_filename(filename: str) -> str:
    """파일명 정리"""
    # 특수문자 제거 및 공백을 언더스코어로 변경
    cleaned = re.sub(r'[^\w\s-.]', '', filename)
    cleaned = re.sub(r'[-\s]+', '_', cleaned)
    return cleaned

def generate_document_id(content: str, timestamp: Optional[datetime] = None) -> str:
    """문서 ID 생성"""
    if timestamp is None:
        timestamp = datetime.now()
    
    # 콘텐츠 해시와 타임스탬프를 조합
    content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
    time_str = timestamp.strftime("%Y%m%d_%H%M%S")
    return f"doc_{time_str}_{content_hash}"

def format_file_size(size_bytes: int) -> str:
    """파일 크기 포맷팅"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    size = size_bytes
    
    while size >= 1024 and i < len(size_names) - 1:
        size /= 1024
        i += 1
    
    return f"{size:.1f} {size_names[i]}"

def format_datetime(dt: Union[datetime, str], format_type: str = "default") -> str:
    """날짜시간 포맷팅"""
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
        except:
            return dt
    
    if format_type == "short":
        return dt.strftime("%m/%d %H:%M")
    elif format_type == "date":
        return dt.strftime("%Y-%m-%d")
    elif format_type == "time":
        return dt.strftime("%H:%M:%S")
    else:  # default
        return dt.strftime("%Y-%m-%d %H:%M:%S")

def truncate_text(text: str, max_length: int = ConfigConstants.MAX_PREVIEW_LENGTH) -> str:
    """텍스트 자르기"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."

def calculate_reading_time(text: str, words_per_minute: int = 200) -> int:
    """읽기 시간 계산 (분)"""
    word_count = len(text.split())
    return max(1, round(word_count / words_per_minute))

def get_text_stats(text: str) -> Dict[str, int]:
    """텍스트 통계 계산"""
    if not text:
        return {"words": 0, "chars": 0, "lines": 0, "paragraphs": 0}
    
    words = len(text.split())
    chars = len(text)
    lines = len(text.split('\n'))
    paragraphs = len([p for p in text.split('\n\n') if p.strip()])
    
    return {
        "words": words,
        "chars": chars,
        "lines": lines,
        "paragraphs": paragraphs
    }

def create_progress_tracker(total_steps: int):
    """진행 상황 추적기 생성"""
    return {
        "current_step": 0,
        "total_steps": total_steps,
        "progress_bar": st.progress(0),
        "status_text": st.empty()
    }

def update_progress(tracker: Dict, step: int, message: str):
    """진행 상황 업데이트"""
    progress = step / tracker["total_steps"]
    tracker["progress_bar"].progress(progress)
    tracker["status_text"].text(message)
    tracker["current_step"] = step

def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """안전한 JSON 파싱"""
    try:
        return json.loads(json_str) if json_str else default
    except:
        return default

def debounce_function(func, delay: float = 0.5):
    """함수 디바운싱"""
    last_called = [0]
    
    def wrapper(*args, **kwargs):
        now = time.time()
        if now - last_called[0] >= delay:
            last_called[0] = now
            return func(*args, **kwargs)
    
    return wrapper

def batch_process(items: List[Any], batch_size: int = 10, progress_callback=None):
    """배치 처리"""
    results = []
    total = len(items)
    
    for i in range(0, total, batch_size):
        batch = items[i:i + batch_size]
        batch_results = []
        
        for item in batch:
            # 여기서 실제 처리 로직 수행
            batch_results.append(item)
        
        results.extend(batch_results)
        
        if progress_callback:
            progress_callback(min(i + batch_size, total), total)
    
    return results

class TimerContext:
    """시간 측정 컨텍스트 매니저"""
    
    def __init__(self, description: str = "Operation"):
        self.description = description
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        elapsed = self.end_time - self.start_time
        print(f"{self.description} completed in {elapsed:.2f} seconds")
    
    @property
    def elapsed(self) -> float:
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0