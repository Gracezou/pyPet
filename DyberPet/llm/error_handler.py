"""LLM错误处理器"""
from typing import Dict, Optional, Tuple
from .constants import ERROR_CODES, ERROR_MESSAGES
from .types import ErrorType


class ErrorHandler:
    """统一错误处理"""
    
    def __init__(self, language: str = "zh_CN"):
        self.language = language
        self._messages = ERROR_MESSAGES.get(language, ERROR_MESSAGES["zh_CN"])
    
    def get_error_info(self, error: Dict[str, str]) -> Tuple[str, str, ErrorType]:
        """
        获取错误信息
        
        Args:
            error: 错误字典 {"code": "E001", "details": "..."}
            
        Returns:
            (错误消息, 详细信息, 错误类型)
        """
        code = error.get("code", "E999")
        if code not in self._messages:
            code = "E999"
        
        message = self._messages[code]
        details = error.get("details", "")
        error_type = ERROR_CODES.get(code, "unknown")
        
        return message, details, error_type
    
    def format_error(self, error: Dict[str, str]) -> str:
        """格式化错误消息用于显示"""
        message, details, _ = self.get_error_info(error)
        if details:
            return f"{message}\n详情: {details}"
        return message
    
    def set_language(self, language: str) -> None:
        """切换语言"""
        self._messages = ERROR_MESSAGES.get(language, ERROR_MESSAGES["zh_CN"])
