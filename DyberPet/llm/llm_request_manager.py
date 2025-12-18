import time
import uuid
from typing import Dict, List, Any, Optional, Tuple
from PySide6.QtCore import QObject, QTimer, Signal
import DyberPet.settings as settings

from .types import EventPriority, EventType, StandardEvent, PetStatus, LLMResponse
from .constants import REQUEST_MANAGER_CONFIG, EMOTION_ICON_MAP
from .error_handler import ErrorHandler
from .llm_client import LLMClient
from .event_queue import EventQueue
from .throttle_manager import ThrottleManager
from .request_tracker import RequestTracker

class LLMRequestManager(QObject):
    """大模型请求管理器"""
    
    # 信号定义
    error_occurred = Signal(str, str)
    update_software_monitor = Signal(float, float)
    register_bubble = Signal(dict)
    add_chatai_response = Signal(str)
    execute_actions = Signal(list) # 新增信号

    def __init__(self, llm_client: LLMClient, parent: Optional[QObject] = None):
        super().__init__(parent)
        
        # 初始化LLM客户端
        self.llm_client = llm_client
        self.llm_client.structured_response_ready.connect(self.handle_structured_response)
        self.llm_client.error_occurred.connect(self.handle_llm_error)

        # 核心组件
        self.error_handler = ErrorHandler(settings.language_code)
        self.event_queue = EventQueue(REQUEST_MANAGER_CONFIG["priority_threshold"])
        self.throttle_manager = ThrottleManager(REQUEST_MANAGER_CONFIG["high_priority_throttle_window"])
        self.request_tracker = RequestTracker()
        
        # 配置参数
        self.max_error_retries = settings.llm_config.get('max_retries', 3)
        self.retry_delay = settings.llm_config.get('retry_delay', 1)
        
        # 定时器
        self.retry_timers: Dict[str, QTimer] = {}
        self.first_time_api_key_error = True

    def _create_standard_event_data(self, event_type: EventType, priority: EventPriority, context: Dict[str, Any]) -> StandardEvent:
        """
        创建标准格式的事件数据

        Args:
            event_type: 事件类型
            priority: 事件优先级
            context: 事件上下文数据（不应包含timestamp和pet_status）

        Returns:
            标准格式的事件数据字典
        """
        # 生成事件ID
        event_id = str(uuid.uuid4())

        # 获取当前时间戳
        current_time = time.time()

        # 获取伴侣状态快照
        pet_status = self.get_pet_status()

        # 清理context中可能存在的重复字段
        clean_context = context.copy()
        clean_context.pop('timestamp', None)
        clean_context.pop('pet_status', None)

        # 构建标准事件数据
        standard_event = {
            "event_id": event_id,
            "event_type": event_type,
            "priority": priority,
            "timestamp": current_time,
            "pet_status": pet_status,
            "context": clean_context
        }

        # # 调试日志：验证标准事件数据格式
        # print(f"[调试] 创建标准事件数据 - ID: {event_id[:8]}..., 类型: {event_type.value}, 优先级: {priority.value}")
        # print(f"[调试] Context字段: {list(clean_context.keys())}")
        # if 'timestamp' in context or 'pet_status' in context:
        #     print(f"[警告] 原始context包含重复字段，已清理: timestamp={context.get('timestamp', 'None')}, pet_status={'存在' if 'pet_status' in context else '不存在'}")

        return standard_event

    def _process_high_priority_event(self, event_type: EventType, standard_event_list: list):
        """处理高优先级事件"""
        request_id = str(uuid.uuid4())
        message = self.build_request_message({event_type: standard_event_list})
        
        if self.send_llm_request(message, request_id):
            self.request_tracker.add(request_id, event_type, EventPriority.HIGH, message)
            print(f"[LLM Request Manager] 发送高优先级请求: {request_id}")

    def add_event_from_petwidget(self, data_dict: dict):
        """
        从PetWidget接收事件数据并转换为标准格式

        Args:
            data_dict: 包含event_type、priority、event_data的字典
        """
        print(f"[调试] PetWidget事件接收 - 类型: {data_dict['event_type'].value}, 优先级: {data_dict['priority'].value}")
        print(f"[调试] 原始event_data字段: {list(data_dict['event_data'].keys())}")

        # 使用标准方法创建事件数据
        standard_event = self._create_standard_event_data(
            data_dict['event_type'],
            data_dict['priority'],
            data_dict['event_data']
        )

        # 调用内部add_event方法
        self.add_event(standard_event)

    def add_event_from_chatai(self, message: str) -> None:
        """
        从ChatAI接收消息并转换为标准格式的事件

        Args:
            message: 用户输入的聊天消息
        """
        print(f"[调试] ChatAI事件接收 - 消息: {message[:50]}{'...' if len(message) > 50 else ''}")

        # 构建聊天事件的context
        context = {
            "message": message,
            "description": "用户直接对话",
            "type": "chat"
        }

        # 使用标准方法创建事件数据
        standard_event = self._create_standard_event_data(
            EventType.USER_INTERACTION,
            EventPriority.HIGH,
            context
        )

        # 调用内部add_event方法，跳过节流
        self.add_event(standard_event, skip_throttle=True)

    def add_event(self, standard_event: Dict[str, Any], skip_throttle=False) -> None:
        """
        添加标准格式的事件到累积器

        Args:
            standard_event: 标准格式的事件数据
            skip_throttle: 是否跳过节流处理
        """
        if not settings.llm_config.get('enabled', False):
            print("[LLM Request Manager] LLM未启用")
            if skip_throttle:
                msg = self.error_handler._messages.get("E010", "LLM功能未启用")
                self.error_occurred.emit(msg, None)
            return
        if not settings.llm_config.get('api_key', ''):
            print("[LLM Request Manager] 未设置API Key")
            if self.first_time_api_key_error or skip_throttle:
                self.first_time_api_key_error = False
                msg = self.error_handler._messages.get("E005", "未设置API密钥")
                self.error_occurred.emit(msg, None)
            return

        event_type = standard_event["event_type"]
        priority = standard_event["priority"]

        # 高优先级事件直接处理
        if priority == EventPriority.HIGH:
            self.process_high_priority_event(event_type, standard_event, skip_throttle)
            return

        # 其他事件加入队列
        self.event_queue.add(standard_event, is_high_priority=False)
        if self.event_queue.should_process(event_type):
            self.process_accumulated_events(event_type)

    def process_high_priority_event(self, event_type: EventType, standard_event: Dict[str, Any], skip_throttle=False) -> None:
        """处理高优先级事件"""
        if skip_throttle:
            self._process_high_priority_event(event_type, [standard_event])
            return
        
        # 检查是否需要节流
        if self.throttle_manager.should_throttle(event_type, True):
            self.event_queue.add(standard_event, is_high_priority=True)
            self.throttle_manager.restart_timer(event_type, True)
            print(f"[节流] 合并事件: {event_type.value}")
            return
        
        # 检查是否有同类型高优先级请求正在处理
        if self.request_tracker.is_high_priority_processing(event_type):
            self.event_queue.add(standard_event, is_high_priority=True)
            self.throttle_manager.set_deadline(event_type, True)
            self.throttle_manager.start_timer(
                event_type, True,
                lambda: self._process_throttled_events(event_type),
                parent=self
            )
            print(f"[节流] 创建待处理事件: {event_type.value}")
            return
        
        # 直接处理
        self._process_high_priority_event(event_type, [standard_event])

    def _process_throttled_events(self, event_type: EventType) -> None:
        """处理节流事件"""
        events = self.event_queue.pop(event_type, is_high_priority=True)
        if events:
            print(f"[节流] 处理{len(events)}个事件: {event_type.value}")
            self._process_high_priority_event(event_type, events)
        self.throttle_manager.stop_timer(event_type, True)

    def handle_llm_error(self, error: Dict[str, str], request_id: Optional[str] = None) -> None:
        """处理LLM错误"""
        if not request_id or not self.request_tracker.exists(request_id):
            print(f"[LLM Request Manager] 忽略无效请求ID: {request_id}")
            return
        
        if self.request_tracker.get_retry_count(request_id) < self.max_error_retries:
            self._schedule_retry(request_id)
        else:
            self._handle_final_error(error, request_id)
    
    def _schedule_retry(self, request_id: str) -> None:
        """计划重试请求"""
        retry_count = self.request_tracker.increment_retry(request_id)
        print(f"正在重试请求: {request_id}, 重试次数: {retry_count}")
        
        retry_timer = QTimer(self)
        retry_timer.setSingleShot(True)
        retry_timer.timeout.connect(lambda: self._retry_request(request_id))
        self.retry_timers[request_id] = retry_timer
        retry_timer.start(self.retry_delay * 1000)
    
    def _handle_final_error(self, error: Dict[str, str], request_id: str) -> None:
        """处理最终错误"""
        msg, details, _ = self.error_handler.get_error_info(error)
        self._stop_all_queues()
        self.delete_request(request_id)
        self.error_occurred.emit(msg, details)


    def _retry_request(self, request_id: str):
        """执行重试请求"""
        req_info = self.request_tracker.get(request_id)
        if not req_info:
            return

        print(f"执行延迟重试: {request_id}")
        if not self.send_llm_request(req_info["message"], request_id):
            self.handle_llm_error({"code": "E011", "details": "重试发送失败"}, request_id)
        
        self.retry_timers.pop(request_id, None)

    def _stop_all_queues(self):
        """停止所有队列和定时器"""
        print("[LLM Request Manager] 停止所有队列")
        
        for timer in self.retry_timers.values():
            if timer.isActive():
                timer.stop()
        self.retry_timers.clear()
        
        self.throttle_manager.stop_all()
        self.event_queue.clear()
        self.request_tracker.clear()

    def delete_request(self, request_id: Optional[str] = None):
        """清理请求记录"""
        if request_id:
            timer = self.retry_timers.pop(request_id, None)
            if timer and timer.isActive():
                timer.stop()
            self.request_tracker.remove(request_id)
        else:
            for timer in self.retry_timers.values():
                if timer.isActive():
                    timer.stop()
            self.retry_timers.clear()
            self.request_tracker.clear()


    def handle_structured_response(self, response, request_id: Optional[str] = None):
        """处理LLM结构化响应"""
        if request_id and not self.request_tracker.exists(request_id):
            print(f"[LLM Request Manager] 忽略未知请求ID: {request_id}")
            return
        
        self.handle_llm_response(response)
        self.delete_request(request_id)


    def handle_llm_response(self, data: LLMResponse) -> None:
        """处理LLM结构化响应"""
        if not isinstance(data, dict):
            return
        
        self._handle_adaptive_timing(data)
        self._handle_emotion_bubble(data)
        self._handle_chat_response(data)
        self._handle_actions(data)
    
    def _handle_adaptive_timing(self, data: LLMResponse) -> None:
        """处理自适应时间间隔"""
        if not data.get('adaptive_timing_decision'):
            return
        
        new_interval = data.get('recommended_interval')
        new_idle_threshold = data.get('recommended_idle_threshold')
        
        adaptive_interval = None
        if new_interval and isinstance(new_interval, (int, float)) and 300 <= new_interval <= 3600:
            adaptive_interval = new_interval
            print(f"[自适应] 更新交互间隔: {new_interval}秒")
        
        idle_threshold = None
        if new_idle_threshold and isinstance(new_idle_threshold, (int, float)) and 60 <= new_idle_threshold <= 1800:
            idle_threshold = new_idle_threshold
            print(f"[自适应] 更新空闲阈值: {new_idle_threshold}秒")
        
        self.update_software_monitor.emit(adaptive_interval, idle_threshold)
    
    def _handle_emotion_bubble(self, data: LLMResponse) -> None:
        """处理情绪气泡"""
        if not (data.get('emotion') and settings.bubble_on):
            return
        
        emotion = data.get('emotion', '正常')
        emotion_icon = EMOTION_ICON_MAP.get(emotion, "bb_normal")
        
        text_content = data.get('text', '')
        bubble_message = text_content.split('<sep>')[0].strip() if '<sep>' in text_content else text_content
        
        bubble_data = {
            "bubble_type": "llm",
            "icon": emotion_icon,
            "message": bubble_message,
            "countdown": None,
            "start_audio": None,
            "end_audio": None
        }
        self.register_bubble.emit(bubble_data)
    
    def _handle_chat_response(self, data: LLMResponse) -> None:
        """处理聊天响应"""
        if data.get('text'):
            self.add_chatai_response.emit(data['text'])
    
    def _handle_actions(self, data: LLMResponse) -> None:
        """处理动作执行"""
        actions = data.get('action')
        if actions and isinstance(actions, list):
            print(f"[LLM Request Manager] 执行动作: {actions}")
            self.execute_actions.emit(actions)
            
        
    


    def process_accumulated_events(self, event_type: EventType) -> None:
        """处理累积事件"""
        events = self.event_queue.pop(event_type, is_high_priority=False)
        if not events:
            return
        
        request_id = str(uuid.uuid4())
        request_message = self.build_request_message({event_type: events})
        
        if self.send_llm_request(request_message, request_id):
            self.request_tracker.add(request_id, event_type, EventPriority.MEDIUM, request_message)
            print(f"[LLM Request Manager] 发送请求: {request_id}")

    def get_pet_status(self) -> PetStatus:
        return {
            'pet_name': settings.petname,
            'hp': f"{settings.pet_data.hp}/{settings.HP_TIERS[-1]*settings.HP_INTERVAL} ({settings.TIER_NAMES[settings.pet_data.hp_tier]})",
            'fv': f"{settings.pet_data.fv}/{settings.LVL_BAR[settings.pet_data.fv_lvl]}",
            'hp_tier': settings.pet_data.hp_tier,
            'fv_lvl': settings.pet_data.fv_lvl,
            'time': time.strftime("%H:%M")
        }
    
    def build_request_message(self, events_by_type: Dict[EventType, List[Dict]]) -> str:
        """
        根据累积的事件构建请求消息
        Args:
            events_by_type: 按类型分组的事件列表（标准事件结构）
        Returns:
            构建好的请求消息
        """
        try:
            message = ""
            # 从标准事件数据中获取伴侣状态（使用最新的事件）
            pet_status = None
            latest_timestamp = 0
            
            for events in events_by_type.values():
                for event in events:
                    # 新格式：标准事件数据结构
                    if isinstance(event, dict) and "pet_status" in event and "timestamp" in event:
                        event_timestamp = event["timestamp"]
                        if event_timestamp > latest_timestamp:
                            latest_timestamp = event_timestamp
                            pet_status = event["pet_status"]
            # 如果事件中没有状态信息，则获取当前状态
            if not pet_status:
                print("使用当前伴侣状态")
                pet_status = self.get_pet_status()
            # 添加事件信息
            for event_type, events in events_by_type.items():
                if events:
                    message += f"[{event_type.value}事件]\n"
                    for event in events:
                        # 获取context数据（标准事件结构）
                        context = event.get("context", {})
                        if context:
                            # 根据事件类型格式化上下文
                            if event_type == EventType.USER_INTERACTION:
                                # 检查是否有直接对话消息
                                if "message" in context:
                                    # 如果有交互强度信息，添加到消息中
                                    if "intensity" in context:
                                        message += f"{context['message']}\n"
                                    else:
                                        message += f"用户说: {context['message']}\n"
                                else:
                                    message += f"{context.get('description')}\n"
                                    # 如果有交互强度信息，添加到消息中
                                    if "intensity" in context:
                                        action_text = context.get('action', '与你互动')
                                        message += f"用户{action_text}\n"
                                        message += f"交互强度: {context['intensity']}\n"
                            elif event_type == EventType.STATUS_CHANGE:
                                # 提供更多原始信息，减少解释性描述
                                if "event_source" in context:
                                    message += f"来源=>{context['event_source']}\n "
                                message += f"{context.get('description')}\n"
                            elif event_type == EventType.TIME_TRIGGER:
                                message += f"当前是{context.get('time_period', '')}\n"
                            elif event_type == EventType.ENVIRONMENT:
                                message += f"{context.get('description', '')}\n"

            message += "\n"
            
            # 构建状态消息
            status_message = f"[伴侣状态] 名称:{pet_status.get('pet_name', settings.petname)}, "
            status_message += f"饱食度:{pet_status.get('hp', 'No Data')}, "
            status_message += f"好感度:{pet_status.get('fv', 'No Data')}, "
            status_message += f"好感度等级:{pet_status.get('fv_lvl', 'No Data')}, "
            status_message += f"时间:{pet_status.get('time', time.strftime('%H:%M'))}"
 
            # 如果有位置信息，添加到状态中
            if 'position' in pet_status:
                pos = pet_status['position']
                status_message += f", 你的位置:({pos['x']}/{pos['screen_width']},{pos['y']}/{pos['screen_height']})"
            
            # 将状态信息添加到消息末尾
            if message:
                message += "\n"
            message += status_message
            
            return message
        except Exception as e:
            print(f"构建请求消息失败: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return ""

    def send_llm_request(self, message: str, request_id: Optional[str] = None) -> None:
        """
        发送LLM请求
        Args:
            message: 请求消息内容
            request_id: 请求ID，用于跟踪响应
        """
        if not message:
            return False
        try:
            print(f"\n===== 发送LLM请求 (ID: {request_id}) =====\n{message}")
            # 调用LLM客户端发送消息
            self.llm_client.send_message(message, request_id)
            return True
        except Exception as e:
            print(f"发送LLM请求失败: {str(e)}")
            return False
        
    def reinitialize(self):
        """重新初始化LLM设定"""
        self._stop_all_queues()
        self.first_time_api_key_error = True
        self.llm_client.reinitialize_for_pet_change()
        
        print(f"[LLM Request Manager] 重新初始化完成 - 当前宠物: {settings.petname}")
    
    def cleanup(self):
        """清理所有资源，准备关闭"""
        print("[LLM Request Manager] Starting cleanup...")
        try:
            # Stop all queues and timers
            self._stop_all_queues()
            
            # Clean up LLM client
            if hasattr(self, 'llm_client') and self.llm_client:
                self.llm_client.close()
            
            print("[LLM Request Manager] Cleanup completed")
        except Exception as e:
            print(f"[LLM Request Manager] Error during cleanup: {e}")




if __name__ == "__main__":
    # 为了测试，直接导入
    import sys
    sys.path.append("c:\\Users\\admint\\Desktop\\新建文件夹\\DyberPet")
    from DyberPet.llm.llm_client import LLMClient
    
    manager = LLMRequestManager()
    context = {"action": "点击宠物"}
    manager.add_event(
        manager._create_standard_event_data(
            EventType.USER_INTERACTION,
            EventPriority.HIGH,
            context
        ),
        skip_throttle=True
    )
