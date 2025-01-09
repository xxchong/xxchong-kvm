import sys
import os
from datetime import datetime
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt, QTimer, QSettings, pyqtSignal
from PyQt5.QtGui import QIcon, QKeyEvent, QCursor, QPalette
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QAction, QDialog, QFileDialog, QPushButton, QVBoxLayout, QLineEdit, QGridLayout
from PyQt5.QtMultimedia import QCamera, QCameraInfo
from PyQt5.QtMultimediaWidgets import QCameraViewfinder
import logging
from module.video_module import VideoHandler
from module.keyboard_module import KeyboardHandler #导入键盘模块
from module.mouse_module import MouseHandler #导入鼠标模块
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

#快捷键
shortcuts = ["Meta","Ctrl+Alt+Del", "Alt+Tab", "Ctrl+Shift+Esc", "Alt+F4","Meta+E","Meta+Tab", "Meta+R", "Meta+PrtSc", "Meta+Break","Shift+F10", "Alt+Space"]
keyboard_handler = None #初始化键盘处理
mouse_handler = None #初始化鼠标处理
camera_started = False#摄像头是否启动

from custom_shortcut_dialog import CustomShortcutDialog


# 设备设置对话框类
class DeviceSetupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('Device_Setup.ui', self)  # 加载UI文件
        self.setWindowTitle("分辨率设置")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)  # 移除帮助按钮


