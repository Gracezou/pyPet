"""HTTP API客户端（本地/远程）"""
from typing import Dict, Any, List, Optional
import requests
from .api_client_base import BaseAPIClient


class HTTPAPIClient(BaseAPIClient):
    """HTTP API客户端"""
    
    def __init__(self, api_url: str, api_key: Optional[str] = None, debug_mode: bool = False):
        super().__init__(api_key, debug_mode)
        self.api_url = api_url
    
    def validate_config(self) -> tuple[bool, Optional[str]]:
        """验证配置"""
        if not self.api_url:
            return False, "E003"
        return True, None
    
    def call_api(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """调用HTTP API"""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        request_data = {
            "model": kwargs.get('model', 'local-model'),
            "messages": messages,
            "temperature": kwargs.get('temperature', 0.8),
            "max_tokens": kwargs.get('max_tokens', 600)
        }
        
        if self.debug_mode:
            print(f"\n===== HTTP API请求 =====")
            print(f"URL: {self.api_url}")
            print(f"消息数: {len(messages)}")
        
        response = requests.post(
            self.api_url,
            headers=headers,
            json=request_data,
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"HTTP错误: {response.status_code} - {response.text}")
        
        return response.json()
