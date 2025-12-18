"""LLM模块常量定义"""
from typing import Dict

# 错误码定义
ERROR_CODES = {
    "E001": "internal",
    "E002": "network",
    "E003": "network",
    "E004": "config",
    "E005": "config",
    "E006": "api",
    "E007": "api",
    "E008": "format",
    "E009": "internal",
    "E010": "config",
    "E011": "internal",
    "E999": "unknown",
}

# 错误消息 (多语言支持)
ERROR_MESSAGES: Dict[str, Dict[str, str]] = {
    "zh_CN": {
        "E001": "程序内部线程错误",
        "E002": "大模型请求失败，状态码异常",
        "E003": "HTTP请求异常",
        "E004": "未安装dashscope库，无法使用通义千问API",
        "E005": "未设置通义千问API密钥",
        "E006": "通义千问API请求失败",
        "E007": "通义千问API异常",
        "E008": "大模型回复格式错误，无法解析JSON",
        "E009": "大模型回复处理异常",
        "E010": "大模型功能未启用",
        "E011": "重试发送失败",
        "E999": "未知错误",
    },
    "en_US": {
        "E001": "Internal thread error",
        "E002": "LLM request failed with abnormal status code",
        "E003": "HTTP request exception",
        "E004": "dashscope library not installed",
        "E005": "API key not configured",
        "E006": "Qwen API request failed",
        "E007": "Qwen API exception",
        "E008": "Invalid JSON format in LLM response",
        "E009": "LLM response processing error",
        "E010": "LLM feature not enabled",
        "E011": "Retry failed",
        "E999": "Unknown error",
    }
}

# LLM配置默认值
LLM_CONFIG_DEFAULTS = {
    "enabled": False,
    "model_type": "Qwen",
    "api_key": None,
    "debug_mode": False,
    "timeout": 10,
    "max_retries": 3,
    "retry_delay": 1,
    "temperature": 0.8,
    "max_tokens": 600,
    "default_system_prompt": "你是一个智能的桌面伴侣，需要根据用户交互和系统事件做出简短友好的回应。"
}

# 请求管理器配置
REQUEST_MANAGER_CONFIG = {
    "priority_threshold": 4,
    "high_priority_throttle_window": 2.0,  # 秒
    "max_conversation_history": 10,  # 最大对话历史条数
}

# 情绪映射
EMOTION_ICON_MAP = {
    "高兴": "bb_fv_lvlup",
    "难过": "bb_fv_drop",
    "可爱": "bb_hp_low",
    "天使": "bb_hp_zero",
    "正常": "bb_pat_focus",
    "困惑": "bb_pat_frequent",
}
