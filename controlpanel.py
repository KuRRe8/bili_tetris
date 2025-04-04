"""
File: controlpanel.py
Author: KuRRe8
Created: 2025-04-05
Description:
    创建一个半透明的置顶信息面板，显示关键信息，如最高行数和决策数。
    窗口无边框、透明，并保持在最前面。
"""

import config.settings
from _logger import logger
import tkinter as tk

class ControlPanel:
    def __init__(self):
        self.root = tk.Tk()

        # 设置窗口为置顶
        self.root.attributes('-topmost', config.settings.CP_TOPMOST)

        # 设置窗口透明度
        self.root.attributes('-alpha', config.settings.CP_ALPHA)

        # 不显示窗口边框
        self.root.overrideredirect(True)

        # 设置窗口大小和位置
        self.root.geometry('300x100+100+100')  # 宽度300，高度100，位置(100,100)

        # 添加标签用于显示信息
        self.label = tk.Label(self.root, text="最高行数: 0\n决策数: 0", font=("Arial", 14), bg='black', fg='white')
        self.label.pack(fill='both', expand=True)

        # 绑定鼠标事件以实现拖动
        self.label.bind("<Button-1>", self.start_move)
        self.label.bind("<B1-Motion>", self.do_move)

        # 绑定键盘事件以响应 Esc 键退出
        self.root.bind("<Escape>", self.exit_window)

        # 初始化拖动相关变量
        self._offset_x = 0
        self._offset_y = 0

    def start_move(self, event):
        # 记录鼠标按下时的偏移量
        self._offset_x = event.x
        self._offset_y = event.y

    def do_move(self, event):
        # 根据鼠标移动更新窗口位置
        x = self.root.winfo_x() + event.x - self._offset_x
        y = self.root.winfo_y() + event.y - self._offset_y
        self.root.geometry(f"+{x}+{y}")

    def exit_window(self, event):
        # 退出窗口
        self.root.destroy()

    def start(self):
        # 启动窗口的主循环
        self.root.mainloop()

    def update(self, highest_row, decision_rate):
        # 更新标签的文本
        self.label.config(text=f"最高行数: {highest_row}\n决策数: {decision_rate}")

if __name__ == "__main__":
    logger.info('Control Panel test1')
    conp = ControlPanel()
    conp.start()