# 主窗口UI类
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        self.MainWindow = MainWindow  # 保存对MainWindow的引用
        MainWindow.resize(800, 600)   # 设置初始大小,但允许调整
        # MainWindow.setMinimumSize(800, 600)  # 添加最小尺寸限制

        self.centralwidget = QCameraViewfinder(MainWindow)       # 设置中央部件为摄像头取景器
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)
      # 创建菜单栏
        self.menubar = QtWidgets.QMenuBar(MainWindow) 
        self.menubar.setFixedHeight(25)
        self.menubar.setObjectName("menubar")
        # 创建"输入设备"菜单
        self.menu_video_menu = QtWidgets.QMenu(self.menubar)
        self.menu_video_menu.setTitle("输入设备")
        self.menubar.addMenu(self.menu_video_menu)
         # 连接 aboutToShow 信号到 refresh_input_devices 方法
        self.menu_video_menu.aboutToShow.connect(self.refresh_input_devices)
        # 创建"鼠标模式"菜单
        self.menu_mouse_mode = QtWidgets.QMenu(self.menubar)
        self.menu_mouse_mode.setTitle("鼠标模式")
        self.menubar.addMenu(self.menu_mouse_mode)
        # 创建"鼠标绝对模式"动作
        self.action_mouse_absolute = QAction("绝对模式", self.menu_mouse_mode)
        self.action_mouse_absolute.setIcon(QIcon("./Icon/mouse.png"))
        self.action_mouse_absolute.setCheckable(True)
        self.action_mouse_absolute.setChecked(True) #默认选中绝对模式
        self.menu_mouse_mode.addAction(self.action_mouse_absolute)
        # 创建"鼠标相对模式"动作
        self.action_mouse_relative = QAction("相对模式", self.menu_mouse_mode)
        self.action_mouse_relative.setIcon(QIcon("./Icon/mouse.png"))
        self.action_mouse_relative.setCheckable(True)
        self.menu_mouse_mode.addAction(self.action_mouse_relative)
        # 将动作添加到动作组中，确保只有一个模式被选中
        self.mouse_mode_group = QtWidgets.QActionGroup(self.menu_mouse_mode)#创建动作组 
        self.mouse_mode_group.addAction(self.action_mouse_absolute)
        self.mouse_mode_group.addAction(self.action_mouse_relative)
        self.mouse_mode_group.setExclusive(True)#设置为互斥，确保只有一个模式被选中

        # 创建"键盘支持"菜单
        self.menu_keyboard_support = QtWidgets.QMenu(self.menubar)
        self.menu_keyboard_support.setTitle("键盘布局")
        self.menubar.addMenu(self.menu_keyboard_support)
           # 创建"键盘支持"动作
        self.action_keyboard_US = QAction("US", self.menu_keyboard_support)
        self.action_keyboard_US.setIcon(QIcon("./Icon/shortcutkey.png"))
        self.action_keyboard_US.setCheckable(True)
        self.action_keyboard_US.setChecked(True) #默认选中uk
        self.menu_keyboard_support.addAction(self.action_keyboard_US)
        # 创建"鼠标相对模式"动作
        self.action_keyboard_UK = QAction("UK", self.menu_keyboard_support)
        self.action_keyboard_UK.setIcon(QIcon("./Icon/shortcutkey.png"))
        self.action_keyboard_UK.setCheckable(True)
        self.menu_keyboard_support.addAction(self.action_keyboard_UK)
        # 将动作添加到动作组中，确保只有一种键盘支持被选中
        self.keyboard_support_group = QtWidgets.QActionGroup(self.menu_keyboard_support)#创建动作组 
        self.keyboard_support_group.addAction(self.action_keyboard_US)
        self.keyboard_support_group.addAction(self.action_keyboard_UK)
        self.keyboard_support_group.setExclusive(True)#设置为互斥，确保只有一种键盘支持被选中

        # 创建"快捷键"菜单
        self.menu_shortcut_key = QtWidgets.QMenu(self.menubar)
        self.menu_shortcut_key.setTitle("快捷键")
        self.menubar.addMenu(self.menu_shortcut_key)
        # 添加快捷键动作
        self.custom_shortcut = QAction("自定义快捷键", self.menu_shortcut_key)
        self.custom_shortcut.setIcon(QIcon("./Icon/shortcutkey.png"))
        self.menu_shortcut_key.addAction(self.custom_shortcut)

        for shortcut in shortcuts:
            action = QAction(shortcut, self.menu_shortcut_key)
            action.setIcon(QIcon("./Icon/shortcutkey.png"))
            action.triggered.connect(lambda checked, s=shortcut: self.send_shortcut(s))#绑定快捷键的操作
            self.menu_shortcut_key.addAction(action)
        # 创建"文本"菜单
        self.menu_text_input = QtWidgets.QMenu(self.menubar)
        self.menu_text_input.setTitle("文本")
        self.menubar.addMenu(self.menu_text_input)
        #建创建"粘贴"动作
        self.action_paste = QAction("粘贴", self.menubar)
        self.action_paste.setIcon(QIcon("./Icon/paste.png"))
        self.menu_text_input.addAction(self.action_paste)
        # 创建"设置"菜单
        self.menu_settings = QtWidgets.QMenu(self.menubar)
        self.menu_settings.setTitle("设置")
        self.menubar.addMenu(self.menu_settings)
        # 创建"分辨率设置"动作
        self.action_resolution = QAction("分辨率设置", self.menu_settings)
        self.action_resolution.setIcon(QIcon("./Icon/resolution.png"))
        self.action_resolution.triggered.connect(self.device_config)
        self.menu_settings.addAction(self.action_resolution)
        # 创建"文件保存路径"动作
        self.action_save_path = QAction("文件保存路径", self.menu_settings)
        self.action_save_path.setIcon(QIcon("./Icon/folder.png"))
        self.action_save_path.triggered.connect(self.set_save_path)
        self.menu_settings.addAction(self.action_save_path)
         # 创建"退出"动作
        self.action_exit = QAction("退出", self.menu_settings)
        self.action_exit.setIcon(QIcon("./Icon/exit.png"))
        self.action_exit.triggered.connect(self.exit_program)
        self.menu_settings.addAction(self.action_exit)

        # 创建"截屏"动作
        self.action_screenshot = QAction("截屏", self.menubar)
        self.action_screenshot.setIcon(QIcon("./Icon/screenshot.png"))
        self.action_screenshot.triggered.connect(self.take_screenshot)
        self.menubar.addAction(self.action_screenshot)
        # 设置菜单栏
        MainWindow.setMenuBar(self.menubar)
        # 创建状态栏
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        # 设置状态栏样式，添加顶部边框线
        self.statusbar.setStyleSheet("""
            QStatusBar {
                border-top: 1px solid #B2B2B2; 
                background-color: #F0F0F0;    
            }
        """)
        MainWindow.setStatusBar(self.statusbar)
        # 初始化视频处理模块 *********************************************
        self.video_handler = VideoHandler(MainWindow, self.centralwidget)
        # 创建设备设置对话框
        self.device_setup_dialog = DeviceSetupDialog(MainWindow)
        # 重新翻译UI
        self.retranslateUi(MainWindow)
        # 连接槽函数
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        # 初始刷新输入设备列表
        self.refresh_input_devices()
        # 加载保存路径设置
        self.settings = QSettings("YourCompany", "YourApp")
        self.save_path = self.settings.value("save_path", os.path.join(os.path.dirname(os.path.abspath(__file__)), "Screenshots"))

            # 加载上次保存的键盘布局设置，如果没有保存过则默认使用'US'
        saved_layout = self.settings.value("keyboard_layout", "US")
        
        # 根据保存的设置设置相应的布局
        if saved_layout == "UK":
            self.action_keyboard_UK.trigger()
        else:
            self.action_keyboard_US.trigger()

    # 退出程序
    def exit_program(self):
        self.MainWindow.close()


    def send_shortcut(self, shortcut):
        # 这个方法将在MainWindow类中实现
        pass

     # 设置UI文本
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "KVM"))
        MainWindow.setWindowIcon(QIcon("./Icon/KVM.png"))
        self.menu_video_menu.setTitle(_translate("MainWindow", "输入设备"))
        self.menu_settings.setTitle(_translate("MainWindow", "设置"))
        self.action_resolution.setText(_translate("MainWindow", "分辨率设置"))
        self.action_save_path.setText(_translate("MainWindow", "文件保存路径"))
        self.action_screenshot.setText(_translate("MainWindow", "截屏"))

    # 获取视图窗口大小
    def get_viewfinder_size(self):
        return self.centralwidget.width(), self.centralwidget.height()

    # 刷新输入设备列表
    def refresh_input_devices(self):
        self.online_webcams = self.video_handler.refresh_input_devices()
        # 清空菜单项
        self.menu_video_menu.clear()
        # 为每个摄像头创建菜单项
        for i, camera in enumerate(self.online_webcams):
            camera_action = QAction(f"摄像头 {i + 1}: {camera.description()}", self.menu_video_menu)
            camera_action.setIcon(QIcon("./Icon/devices.png"))
            camera_action.triggered.connect(lambda checked, index=i: self.select_camera(index))
            self.menu_video_menu.addAction(camera_action)

    # 选择摄像头
    def select_camera(self, index):
        if self.video_handler.select_camera(index):
            # self.resize_window_func()
            self.update_status_bar(self.video_handler.get_camera_info())
            global camera_started
            camera_started = self.video_handler.is_camera_started()
            self.MainWindow.adjust_viewfinder_size(self.MainWindow.width(), self.MainWindow.height()) #选中相机的时候更新一下窗口、取景器大小以及偏差
        else:
            QMessageBox.critical(self.centralwidget, "错误", "无法选择摄像头", QMessageBox.Ok)

    # 设备配置对话框
    def device_config(self):
        self.device_setup_dialog.comboBox.clear()
        common_resolutions = ["640x480", "800x600", "1024x768", "1280x720", "1920x1080"]  # 通用分辨率列表
        supported_resolutions = []   # 支持的分辨率列表
        try:    # 尝试获取设备支持的分辨率
            camera_info = QCamera(self.video_handler.online_webcams[self.video_handler.camera_config['device_No']])
            camera_info.load()
            resolutions = camera_info.supportedViewfinderResolutions()
            camera_info.unload()
            for resolution in resolutions:
                supported_resolutions.append(f"{resolution.width()}x{resolution.height()}")
        except Exception as e:
            print(f"无法获取设备支持的分辨率: {e}")
        if not supported_resolutions:    # 如果无法获取支持的分辨率，使用通用列表
            print("使用通用分辨率列表")
            supported_resolutions = common_resolutions
        for res in supported_resolutions: # 添加分辨率到comboBox
            self.device_setup_dialog.comboBox.addItem(res)
        current_resolution = f"{self.video_handler.camera_config['resolution_X']}x{self.video_handler.camera_config['resolution_Y']}"       # 设置当前分辨率
        index = self.device_setup_dialog.comboBox.findText(current_resolution) 
        if index >= 0:
            self.device_setup_dialog.comboBox.setCurrentIndex(index)
        elif self.device_setup_dialog.comboBox.count() > 0:
            self.device_setup_dialog.comboBox.setCurrentIndex(0)
        if self.device_setup_dialog.exec() == QDialog.Accepted:          # 显示对话框
            resolution = self.device_setup_dialog.comboBox.currentText().split('x')
            new_resolution_x = int(resolution[0])
            new_resolution_y = int(resolution[1])
            self.video_handler.update_resolution(new_resolution_x, new_resolution_y)
            self.update_status_bar(self.video_handler.get_camera_info())
            self.MainWindow.adjust_viewfinder_size(self.MainWindow.width(), self.MainWindow.height()) # 添加以下行来触发窗口调整


    # 设置保存路径
    def take_screenshot(self):
        result = self.video_handler.take_screenshot()
        if result:
          self.statusbar.showMessage(result, 5000)

    def set_save_path(self):
        result = self.video_handler.set_save_path()
        if result:
            self.statusbar.showMessage(result, 5000)

    # 更新状态栏
    def update_status_bar(self, message, duration=5000):
        self.statusbar.showMessage(message, duration)

    # 清除状态栏
    def clear_status_bar(self):
        self.statusbar.clearMessage()

