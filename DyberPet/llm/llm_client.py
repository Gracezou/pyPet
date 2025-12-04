import json
from typing import Dict, Any, Optional, List, Union
from PySide6.QtCore import QObject, Signal, QThread, QMutex, QWaitCondition
import queue

import DyberPet.settings as settings
from .api_factory import APIClientFactory
from .api_client_base import BaseAPIClient
from .conversation_manager import ConversationManager
from .constants import LLM_CONFIG_DEFAULTS

class LLMWorker(QThread):
    """处理LLM请求的持久工作线程"""
    response_ready = Signal(dict, str)
    error_occurred = Signal(dict, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._request_queue = queue.Queue()
        self._should_stop = False
        self._mutex = QMutex()
        self._wait_condition = QWaitCondition()
        self.api_client: Optional[BaseAPIClient] = None

    def set_api_client(self, api_client: BaseAPIClient) -> None:
        """设置API客户端"""
        self.api_client = api_client
    
    def enqueue_request(self, request_data: Dict[str, Any], request_id: Optional[str]):
        """将请求添加到队列中等待处理"""
        self._mutex.lock()
        self._request_queue.put({
            "request_data": request_data,
            "request_id": request_id
        })
        self._wait_condition.wakeOne()
        self._mutex.unlock()

    def run(self):
        """主工作循环，处理队列中的请求"""
        print("LLMWorker thread started.")
        while True:
            self._mutex.lock()
            if self._should_stop and self._request_queue.empty():
                self._mutex.unlock()
                break  # Exit loop if stop requested and queue is empty

            if self._request_queue.empty():
                self._wait_condition.wait(self._mutex)  # Wait for a new request or stop signal
                self._mutex.unlock()
                continue  # Re-check conditions

            task = self._request_queue.get()
            self._mutex.unlock()

            try:
                request_data = task["request_data"]
                request_id = task["request_id"]
                
                if not self.api_client:
                    raise Exception("API客户端未初始化")
                
                result = self.api_client.call_api(
                    messages=request_data["messages"],
                    model=request_data.get("model"),
                    temperature=request_data.get("temperature"),
                    max_tokens=request_data.get("max_tokens")
                )
                self.response_ready.emit(result, request_id)
            except Exception as e:
                print(f"\n===== LLMWorker错误 =====\n{str(e)}")
                error_code = "E006" if "API" in str(e) else "E003"
                self.error_occurred.emit({"code": error_code, "details": str(e)}, task.get("request_id"))
        print("LLMWorker thread finished.")

    def stop(self):
        """停止工作线程"""
        print("LLMWorker.stop() called")
        self._mutex.lock()
        self._should_stop = True
        self._wait_condition.wakeOne()  # Wake run() if it's waiting
        self._mutex.unlock()
        
        # Wait for the thread to finish, but with a timeout
        if not self.wait(1000):  # Wait up to 5 seconds
            print("LLMWorker thread did not stop gracefully, terminating...")
            self.terminate()
            self.wait(1000)  # Wait another second for termination
        
        print("LLMWorker.stop() completed")



class LLMClient(QObject):
    """
    与大模型服务通信的客户端类
    负责发送请求到本地或远程大模型服务并处理响应
    """
    error_occurred = Signal(dict, str, name='error_occurred')
    structured_response_ready = Signal(dict, str, name='structured_response_ready')
    
    def __init__(self, parent=None):
        super(LLMClient, self).__init__(parent)
        
        # 配置参数
        self.api_url = "http://localhost:8000/v1/chat/completions"
        self.remote_api_url = "https://api.example.com/v1/chat/completions"
        self.api_key = ""
        self.api_type = "Qwen"
        self.debug_mode = True
        
        # 对话管理器
        self.conversation_manager = ConversationManager()
        
        # 活跃请求追踪
        self._active_requests = {}

        self.schema_prompt = """
请遵循以下指导原则：
## 请求上下文信息

### 事件类型
你将会收到包含以下一种或多种事件类型的请求：
- [用户交互事件]：用户对话、点击、拖拽等
- [状态变化事件]：饱食度、好感度等属性变化
- [时间触发事件]：定时触发的事件
- [环境感知事件]：系统环境变化
- [随机触发事件]：随机触发的特殊事件

### 宠物状态
每次请求都会包含：宠物名称、饱食度(hp:0-100)、好感度(fv:0-120)、好感度等级(fv_lvl)、时间、位置坐标等状态信息

## 响应格式要求
请严格按照以下JSON格式回复，确保所有字段类型正确：

```json
{
    "text": "你的回复内容（可使用'<sep>'分隔多条消息）", // 回复文字内容，支持使用'<sep>'标记分隔多条消息
    "emotion": "高兴|难过|困惑|可爱|正常|天使", // 必须从上述指定的6种情绪中选择一种
    "action": ["动作3","动作1"], // 动作指令数组，最多3个，从可用动作中选择，如果不需要动作，请使用空数组[]
    //以下都是可选字段
    "open_web": "可选：需要打开网页时填写完整URL", // 可选字段，需要打开网页时填写完整URL
    "add_task": "可选：需要添加任务时填写任务内容", // 可选字段，需要添加任务时填写具体任务内容
    "adaptive_timing_decision": true, // 布尔值，用于调整软件监控相关的参数，决策请求时设为true
    "recommended_interval": 300-3600, // 软件监控参数，下次决策间隔（300-3600秒）
    "recommended_idle_threshold": 60-1800 // 软件监控参数，空闲检测阈值（60-1800秒）
}
```

## 可用动作列表
当前可用的动作包括：ACTION_LIST

## 示例回复
{
    "text": "你回来啦！😊 <sep>今天想和我聊什么呢？",
    "emotion": "高兴",
    "action": []
}
注意：请不要带上```json```标签，直接返回JSON格式

## 行为指导
1. **动作使用策略**：只在真正需要时才使用动作，保持低频率（约20%的回复中使用动作），避免过度使用
2. **点击交互**：用户点击行为会提供给你交互强度（0-1范围），如果有交互强度，可以根据此调整情感表达
3. **表情丰富**：在text对话中多使用emoji表情，弥补emotion字段的局限性
4. **避免重复**：遇到连续重复事件时，不要总是回复相似内容，要结合上下文和个性特点
5. **状态感知**：注意用户内容中[宠物状态]后的属性变化，据此调整回应
6. **格式要求**：确保回复是有效的JSON格式，软件监控参数调整时 (adaptive_timing_decision: true)，请保持 text 和 action 字段为空
"""
        self.structured_system_prompt = self.schema_prompt

        self._load_config()
        self._init_api_client()
        self.reset_conversation()
        
        self._worker = LLMWorker()
        self._worker.set_api_client(self.api_client)
        self._worker.response_ready.connect(self._handle_response)
        self._worker.error_occurred.connect(self._handle_error)
        self._worker.start()
            
    def _load_config(self):
        """从settings加载LLM配置"""
        try:
            config = getattr(settings, 'llm_config', LLM_CONFIG_DEFAULTS)
            self.model_type = config.get('model_type', 'Qwen')
            self.debug_mode = config.get('debug_mode', False)
            self.api_key = config.get('api_key', '')
            self.api_url = config.get('api_url', self.api_url)
            self.remote_api_url = config.get('remote_api_url', self.remote_api_url)
            
            if self.model_type == 'Qwen':
                self.api_type = 'dashscope'
            else:
                self.api_type = config.get('api_type', 'local')
            
            self._update_system_prompt()
        except Exception as e:
            print(f"加载LLM配置失败: {e}")
    
    def _init_api_client(self):
        """初始化API客户端"""
        try:
            api_url = self.remote_api_url if self.api_type == 'remote' else self.api_url
            self.api_client = APIClientFactory.create(
                api_type=self.api_type,
                api_key=self.api_key,
                api_url=api_url,
                debug_mode=self.debug_mode
            )
        except Exception as e:
            print(f"初始化API客户端失败: {e}")
    
    def _get_available_actions(self) -> List[str]:
        """获取当前宠物可用的动作列表"""
        try:
            if not hasattr(settings, 'act_data') or not hasattr(settings, 'petname'):
                return []
            
            act_configs = settings.act_data.allAct_params.get(settings.petname, {})
            available_actions = []
            
            for act_name, act_conf in act_configs.items():
                # 只包含已解锁的动作，且避免系统动作
                if (act_conf.get('unlocked', False) and 
                    -1 not in act_conf.get('status_type', [0, 0])):
                    available_actions.append(act_name)
            
            return available_actions
        except Exception as e:
            print(f"获取可用动作失败: {e}")
            return []
    
    def _update_system_prompt(self):
        """更新提示词中的动作列表"""
        try:
            available_actions = self._get_available_actions()
            action_list_str = ', '.join(f'"{action}"' for action in available_actions)
            
            # 更新schema_prompt中的动作列表
            updated_schema = self.schema_prompt.replace('ACTION_LIST', f'{action_list_str}')
            
            # 更新系统提示词
            if hasattr(settings, 'pet_conf') and settings.pet_conf.prompt:
                role_prompt = settings.pet_conf.prompt
            else:
                role_prompt = "你是一个智能的桌面宠物，需要根据用户交互和系统事件做出简短友好的回应。\n"
                        
            # 用户昵称
            usertag = settings.usertag_dict.get(settings.petname, "")
            if usertag:
                nickname_prompt = f"\n8.**用户昵称**：用户希望你称呼TA为{usertag}。"
            else:
                nickname_prompt = ""
            
            self.structured_system_prompt = role_prompt + updated_schema + \
                f"7. **语言匹配**：与用户语言设置保持一致，除非用户明确要求使用其他语言，当前用户语言设置是{settings.language_code}" + \
                nickname_prompt
            
            if self.debug_mode:
                print(f"[LLM Client] 更新角色提示词: {role_prompt}")
                print(f"[LLM Client] 更新动作列表: {action_list_str}")
                print(f"[LLM Client] 用户昵称: {usertag}")
                
        except Exception as e:
            print(f"更新系统提示词失败: {e}")
    
    def reset_conversation(self):
        """重置对话历史"""
        self._cleanup_all_requests()
        self.conversation_manager.clear()
        self.conversation_manager.set_system_prompt(self.structured_system_prompt)
    
    def send_message(self, message: Union[str, Dict[str, Any]], request_id: str) -> None:
        """发送消息到大模型"""
        message_text = message.get('content', '') if isinstance(message, dict) else str(message)
        
        self._active_requests[request_id] = {"message": {"role": "user", "content": message_text}}
        
        config = getattr(settings, 'llm_config', LLM_CONFIG_DEFAULTS)
        request_data = {
            "model": "local-model",
            "messages": self.conversation_manager.get_messages() + [self._active_requests[request_id]["message"]],
            "temperature": config.get('temperature', 0.8),
            "max_tokens": config.get('max_tokens', 600)
        }
        
        self._worker.enqueue_request(request_data, request_id)
    

 
    def _handle_response(self, response: Dict[str, Any], request_id: str):
        """处理LLM响应"""
        print("[调试 _handle_response] 函数处理LLM响应")
        
        # Check if this request is still active (not from a previous pet)
        if not self._is_request_active(request_id):
            return
            
        try:
            assistant_message = self._extract_assistant_message(response)
            if not assistant_message:
                print(f"[LLM Client] 空响应内容，清理请求: {request_id}")
                self._cleanup_request(request_id)
                return
                
            success = self._handle_structured_response(assistant_message, request_id)
            if success:
                self._add_user_message_to_history(request_id)
                self.conversation_manager.add_message("assistant", assistant_message)
            self._cleanup_request(request_id)
                
        except Exception as e:
            self._handle_error(f"处理响应时出错: {str(e)}", request_id)
    
    def _add_user_message_to_history(self, request_id: str):
        """将用户消息添加到对话历史"""
        if request_id in self._active_requests:
            msg = self._active_requests[request_id]["message"]
            self.conversation_manager.add_message(msg["role"], msg["content"])
            del self._active_requests[request_id]
    
    def _is_request_active(self, request_id: str) -> bool:
        """检查请求是否仍然活跃"""
        if request_id not in self._active_requests:
            print(f"[LLM Client] 忽略未知请求ID的回复: {request_id}")
            return False
        return True
    
    def _extract_assistant_message(self, response: Dict[str, Any]) -> str:
        """从响应中提取助手消息内容"""
        raw_content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
        # Strip any ```json and ``` tags only if they appear at start/end
        stripped_content = raw_content.strip().removeprefix("```json").removesuffix("```").strip()
        return stripped_content
    
    def _handle_structured_response(self, assistant_message: str, request_id: str):
        """处理结构化响应"""
        try:
            structured_response = json.loads(assistant_message)
            self.structured_response_ready.emit(structured_response, request_id)
            return True
        except json.JSONDecodeError:
            self._handle_error({"code": "E008", "details": assistant_message[:100] if assistant_message else None}, request_id)
            return False
        except Exception as e:
            self._handle_error({"code": "E009", "details": str(e)}, request_id)
            return False
    
    """
    def _update_continuation_state(self, structured_response: Dict[str, Any]):
        '''更新继续状态'''
        continue_previous = structured_response.get("continue_previous", False) and not self.is_interrupted
        print(f"continue_previous: {continue_previous}, is_interrupted: {self.is_interrupted}")
        
        if continue_previous:
            print("设置waiting_for_action_complete为True")
            self.waiting_for_action_complete = True
        else:
            print("重置中断标志")
            self.reset_interrupt()
            self.waiting_for_action_complete = False
    """
    
    def _handle_error(self, error_message: dict, request_id: str):
        """处理所有错误（包括LLMWorker错误和响应处理错误）"""
        # Check if this request is still active (not from a previous pet)
        if not self._is_request_active(request_id):
            print(f"[LLM Client] 忽略未知请求ID的错误: {request_id}")
            return
            
        print(f"[LLM Client] 处理错误: {error_message}, 请求ID: {request_id}")
        
        self.error_occurred.emit(error_message, request_id)
        # Clean up the request (includes pending message cleanup)
        self._cleanup_request(request_id)
    
    # def interrupt_current_action(self):
    #     """中断当前正在执行的动作序列 (client-side logic)"""
    #     self.is_interrupted = True
    #     print("已中断当前动作序列")
    #     # Note: This does not interrupt a network request already in progress in the worker.
        
    # def reset_interrupt(self):
    #     """重置中断标志"""
    #     self.is_interrupted = False
        
    # def send_continue_message(self):
    #     '''发送继续对话的消息'''
    #     print(f"[调试 send_continue_message]函数被调用，is_interrupted: {self.is_interrupted}")
    #     if self.is_interrupted:
    #         print("动作序列已被中断，不再继续")
    #         self.reset_interrupt()
    #         return
            
    #     last_assistant_message_content: Optional[str] = None
    #     for msg in reversed(self.conversation_history):
    #         if msg["role"] == "assistant":
    #         last_assistant_message_content = msg["content"]
    #         break
        
    #     continue_message = "请继续你刚才未完成的内容。"
    #     if last_assistant_message_content:
    #         try:
    #             import re
    #             json_text = last_assistant_message_content
    #             json_match = re.search(r'```(?:json)?\s*({.*?})\s*```', last_assistant_message_content, re.DOTALL)
    #             if json_match:
    #             json_text = json_match.group(1)
                
    #             last_response = json.loads(json_text)
    #             last_text = last_response.get("text", "")
    #             last_action = last_response.get("action", [])
    #             last_emotion = last_response.get("emotion", "")
                
    #             continue_message = f"请继续你刚才未完成的内容。你上次的回复是「{last_text}」，情绪是「{last_emotion}」，"
    #             action_str = ""
    #             if isinstance(last_action, list) and last_action:
    #                 action_str = f"动作是{last_action}。"
    #             elif isinstance(last_action, str) and last_action:
    #                 action_str = f"动作是{last_action}。"
    #             else:
    #                 action_str = "没有指定动作。"
    #             continue_message += action_str + "继续你的回答。"
    #         except (json.JSONDecodeError, Exception) as e:
    #             print(f"解析上一次响应失败: {e}")
        
    #     print(f"发送继续消息: {continue_message}")
    #     self.send_message(continue_message)

    # def handle_action_complete(self):
    #     return
    #     """处理动作完成事件"""
    #     print(f"[调试 动作完成事件触发]，waiting_for_action_complete: {self.waiting_for_action_complete}, is_interrupted: {self.is_interrupted}")
    #     print(f"[调试] LLMClient实例ID: {id(self)}")
    #     if self.waiting_for_action_complete and not self.is_interrupted:
    #         print("动作完成后，直接调用send_continue_message")
    #         self.send_continue_message()
    #     self.waiting_for_action_complete = False

    def close(self):
        """停止LLM工作线程并进行清理"""
        print("Closing LLMClient, stopping worker...")
        try:
            # Clear all active requests first
            self._cleanup_all_requests()
            
            # Stop the worker thread
            if hasattr(self, '_worker') and self._worker is not None:
                self._worker.stop()
                print("LLMWorker stopped by LLMClient.close()")
            
        except Exception as e:
            print(f"Error during LLMClient.close(): {e}")
        finally:
            print("LLMClient.close() completed")

    def change_model(self):
        self.model_type = settings.llm_config.get('model_type', 'Qwen')
        self.api_type = 'dashscope' if self.model_type == 'Qwen' else 'remote'
        self._init_api_client()
        self._worker.set_api_client(self.api_client)
        print(f"切换模型为{self.model_type}")
        self.reset_conversation()

    def change_debug_mode(self):
        self.debug_mode = settings.llm_config.get('debug_mode', False)
        print(f"切换调试模式为{self.debug_mode}")

    def reinitialize_for_pet_change(self):
        """切换桌宠时重新初始化"""
        try:
            print(f"LLM模块重新初始化 - 当前桌宠: {settings.petname}")
            self._cleanup_all_requests()
            self._load_config()
            self._init_api_client()
            self._worker.set_api_client(self.api_client)
            self.reset_conversation()
            print("LLM模块重新初始化完成")
        except Exception as e:
            print(f"LLM模块重新初始化失败: {e}")

    def update_prompt_and_history(self):
        """更新动作列表"""
        try:
            print(f"[LLM Client] 更新 prompt")
            self._update_system_prompt()
            self.conversation_manager.set_system_prompt(self.structured_system_prompt)
        except Exception as e:
            print(f"[LLM Client] 更新 prompt 失败: {e}")

    def switch_api_type(self, api_type: str):
        """切换API类型"""
        if api_type not in ["local", "remote", "dashscope"]:
            raise ValueError("不支持的API类型")
        
        self.api_type = api_type
        self._init_api_client()
        self._worker.set_api_client(self.api_client)
        
        if hasattr(settings, 'llm_config'):
            settings.llm_config['api_type'] = api_type
            settings.save_settings()
        self.reset_conversation()

    
    def update_api_key(self):
        self.api_key = settings.llm_config.get('api_key', '')
        self._init_api_client()
        self._worker.set_api_client(self.api_client)
        print(f"更新API密钥")

    def _cleanup_all_requests(self):
        """清理所有活跃请求"""
        self._active_requests.clear()

    def _cleanup_request(self, request_id: str):
        """清理请求"""
        self._active_requests.pop(request_id, None)
