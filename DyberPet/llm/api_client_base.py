"""LLM API客户端基类"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class BaseAPIClient(ABC):
    """API客户端抽象基类"""
    
    def __init__(self, api_key: Optional[str] = None, debug_mode: bool = False):
        self.api_key = api_key
        self.debug_mode = debug_mode
    
    @abstractmethod
    def call_api(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        调用API
        
        Args:
            messages: 消息列表
            **kwargs: 其他参数（temperature, max_tokens等）
            
        Returns:
            标准化的响应字典
        """
        pass
    
    @abstractmethod
    def validate_config(self) -> tuple[bool, Optional[str]]:
        """
        验证配置
        
        Returns:
            (是否有效, 错误消息)
        """
        pass
    
    def format_response(self, raw_response: Any) -> Dict[str, Any]:
        """
        格式化响应为统一格式
        
        Returns:
            {
                "choices": [...],
                "model": "...",
                "usage": {...}
            }
        """
        return raw_response