#主窗口类   
class MainWindow(QMainWindow):
    
    key_event = pyqtSignal(QKeyEvent, bool)

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)    
        # 初始化状态变量
        self.mouse_mode = "absolute"
        self.mouse_locked = False
        self.camera_started = False
        self._init_window()  #初始化窗口    
        self._init_hid_devices() #初始化HID设备
        self._init_handlers() #初始化处理器
        self._init_connections() #初始化信号连接
        self._switch_to_absolute_mode()
        
    def _init_window(self):
        # 居中窗口
        qr = self.frameGeometry()
        cp = QApplication.desktop().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        self.ui.refresh_input_devices()   # 刷新设备列表

    # 初始化HID设备
    def _init_hid_devices(self):
        self.hid_devices = {
            'keyboard': None,
            'mouse_relative': None,
            'mouse_absolute': None
        }
        try:
            self.hid_devices['keyboard'] = open('/dev/hidg0', 'rb+')
            self.hid_devices['mouse_relative'] = open('/dev/hidg1', 'rb+')
            self.hid_devices['mouse_absolute'] = open('/dev/hidg2', 'rb+')
        except Exception as e:
            self.ui.statusbar.showMessage(f"HID设备初始化失败: {e}", 5000)
            logging.error(f"HID设备初始化失败: {e}")

    # 初始化鼠标键盘事件处理
    def _init_handlers(self):
        global keyboard_handler, mouse_handler
        keyboard_handler = KeyboardHandler(self.hid_devices['keyboard'])
        keyboard_handler.key_event.connect(keyboard_handler.handle_key_event)
        mouse_handler = MouseHandler(
            self,
            self.hid_devices['mouse_absolute'],
            self.hid_devices['mouse_relative'],
            self.ui.centralwidget.width(),
            self.ui.centralwidget.height()
        )

    # 初始化信号连接
    def _init_connections(self):
        self.ui.action_mouse_absolute.triggered.connect(self.switch_mouse_mode)        # 鼠标模式切换
        self.ui.action_mouse_relative.triggered.connect(self.switch_mouse_mode)

        self.ui.action_keyboard_US.triggered.connect(lambda: self._switch_keyboard_layout('US')) #键盘布局切换
        self.ui.action_keyboard_UK.triggered.connect(lambda: self._switch_keyboard_layout('UK'))

        def connect_shortcut(action):        # 快捷键菜单
            shortcut_text = action.text()
            action.triggered.connect(lambda: self.handle_shortcut(shortcut_text))
        for action in self.ui.menu_shortcut_key.actions():         # 为每个动作创建连接
            connect_shortcut(action)
        self.ui.action_paste.triggered.connect(self.paste_to_controlled_machine)      # 粘贴动作


        #自定义快捷键
        self.custom_shortcut_dialog = CustomShortcutDialog(self)
        self.ui.custom_shortcut.triggered.connect(self.custom_shortcut_dialog.show)
        self.custom_shortcut_dialog.shortcut_created.connect(self.handle_shortcut)


  


    # 切换键盘布局
    def _switch_keyboard_layout(self, layout):
        if keyboard_handler:
            keyboard_handler.set_keyboard_layout(layout)
            self.ui.statusbar.showMessage(f"键盘布局已切换为: {layout}", 3000)
            # 可以在这里添加保存布局设置的代码
            if hasattr(self, 'settings'):
                self.settings.setValue("keyboard_layout", layout)

    # 鼠标模式相关方法
    def switch_mouse_mode(self):
        if self.ui.action_mouse_absolute.isChecked():
            self._switch_to_absolute_mode()
        else:
            self._switch_to_relative_mode()
        keyboard_handler._reset_keyboard_state()

    # 切换到绝对模式
    def _switch_to_absolute_mode(self):
        self.mouse_mode = "absolute"
        mouse_handler.set_mode(self.mouse_mode)
        self.mouse_locked = False
        self.setMouseTracking(True)     # 鼠标追踪
        self.ui.centralwidget.setMouseTracking(True)
        self.releaseMouse()#释放鼠标
        self.unsetCursor()#释放光标
        self._show_status_message("鼠标模式：绝对模式", 3000)

    # 切换到相对模式
    def _switch_to_relative_mode(self):
        self.mouse_mode = "relative"
        mouse_handler.set_mode(self.mouse_mode)
        self.setMouseTracking(True)     # 鼠标追踪
        self.ui.centralwidget.setMouseTracking(True)
        self.mouse_locked = True
        self.centerMouse()
        self._show_status_message("鼠标模式：相对模式已启用。按 Ctrl+Alt+F2 退出相对模式。", 10000)

    # 将鼠标居中
    def centerMouse(self):
        center = self.ui.centralwidget.rect().center()
        global_center = self.ui.centralwidget.mapToGlobal(center)
        QCursor.setPos(global_center)

    # 统一处理所有鼠标输入事件的方法
    def _handle_input_event(self, event_type, event):
        self.camera_started = self.ui.video_handler.is_camera_started()
        if not self.camera_started:
            return
            
        # 在相对模式下，如果鼠标未锁定且点击了取景器，重新进入相对模式
        if (event_type == 'press' and 
            self.mouse_mode == "relative" and 
            not self.mouse_locked and 
            self.ui.centralwidget.underMouse()):
            self._switch_to_relative_mode()
            return
            
        #使用字典来存储事件类型和对应的处理方法
        event_handlers = {
            'press': mouse_handler.mousePressEvent,
            'release': mouse_handler.mouseReleaseEvent,
            'wheel': mouse_handler.wheelEvent,
            'move': mouse_handler.mouseMoveEvent
        }
        
        if event_type in event_handlers:
            event_handlers[event_type](event)
    # 鼠标事件
    def mousePressEvent(self, event): self._handle_input_event('press', event)
    def mouseReleaseEvent(self, event): self._handle_input_event('release', event)
    def wheelEvent(self, event): self._handle_input_event('wheel', event)
    def mouseMoveEvent(self, event): self._handle_input_event('move', event)

    # 键盘事件
    def keyPressEvent(self, event):
        if not self.ui.video_handler.is_camera_started():
            return super().keyPressEvent(event)
            
        if self.mouse_locked or self.ui.centralwidget.underMouse():
            if self._is_mode_switch_combo(event):
                # self.ui.action_mouse_absolute.trigger()
                self.mouse_locked = False
                self.releaseMouse()#释放鼠标
                self.unsetCursor()#释放光标
                self.setMouseTracking(False)
                self.ui.centralwidget.setMouseTracking(False)
            else:
                keyboard_handler.handle_key_event(event, True)
                self.update_key_status()
        else:
            super().keyPressEvent(event)

    # 键盘释放事件
    def keyReleaseEvent(self, event):
        if not self.ui.video_handler.is_camera_started():
            return super().keyReleaseEvent(event)
        if self.ui.centralwidget.underMouse():
            keyboard_handler.handle_key_event(event, False)
            self.update_key_status()
        else:
            super().keyReleaseEvent(event)

    # 检查是否是模式切换组合键
    def _is_mode_switch_combo(self, event):
        return (event.key() == Qt.Key_F12 and 
                event.modifiers() == (Qt.ShiftModifier | Qt.AltModifier))
    
    # 处理快捷键事件
    def handle_shortcut(self, shortcut: str):
        if not self.ui.video_handler.is_camera_started():
            self._show_status_message("摄像头未启动，无法发送快捷键", 3000)
            return
        if self.hid_devices['keyboard']:
            keyboard_handler.send_shortcut(shortcut)
            self._show_status_message(f"已发送快捷键: {shortcut}", 3000)
        else:
            self._show_status_message("HID设备未就绪，无法发送快捷键", 3000)

    # 状态更新方法
    def update_key_status(self):
        if not self.ui.video_handler.is_camera_started():
            return self.ui.statusbar.clearMessage()
        if self.ui.centralwidget.underMouse():
            key_status = keyboard_handler.get_key_status()
            self._show_status_message(key_status if key_status else None)
        else:
            self.ui.statusbar.clearMessage()

    # 显示状态栏消息
    def _show_status_message(self, message, timeout=0):
        if message:
            self.ui.statusbar.showMessage(message, timeout)
        else:
            self.ui.statusbar.clearMessage()

    # 剪贴板相关方法
    def paste_to_controlled_machine(self):
        text = QApplication.clipboard().text()
        if not text:
            return QMessageBox.warning(self.ui.centralwidget, 
                                     "警告", "剪贴板中没有文本", 
                                     QMessageBox.Ok)
        self.send_text_to_device(text)
        
    # 发送文本到设备
    def send_text_to_device(self, text):
        if not (self.ui.video_handler.is_camera_started() and 
                self.hid_devices['keyboard']):
            return self._show_status_message("HID设备未就绪，无法发送文本", 3000)
            
        for char in text:
            keyboard_handler.send_character(char)
        self._show_status_message("文本已发送", 3000)

       # 窗口调整相关方法
    def resizeEvent(self, event):
        super().resizeEvent(event)
        # 添加短暂延迟以确保窗口尺寸已稳定
        QtCore.QTimer.singleShot(10, lambda: self.adjust_viewfinder_size(self.width(), self.height()))

    # 窗口状态改变事件
    def changeEvent(self, event):
        if event.type() == QtCore.QEvent.WindowStateChange:
            # 添加短暂延迟以确保窗口状态已完全改变
            QtCore.QTimer.singleShot(10, lambda: self.adjust_viewfinder_size(self.width(), self.height()))
        super().changeEvent(event)

    # 调整取景器大小
    def adjust_viewfinder_size(self, window_width, window_height):
        if not self._can_adjust_viewfinder():
            return
        camera_config = self.ui.video_handler.get_camera_config()
        # 通过ui访问菜单栏和状态栏
        menu_height = self.ui.menubar.height()
        status_height = self.ui.statusbar.height()
        # 计算实际可用区域
        available_height = window_height - menu_height - status_height
        
        new_size = self._calculate_viewfinder_size(
            window_width, 
            available_height,
            camera_config['resolution_X'],
            camera_config['resolution_Y']
        )
        # 调整y偏移，只需要考虑菜单栏的高度
        width, height, x_offset, y_offset = new_size
        y_offset += menu_height
        self._apply_viewfinder_size(width, height, x_offset, y_offset)
        mouse_handler.update_viewport(width, height, x_offset, y_offset)
        self.update()

    # 检查是否可以调整取景器
    def _can_adjust_viewfinder(self):
        return (self.ui.video_handler.is_camera_started() and 
                self.ui.video_handler.get_camera_config())

    # 计算取景器尺寸
    def _calculate_viewfinder_size(self, window_w, window_h, camera_w, camera_h):
        # 使用浮点数计算以提高精度
        scale = min(window_w / float(camera_w), window_h / float(camera_h))
        new_w = int(camera_w * scale)
        new_h = int(camera_h * scale)
        # 确保尺寸不为0
        new_w = max(1, new_w)
        new_h = max(1, new_h)
        # 计算居中偏移
        x_offset = (window_w - new_w) // 2
        y_offset = (window_h - new_h) // 2
        return new_w, new_h, x_offset, y_offset
    
    # 应用取景器尺寸
    def _apply_viewfinder_size(self, width, height, x_offset, y_offset):
        self.ui.centralwidget.resize(width, height)
        self.ui.centralwidget.move(x_offset, y_offset)
        logging.info(f"窗口大小: {self.width()}x{self.height()}")
        logging.info(f"菜单栏高度: {self.ui.menubar.height()}")
        logging.info(f"状态栏高度: {self.ui.statusbar.height()}")
        logging.info(f"取景器大小: {width}x{height}")
        logging.info(f"取景器位置: ({x_offset}, {y_offset})")

    # 清理方法
    def closeEvent(self, event):
        self.ui.video_handler.set_webcam(False)
        self._close_hid_devices()
        super().closeEvent(event)

    #关闭hid设备
    def _close_hid_devices(self):
        for device_name, device in self.hid_devices.items():
            if device:
                logging.info(f"正在关闭HID设备: {device_name}")
                device.close()
            else:
                logging.info(f"HID设备 {device_name} 已经关闭或未初始化")
        self.hid_devices = {k: None for k in self.hid_devices}
        logging.info("所有HID设备已关闭")
# 主程序入口
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())






