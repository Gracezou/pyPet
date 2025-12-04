"""鼠标工具类"""
from PySide6.QtCore import QObject, Signal
import pynput.mouse as mouse


class MouseMoveManager(QObject):
    """鼠标移动管理器"""
    moved = Signal(int, int)
    clicked = Signal(bool)

    def __init__(self, movement=True, click=False, parent=None):
        super().__init__(parent)
        if movement and click:
            self._listener = mouse.Listener(on_move=self._handle_move,
                                            on_click=self._handle_click)
        elif movement:
            self._listener = mouse.Listener(on_move=self._handle_move)
        elif click:
            self._listener = mouse.Listener(on_click=self._handle_click)
        else:
            return

        self._listener.start()

    def _handle_move(self, x, y):
        self.moved.emit(x, y)

    def _handle_click(self, x, y, button, pressed):
        if button == mouse.Button.left:
            self.clicked.emit(pressed)
