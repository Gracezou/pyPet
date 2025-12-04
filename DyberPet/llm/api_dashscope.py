"""通义千问API客户端"""
from typing import Dict, Any, List, Optional
from .api_client_base import BaseAPIClient

try:
    import dashscope
    DASHSCOPE_AVAILABLE = True
except ImportError:
    DASHSCOPE_AVAILABLE = False


class DashscopeClient(BaseAPIClient):
    """通义千问API客户端"""
    
    def validate_config(self) -> tuple[bool, Optional[str]]:
        """验证配置"""
        if not DASHSCOPE_AVAILABLE:
            return False, "E004"
        if not self.api_key:
            return False, "E005"
        return True, None
    
    def call_api(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """调用通义千问API"""
        model = kwargs.get('model', 'qwen-plus')
        if model == "local-model":
            model = "qwen-max"
        
        if self.debug_mode:
            print(f"\n===== 通义千问API请求 =====")
            print(f"模型: {model}")
            print(f"消息数: {len(messages)}")
        
        response = dashscope.Generation.call(
            api_key=self.api_key,
            model=model,
            messages=messages,
            result_format='message',
            temperature=kwargs.get('temperature', 0.8),
            max_tokens=kwargs.get('max_tokens', 600),
        )
        
        if response.status_code != 200:
            raise Exception(f"API错误: {response.status_code} - {response.message}")
        
        return self.format_response(response)
    
    def format_response(self, raw_response: Any) -> Dict[str, Any]:
        """格式化响应"""
        return {
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": raw_response.output.choices[0].message.content
                },
                "finish_reason": "stop"
            }],
            "model": raw_response.request_id,
            "usage": {
                "prompt_tokens": raw_response.usage.input_tokens,
                "completion_tokens": raw_response.usage.output_tokens,
                "total_tokens": raw_response.usage.input_tokens + raw_response.usage.output_tokens
            }
        }
