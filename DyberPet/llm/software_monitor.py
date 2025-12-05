"""
软件监控模块
监控用户使用的软件应用程序
"""
import time
import psutil
from PySide6.QtCore import QObject, Signal


class SoftwareMonitor(QObject):
    """软件监控器"""
    
    software_status_updated = Signal(dict, str, str)  # active_windows, new_software, closed_software
    
    def __init__(self):
        super().__init__()
        self.last_active_window = None
        self.check_interval = 5
        self.running = False
        
    def set_check_interval(self, interval):
        """设置检查间隔"""
        self.check_interval = interval
        
    def run(self):
        """运行监控"""
        self.running = True
        while self.running:
            try:
                current_window = self.get_active_window()
                new_software = None
                closed_software = None
                
                if current_window != self.last_active_window:
                    if current_window:
                        new_software = current_window.get('name', '')
                    if self.last_active_window:
                        closed_software = self.last_active_window.get('name', '')
                    
                    self.last_active_window = current_window
                
                self.software_status_updated.emit(
                    current_window or {}, 
                    new_software or '', 
                    closed_software or ''
                )
                
                time.sleep(self.check_interval)
                
            except Exception as e:
                print(f"软件监控错误: {e}")
                time.sleep(self.check_interval)
    
    def get_active_window(self):
        """获取当前活跃窗口"""
        try:
            # 简化实现，返回当前进程信息
            current_process = psutil.Process()
            return {
                'name': current_process.name(),
                'title': 'Active Window'
            }
        except:
            return None
    
    def stop(self):
        """停止监控"""
        self.running = False
        
    def cleanup(self):
        """清理资源"""
        self.stop()