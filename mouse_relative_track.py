#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import struct
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QPoint
from PyQt5.QtGui import QKeySequence, QCursor
from PyQt5.QtWidgets import QShortcut

MOUSE_RELATIVE_DEVICE = '/dev/hidg1'

class MouseCaptureWidget(QWidget):
    coordinate_updated = pyqtSignal(int, int, int, int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)
        self.last_x = 0
        self.last_y = 0
        self.buttons = 0
        self.running = True
        
        # 添加屏幕相关属性
        self.screen = QApplication.primaryScreen()
        self.screen_rect = self.screen.geometry()
        self.center_x = self.screen_rect.width() // 2
        self.center_y = self.screen_rect.height() // 2
                
        # 修改窗口属性和标志
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnTopHint | 
            Qt.Tool |
            Qt.NoDropShadowWindowHint
        )
        
        # 更新样式表
        self.setStyleSheet("""
            QWidget {
                background-color: transparent;
                border: none;
                margin: 0;
                padding: 0;
            }
        """)
        # 添加备用退出快捷键
        self.escape_shortcut = QShortcut(QKeySequence("Esc"), self)
        self.escape_shortcut.activated.connect(self.parent().toggle_capture)
        
        # 添加移动灵敏度设置
        self.sensitivity = 2.0  # 可以根据需要调整这个值
        
    def keyPressEvent(self, event):
        # 允许Ctrl+Q事件传递给父窗口
        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_Q:
            event.ignore()
        else:
            super().keyPressEvent(event)
            
    def mousePressEvent(self, event):
        if not self.running:
            return
            
        button_map = {
            Qt.LeftButton: 1,
            Qt.RightButton: 2,
            Qt.MiddleButton: 4
        }
        
        if event.button() in button_map:
            self.buttons |= button_map[event.button()]
            self.send_mouse_relative_report(self.buttons, 0, 0)
    
    def mouseReleaseEvent(self, event):
        if not self.running:
            return
            
        button_map = {
            Qt.LeftButton: 1,
            Qt.RightButton: 2,
            Qt.MiddleButton: 4
        }
        
        if event.button() in button_map:
            self.buttons &= ~button_map[event.button()]
            self.send_mouse_relative_report(self.buttons, 0, 0)
    
    def mouseMoveEvent(self, event):
        if not self.running:
            return
            
        current_x = event.x()
        current_y = event.y()
        
        if self.last_x == 0 and self.last_y == 0:
            self.last_x = current_x
            self.last_y = current_y
            return
        
        # 计算移动距离并应用灵敏度
        dx = int((current_x - self.last_x) * self.sensitivity)
        dy = int((current_y - self.last_y) * self.sensitivity)
        
        # 检查是否接近屏幕边缘
        near_edge = (
            current_x <= 50 or 
            current_x >= self.screen_rect.width() - 50 or
            current_y <= 50 or 
            current_y >= self.screen_rect.height() - 50
        )
        
        if near_edge:
            # 将鼠标移动到屏幕中心
            QCursor.setPos(self.mapToGlobal(QPoint(self.center_x, self.center_y)))
            self.last_x = self.center_x
            self.last_y = self.center_y
        else:
            self.last_x = current_x
            self.last_y = current_y
        
        if dx != 0 or dy != 0:
            # 分段发送大的移动距离
            while abs(dx) > 127 or abs(dy) > 127:
                send_dx = max(-127, min(127, dx))
                send_dy = max(-127, min(127, dy))
                self.send_mouse_relative_report(self.buttons, send_dx, send_dy)
                dx -= send_dx
                dy -= send_dy
            
            # 发送剩余的移动距离
            if dx != 0 or dy != 0:
                self.send_mouse_relative_report(self.buttons, dx, dy)
            
            self.coordinate_updated.emit(dx, dy, current_x, current_y)
    
    def wheelEvent(self, event):
        if not self.running:
            return
            
        wheel_delta = event.angleDelta().y() // 120
        self.send_mouse_relative_report(self.buttons, 0, 0, wheel_delta)

    def send_mouse_relative_report(self, buttons, dx, dy, wheel=0, pan=0):
        buttons = buttons & 0xFF
        dx = max(-127, min(127, dx))
        dy = max(-127, min(127, dy))
        wheel = max(-127, min(127, wheel))
        pan = max(-127, min(127, pan))

        try:
            report = struct.pack('<bbbbb', buttons, dx, dy, wheel, pan)
            print(f"发送相对鼠标报告: buttons={buttons}, dx={dx}, dy={dy}, wheel={wheel}, pan={pan}")
            
            if os.path.exists(MOUSE_RELATIVE_DEVICE):
                with open(MOUSE_RELATIVE_DEVICE, 'wb') as device:
                    device.write(report)
                    device.flush()
            else:
                print(f"错误：设备 {MOUSE_RELATIVE_DEVICE} 不存在", file=sys.stderr)
        except IOError as e:
            print(f"发送HID报告时出错: {e}", file=sys.stderr)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("全屏鼠标事件捕获")
        self.setGeometry(100, 100, 300, 200)
        
        # 保持窗口始终在最顶层
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        # 创建主布局
        layout = QVBoxLayout()
        
        # 状态标签
        self.status_label = QLabel("鼠标事件捕获已启动")
        layout.addWidget(self.status_label)

        # 坐标显示标签
        self.coord_label = QLabel("dX: 0, dY: 0")
        layout.addWidget(self.coord_label)

        # 控制按钮
        self.toggle_button = QPushButton("停止捕获")
        self.toggle_button.clicked.connect(self.toggle_capture)
        layout.addWidget(self.toggle_button)

        # 添加热键支持
        self.shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)
        self.shortcut.setContext(Qt.ApplicationShortcut)
        self.shortcut.activated.connect(self.toggle_capture)
        
        # 添加热键提示
        self.shortcut_label = QLabel("按 Ctrl+Q 或 ESC 切换捕获状态")
        layout.addWidget(self.shortcut_label)

        # 设置中央窗口部件
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # 创建鼠标捕获窗口
        self.capture_widget = MouseCaptureWidget(self)
        self.capture_widget.coordinate_updated.connect(self.update_coordinates)
        self.capture_widget.showFullScreen()

    def update_coordinates(self, dx, dy, x, y):
        self.coord_label.setText(f"dX: {dx}, dY: {dy}")

    def toggle_capture(self):
        if self.toggle_button.text() == "停止捕获":
            self.capture_widget.running = False
            self.capture_widget.hide()
            self.status_label.setText("鼠标事件捕获已停止")
            self.toggle_button.setText("开始捕获")
            # 确保控制窗口可见
            self.raise_()
            self.activateWindow()
        else:
            self.capture_widget.running = True
            self.capture_widget.showFullScreen()
            self.status_label.setText("鼠标事件捕获已启动")
            self.toggle_button.setText("停止捕获")

    def closeEvent(self, event):
        self.capture_widget.close()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())



    