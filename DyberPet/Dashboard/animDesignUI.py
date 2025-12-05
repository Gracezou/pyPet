"""
动画设计UI模块
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal

class ActDesignWindow(QWidget):
    """动画设计窗口"""

    createNewAnim = Signal(str, dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("动画设计")
        self.setFixedSize(400, 300)

        layout = QVBoxLayout()
        label = QLabel("动画设计功能暂未实现")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        self.setLayout(layout)

    def updateCombo(self):
        """更新组合框 - 占位方法"""
        pass