"""事件队列管理器"""
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
from .types import EventType, EventPriority, StandardEvent


class EventQueue:
    """事件队列管理器"""
    
    def __init__(self, priority_threshold: int = 4):
        self.priority_threshold = priority_threshold
        self._queues: Dict[Tuple[EventType, bool], List[StandardEvent]] = defaultdict(list)
    
    def add(self, event: StandardEvent, is_high_priority: bool = False) -> None:
        """添加事件到队列"""
        key = (event["event_type"], is_high_priority)
        self._queues[key].append(event)
    
    def get(self, event_type: EventType, is_high_priority: bool = False) -> List[StandardEvent]:
        """获取指定类型的事件列表"""
        key = (event_type, is_high_priority)
        return self._queues.get(key, [])
    
    def pop(self, event_type: EventType, is_high_priority: bool = False) -> List[StandardEvent]:
        """弹出并清空指定类型的事件"""
        key = (event_type, is_high_priority)
        events = self._queues.get(key, [])
        self._queues[key] = []
        return events
    
    def clear(self, event_type: Optional[EventType] = None) -> None:
        """清空队列"""
        if event_type:
            self._queues = {k: v for k, v in self._queues.items() if k[0] != event_type}
        else:
            self._queues.clear()
    
    def should_process(self, event_type: EventType) -> bool:
        """检查是否应该处理该类型事件"""
        events = self.get(event_type, is_high_priority=False)
        if not events:
            return False
        accumulated_priority = sum(e["priority"].value for e in events)
        return accumulated_priority >= self.priority_threshold
    
    def __len__(self) -> int:
        return sum(len(events) for events in self._queues.values())
