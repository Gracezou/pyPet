#!/usr/bin/env python3
"""
AI桌面伴侣 - 主入口文件
基于DyberPet二次开发的AI智能桌面伴侣
"""

import sys
import os
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """主函数 - 启动AI桌面伴侣"""
    try:
        # 导入并运行应用
        from run_DyberPet import DyberPetApp
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt
        from tendo import singleton
        
        # 避免多进程
        try:
            me = singleton.SingleInstance()
        except:
            print("AI桌面伴侣已在运行中")
            sys.exit(1)
        
        # 创建应用
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
        
        app = DyberPetApp(sys.argv)
        app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)
        
        print("🎉 AI桌面伴侣启动成功！")
        sys.exit(app.exec())
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保已安装所有依赖: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()