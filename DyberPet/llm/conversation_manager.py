"""对话历史管理器"""
from typing import List, Dict
from collections import deque
from .constants import REQUEST_MANAGER_CONFIG


class ConversationManager:
    """对话历史管理器（滑动窗口）"""
    
    def __init__(self, max_history: int = None):
        self.max_history = max_history or REQUEST_MANAGER_CONFIG["max_conversation_history"]
        self._history = deque(maxlen=self.max_history)
        self._system_prompt: Dict[str, str] = {}
    
    def set_system_prompt(self, prompt: str) -> None:
        """设置系统提示词"""
        self._system_prompt = {"role": "system", "content": prompt}
    
    def add_message(self, role: str, content: str) -> None:
        """添加消息"""
        self._history.append({"role": role, "content": content})
    
    def get_messages(self) -> List[Dict[str, str]]:
        """获取完整消息列表（包含系统提示词）"""
        messages = []
        if self._system_prompt:
            messages.append(self._system_prompt)
        messages.extend(list(self._history))
        return messages
    
    def clear(self) -> None:
        """清空历史"""
        self._history.clear()
    
    def get_token_estimate(self) -> int:
        """估算token数量（粗略估计）"""
        total_chars = sum(len(msg["content"]) for msg in self._history)
        if self._system_prompt:
            total_chars += len(self._system_prompt["content"])
        return total_chars // 2  # 粗略估计：2字符≈1token
    
    def __len__(self) -> int:
        return len(self._history)
