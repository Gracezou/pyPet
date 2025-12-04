"""LLM模块类型定义"""
from typing import TypedDict, Literal, Optional, List, Dict, Any
from enum import Enum


class EventPriority(Enum):
    """事件优先级"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class EventType(Enum):
    """事件类型"""
    USER_INTERACTION = "用户交互"
    STATUS_CHANGE = "状态变化"
    TIME_TRIGGER = "时间触发"
    RANDOM_EVENT = "随机触发"
    ENVIRONMENT = "环境感知"


class PetStatus(TypedDict):
    """宠物状态"""
    pet_name: str
    hp: str
    fv: str
    hp_tier: int
    fv_lvl: int
    time: str


class StandardEvent(TypedDict):
    """标准事件数据结构"""
    event_id: str
    event_type: EventType
    priority: EventPriority
    timestamp: float
    pet_status: PetStatus
    context: Dict[str, Any]


class LLMResponse(TypedDict, total=False):
    """LLM响应结构"""
    text: str
    emotion: Literal["高兴", "难过", "困惑", "可爱", "正常", "天使"]
    action: List[str]
    open_web: Optional[str]
    add_task: Optional[str]
    adaptive_timing_decision: Optional[bool]
    recommended_interval: Optional[int]
    recommended_idle_threshold: Optional[int]


ErrorType = Literal["internal", "network", "config", "api", "format", "unknown"]
