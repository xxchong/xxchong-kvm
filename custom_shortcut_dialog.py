from PyQt5.QtWidgets import QDialog, QPushButton, QGridLayout, QLineEdit
from PyQt5.QtCore import pyqtSignal

class CustomShortcutDialog(QDialog):
    shortcut_created = pyqtSignal(str)  # 创建一个信号，用于发送快捷键字符串

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("自定义快捷键")
        self.resize(400, 200)  # 增加窗口宽度
        layout = QGridLayout(self)  # 使用网格布局

        # 创建按钮并添加到布局中
        self.keys = {'Ctrl': False, 'Shift': False, 'Alt': False, 'Meta': False}
        self.operation_keys = {'Tab': False, 'Prt Sc': False}  # 操作键
        self.buttons = {}
        row = 0
        for key in self.keys:
            btn = QPushButton(key, self)
            btn.setCheckable(True)
            btn.toggled.connect(lambda checked, key=key: self.toggle_key(key, checked))
            layout.addWidget(btn, 0, row)  # 特殊键在第一行
            self.buttons[key] = btn
            row += 1

        row = 0
        for key in self.operation_keys:
            btn = QPushButton(key, self)
            btn.setCheckable(True)
            btn.toggled.connect(lambda checked, key=key: self.toggle_key(key, checked))
            layout.addWidget(btn, 1, row)  # 操作键在第二行
            self.buttons[key] = btn
            row += 1

        # 添加文本输入框以允许用户输入自定义快捷键
        self.custom_input = QLineEdit(self)
        layout.addWidget(self.custom_input, 2, 0, 1, 4)  # 跨四列

        # 添加按钮
        self.clear_button = QPushButton("清除", self)
        self.clear_button.clicked.connect(self.clear_inputs)
        layout.addWidget(self.clear_button, 3, 0)

        self.send_button = QPushButton("发送", self)
        self.send_button.clicked.connect(self.send_shortcut)
        layout.addWidget(self.send_button, 3, 1)

        self.close_button = QPushButton("关闭", self)
        self.close_button.clicked.connect(self.close)
        layout.addWidget(self.close_button, 3, 2)

    def toggle_key(self, key, checked):
        if key in self.keys:
            self.keys[key] = checked
        elif key in self.operation_keys:
            self.operation_keys[key] = checked

    def clear_inputs(self):
        # 清除所有键的选中状态和文本框内容
        for key in self.keys:
            self.keys[key] = False
            self.buttons[key].setChecked(False)
        for key in self.operation_keys:
            self.operation_keys[key] = False
            self.buttons[key].setChecked(False)
        self.custom_input.clear()

    def send_shortcut(self):
        # 从选中的键和文本框中创建快捷键字符串
        shortcut = '+'.join([k for k, v in self.keys.items() if v] + [k for k, v in self.operation_keys.items() if v])
        if self.custom_input.text():
            shortcut += '+' + self.custom_input.text()
        self.shortcut_created.emit(shortcut)  # 发送快捷键字符串

    def create_shortcut(self):
        # 这个方法现在可以删除或保留为空，因为发送按钮已经处理了快捷键的创建和发送
        pass