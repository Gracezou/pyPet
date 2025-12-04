"""LLM配置管理器"""
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from .constants import LLM_CONFIG_DEFAULTS


@dataclass
class LLMConfig:
    """LLM配置数据类"""
    enabled: bool = False
    model_type: str = "Qwen"
    api_key: Optional[str] = None
    api_url: str = "http://localhost:8000/v1/chat/completions"
    remote_api_url: str = "https://api.example.com/v1/chat/completions"
    debug_mode: bool = False
    timeout: int = 10
    max_retries: int = 3
    retry_delay: int = 1
    temperature: float = 0.8
    max_tokens: int = 600
    max_conversation_history: int = 10
    
    @property
    def api_type(self) -> str:
        """根据model_type自动推断api_type"""
        return "dashscope" if self.model_type == "Qwen" else "local"
    
    def validate(self) -> Tuple[bool, Optional[str]]:
        """验证配置"""
        if self.enabled and not self.api_key:
            return False, "API密钥未设置"
        if self.temperature < 0 or self.temperature > 2:
            return False, "temperature必须在0-2之间"
        if self.max_tokens < 1 or self.max_tokens > 4000:
            return False, "max_tokens必须在1-4000之间"
        if self.max_retries < 0 or self.max_retries > 10:
            return False, "max_retries必须在0-10之间"
        return True, None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "enabled": self.enabled,
            "model_type": self.model_type,
            "api_key": self.api_key,
            "api_url": self.api_url,
            "remote_api_url": self.remote_api_url,
            "debug_mode": self.debug_mode,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LLMConfig':
        """从字典创建"""
        config_data = LLM_CONFIG_DEFAULTS.copy()
        config_data.update(data)
        return cls(
            enabled=config_data.get("enabled", False),
            model_type=config_data.get("model_type", "Qwen"),
            api_key=config_data.get("api_key"),
            api_url=config_data.get("api_url", "http://localhost:8000/v1/chat/completions"),
            remote_api_url=config_data.get("remote_api_url", "https://api.example.com/v1/chat/completions"),
            debug_mode=config_data.get("debug_mode", False),
            timeout=config_data.get("timeout", 10),
            max_retries=config_data.get("max_retries", 3),
            retry_delay=config_data.get("retry_delay", 1),
            temperature=config_data.get("temperature", 0.8),
            max_tokens=config_data.get("max_tokens", 600),
            max_conversation_history=config_data.get("max_conversation_history", 10),
        )


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, settings_module=None):
        self.settings = settings_module
        self._config: Optional[LLMConfig] = None
        self._load()
    
    def _load(self) -> None:
        """加载配置"""
        if self.settings and hasattr(self.settings, 'llm_config'):
            self._config = LLMConfig.from_dict(self.settings.llm_config)
        else:
            self._config = LLMConfig.from_dict(LLM_CONFIG_DEFAULTS)
    
    def get(self) -> LLMConfig:
        """获取配置"""
        if not self._config:
            self._load()
        return self._config
    
    def update(self, **kwargs) -> Tuple[bool, Optional[str]]:
        """更新配置"""
        if not self._config:
            self._load()
        
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
        
        is_valid, error = self._config.validate()
        if not is_valid:
            return False, error
        
        if self.settings:
            self.settings.llm_config.update(kwargs)
            if hasattr(self.settings, 'save_settings'):
                self.settings.save_settings()
        
        return True, None
    
    def reload(self) -> None:
        """重新加载配置"""
        self._load()
    
    def reset(self) -> None:
        """重置为默认配置"""
        self._config = LLMConfig.from_dict(LLM_CONFIG_DEFAULTS)
