"""请求追踪器"""
from typing import Dict, Optional
from .types import EventType, EventPriority


class RequestTracker:
    """请求追踪器"""
    
    def __init__(self):
        self._requests: Dict[str, Dict] = {}
    
    def add(self, request_id: str, event_type: EventType, priority: EventPriority, message: str) -> None:
        """添加请求"""
        self._requests[request_id] = {
            "event_type": event_type,
            "priority": priority,
            "message": message,
            "retry_count": 0
        }
    
    def get(self, request_id: str) -> Optional[Dict]:
        """获取请求信息"""
        return self._requests.get(request_id)
    
    def exists(self, request_id: str) -> bool:
        """检查请求是否存在"""
        return request_id in self._requests
    
    def increment_retry(self, request_id: str) -> int:
        """增加重试次数"""
        if request_id in self._requests:
            self._requests[request_id]["retry_count"] += 1
            return self._requests[request_id]["retry_count"]
        return 0
    
    def get_retry_count(self, request_id: str) -> int:
        """获取重试次数"""
        return self._requests.get(request_id, {}).get("retry_count", 0)
    
    def remove(self, request_id: str) -> None:
        """移除请求"""
        self._requests.pop(request_id, None)
    
    def clear(self) -> None:
        """清空所有请求"""
        self._requests.clear()
    
    def is_high_priority_processing(self, event_type: EventType) -> bool:
        """检查是否有高优先级事件正在处理"""
        return any(
            req["event_type"] == event_type and req["priority"] == EventPriority.HIGH
            for req in self._requests.values()
        )
    
    def __len__(self) -> int:
        return len(self._requests)
