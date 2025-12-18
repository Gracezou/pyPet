"""
统一的UI颜色规范系统
支持亮色/暗色主题自动适配
"""
from PySide6.QtGui import QColor
from qfluentwidgets import isDarkTheme

class ThemeColors:
    """主题感知颜色系统"""

    @staticmethod
    def text_primary():
        """主要文本颜色 - 高对比度"""
        return QColor(33, 33, 33) if not isDarkTheme() else QColor(255, 255, 255)

    @staticmethod
    def text_secondary():
        """次要文本颜色 - 中等对比度"""
        return QColor(80, 80, 80) if not isDarkTheme() else QColor(200, 200, 200)

    @staticmethod
    def text_tertiary():
        """辅助文本颜色 - 低对比度（禁用状态）"""
        return QColor(140, 140, 140) if not isDarkTheme() else QColor(120, 120, 120)

    @staticmethod
    def background_primary():
        """主背景色"""
        return QColor(255, 255, 255) if not isDarkTheme() else QColor(32, 32, 32)

    @staticmethod
    def background_secondary():
        """次要背景色（卡片、面板）"""
        return QColor(249, 249, 249) if not isDarkTheme() else QColor(43, 43, 43)

    @staticmethod
    def separator():
        """分隔线颜色"""
        if isDarkTheme():
            return QColor(255, 255, 255, 51)  # 白色半透明
        else:
            return QColor(0, 0, 0, 30)  # 黑色半透明

    @staticmethod
    def hp_bar_colors():
        """HP进度条颜色（按层级）"""
        # 返回值：[极低, 低, 中, 高]
        return [
            "#f8595f",  # 红色 - 极低
            "#f8595f",  # 红色 - 低
            "#FAC486",  # 金色 - 中等
            "#6bc96f"   # 深绿色 - 高（替换浅绿#abf1b7以提高对比度）
        ]

    @staticmethod
    def fv_bar_color():
        """好感度进度条颜色"""
        return "#F4665C"  # 珊瑚红

    @staticmethod
    def progress_bar_text():
        """进度条文本颜色"""
        return QColor(0, 0, 0)  # 黑色（与HP/FV条搭配）

    @staticmethod
    def badge_text_for_background(bg_color: QColor):
        """根据背景色亮度自动选择徽章文本颜色"""
        # 计算亮度（相对亮度公式）
        luminance = (0.299 * bg_color.red() +
                    0.587 * bg_color.green() +
                    0.114 * bg_color.blue()) / 255

        # 亮度阈值 0.5
        return QColor(0, 0, 0) if luminance > 0.5 else QColor(255, 255, 255)
