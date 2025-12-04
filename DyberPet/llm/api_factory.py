"""API客户端工厂"""
from typing import Optional
from .api_client_base import BaseAPIClient
from .api_dashscope import DashscopeClient
from .api_http import HTTPAPIClient


class APIClientFactory:
    """API客户端工厂类"""
    
    @staticmethod
    def create(
        api_type: str,
        api_key: Optional[str] = None,
        api_url: Optional[str] = None,
        debug_mode: bool = False
    ) -> BaseAPIClient:
        """
        创建API客户端
        
        Args:
            api_type: API类型 ("dashscope", "local", "remote")
            api_key: API密钥
            api_url: API地址（HTTP类型需要）
            debug_mode: 调试模式
            
        Returns:
            API客户端实例
        """
        if api_type == "dashscope":
            return DashscopeClient(api_key=api_key, debug_mode=debug_mode)
        elif api_type in ["local", "remote"]:
            if not api_url:
                raise ValueError(f"HTTP API需要提供api_url")
            return HTTPAPIClient(api_url=api_url, api_key=api_key, debug_mode=debug_mode)
        else:
            raise ValueError(f"不支持的API类型: {api_type}")
