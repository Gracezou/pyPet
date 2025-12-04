"""节流管理器"""
import time
from typing import Dict, Tuple, Optional, Callable
from PySide6.QtCore import QTimer
from .types import EventType


class ThrottleManager:
    """节流管理器"""
    
    def __init__(self, throttle_window: float = 2.0):
        self.throttle_window = throttle_window
        self._timers: Dict[Tuple[EventType, bool], QTimer] = {}
        self._deadlines: Dict[Tuple[EventType, bool], float] = {}
    
    def should_throttle(self, event_type: EventType, is_high_priority: bool = True) -> bool:
        """检查是否应该节流"""
        key = (event_type, is_high_priority)
        deadline = self._deadlines.get(key)
        if deadline and time.time() <= deadline:
            return True
        return False
    
    def set_deadline(self, event_type: EventType, is_high_priority: bool = True) -> None:
        """设置节流截止时间"""
        key = (event_type, is_high_priority)
        self._deadlines[key] = time.time() + self.throttle_window
    
    def start_timer(self, event_type: EventType, is_high_priority: bool, callback: Callable, parent=None) -> None:
        """启动节流定时器"""
        key = (event_type, is_high_priority)
        self.stop_timer(event_type, is_high_priority)
        
        timer = QTimer(parent)
        timer.setSingleShot(True)
        timer.timeout.connect(callback)
        timer.start(int(self.throttle_window * 1000))
        self._timers[key] = timer
    
    def restart_timer(self, event_type: EventType, is_high_priority: bool) -> None:
        """重启定时器"""
        key = (event_type, is_high_priority)
        timer = self._timers.get(key)
        if timer and timer.isActive():
            timer.stop()
            timer.start(int(self.throttle_window * 1000))
    
    def stop_timer(self, event_type: EventType, is_high_priority: bool) -> None:
        """停止定时器"""
        key = (event_type, is_high_priority)
        timer = self._timers.pop(key, None)
        if timer and timer.isActive():
            timer.stop()
    
    def stop_all(self) -> None:
        """停止所有定时器"""
        for timer in self._timers.values():
            if timer.isActive():
                timer.stop()
        self._timers.clear()
        self._deadlines.clear()
