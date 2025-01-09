from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QKeyEvent
import struct
from collections import OrderedDict
import time
import logging
from typing import Optional, List, Tuple

from module.us_keyboard_mappings import US_MAPPINGS
from module.uk_keyboard_mappings import UK_MAPPINGS
from .key_names import MODIFIER_NAMES, SPECIAL_KEYS

class KeyboardHandler(QObject):
    key_event = pyqtSignal(QKeyEvent, bool)  # True for press, False for release

    def __init__(self, hid_keyboard):
        super().__init__()
        self.hid_keyboard = hid_keyboard
        self.current_layout = 'US'  # 默认US布局
        self.current_modifiers = 0  # 跟踪当前按下的修饰键
        self.current_mappings = US_MAPPINGS  # 默认使用US映射
        self.pressed_keys = OrderedDict()  # 跟踪当前按下的普通键
        self.logger = logging.getLogger(__name__)
        self._reset_hid_device()

    def _reset_keyboard_state(self):
        """重置键盘状态"""
        self.current_modifiers = 0
        self.pressed_keys.clear()
        self._reset_hid_device()
        self.logger.info("键盘状态已完全重置")

    def set_keyboard_layout(self, layout: str) -> None:
        """设置键盘布局"""
        if layout == 'US':
            self.current_mappings = US_MAPPINGS
            self.current_layout = layout
        elif layout == 'UK':
            self.current_mappings = UK_MAPPINGS
            self.current_layout = layout
        else:
            self.logger.warning(f"不支持的键盘布局: {layout}")
            return
        
        self.logger.info(f"键盘布局已切换为: {layout}")
        self._reset_keyboard_state()

    def get_current_layout(self) -> str:
        """获取当前布局"""
        return self.current_layout

    def _get_key_mapping(self, key: int) -> Optional[int]:
        """获取键的映射"""
        return self.current_mappings['standard'].get(key)

    def _reset_hid_device(self) -> None:
        """重置HID设备"""
        try:
            if self.hid_keyboard:
                empty_report = struct.pack('BBBBBBBB', 0, 0, 0, 0, 0, 0, 0, 0)
                self._send_report(empty_report)
                self.logger.debug("HID设备已重置")
        except Exception as e:
            self.logger.error(f"重置HID设备失败: {e}")

    def _send_report(self, report: bytes) -> bool:
        """发送HID报告"""
        try:
            if self.hid_keyboard:
                self.hid_keyboard.write(report)
                self.hid_keyboard.flush()
                self.logger.debug(f"HID报告已发送: {report.hex()}")
                return True
        except Exception as e:
            self.logger.error(f"发送HID报告失败: {e}")
        return False

    def handle_key_event(self, event: QKeyEvent, is_press: bool) -> None:
        """处理键盘事件并发送HID报告"""
        if not self.hid_keyboard:
            return
        try:
            key = event.key()
            if key in self.current_mappings['modifiers']:
                self._handle_modifier_key(key, is_press)
            else:
                self._handle_regular_key(event, is_press)
            self.send_hid_report()
        except Exception as e:
            self.logger.error(f"处理键盘事件时出错: {e}")
            self._reset_hid_device()

    def _handle_modifier_key(self, key: int, is_press: bool) -> None:
        """处理修饰键"""
        if is_press:
            self.current_modifiers |= self.current_mappings['modifiers'][key]
        else:
            self.current_modifiers &= ~self.current_mappings['modifiers'][key]

    def _handle_regular_key(self, event: QKeyEvent, is_press: bool) -> None:
        """处理普通键"""
        key = event.key()
        text = event.text()
        if is_press:
            key_code = self._get_key_mapping(key) or self.current_mappings['shift_chars'].get(text)
            if key_code:
                self.pressed_keys[key] = key_code
                self.logger.debug(f"Key {key} ({text}) pressed. Pressed keys: {list(self.pressed_keys.keys())}")
        else:
            if key in self.pressed_keys:
                del self.pressed_keys[key]
                self.logger.debug(f"Key {key} ({text}) released. Remaining keys: {list(self.pressed_keys.keys())}")

    def send_hid_report(self) -> None:
        """发送HID报告"""
        self.logger.debug(f"Sending HID report. Modifiers: {bin(self.current_modifiers)}, Keys: {list(self.pressed_keys.values())}")

        if not self.hid_keyboard:
            return
        try:
            if len(self.pressed_keys) > 6:
                self.logger.warning("检测到超过6个按键，执行重置")
                self._reset_hid_device()
                return

            keys = list(self.pressed_keys.values())[:6]  # 获取当前按下的普通键的键码，最多6个
            keys.extend([0] * (6 - len(keys)))  # 如果按键数量不足6个，则用0填充
            report = struct.pack('BBBBBBBB', self.current_modifiers, 0, *keys)

            if any(k > 0xFF for k in keys) or self.current_modifiers > 0xFF:
                self.logger.warning("检测到无效的键值，执行重置")
                self._reset_hid_device()
                return
            self._send_report(report)
        except Exception as e:
            self.logger.error(f"发送HID报告失败: {e}")
            self._reset_hid_device()

    def get_key_status(self) -> str:
        """获取当前按键状态"""
        if not self.pressed_keys and not self.current_modifiers:
            return ""

        try:
            key_names = []
            for qt_key, modifier in self.current_mappings['modifiers'].items():
                if self.current_modifiers & modifier:
                    if qt_key in MODIFIER_NAMES:
                        key_names.append(MODIFIER_NAMES[qt_key])

            for key in self.pressed_keys:
                if key in SPECIAL_KEYS:
                    key_names.append(SPECIAL_KEYS[key])
                elif 32 <= key <= 126:
                    key_names.append(chr(key))
                else:
                    key_text = chr(key).upper() if 65 <= key <= 90 else f"Key_{key}"
                    key_names.append(key_text)

            return " + ".join(key_names) + " 键被按下" if key_names else ""
        except Exception as e:
            self.logger.error(f"获取按键状态时出错: {e}")
            return "按键状态获取失败"

    def send_shortcut(self, shortcut: str) -> None:
        """发送快捷键"""
        if not self.hid_keyboard:
            return
        try:
            modifier, key_codes = self._parse_shortcut(shortcut)
            if key_codes:
                self._send_shortcut_sequence(modifier, key_codes)
        except Exception as e:
            self.logger.error(f"发送快捷键'{shortcut}'失败: {e}")

    def _parse_shortcut(self, shortcut: str) -> Tuple[int, List[int]]:
        """解析快捷键"""
        modifier = 0
        key_codes = []

        modifier_map = {
            'ctrl': Qt.Key_Control,
            'control': Qt.Key_Control,
            'shift': Qt.Key_Shift,
            'alt': Qt.Key_Alt,
            'meta': Qt.Key_Meta
        }

        special_keys = {
            'esc': Qt.Key_Escape,
            'escape': Qt.Key_Escape,
            'tab': Qt.Key_Tab,
            'enter': Qt.Key_Return,
            'return': Qt.Key_Return,
            'backspace': Qt.Key_Backspace,
            'delete': Qt.Key_Delete,
            'del': Qt.Key_Delete,
            'space': Qt.Key_Space,
        }

        keys = shortcut.lower().split('+')
        for key in keys:
            key = key.strip()
            if key in modifier_map:
                modifier |= self.current_mappings['modifiers'][modifier_map[key]]
            elif key in special_keys:
                key_code = self.current_mappings['standard'].get(special_keys[key])
                if key_code:
                    key_codes.append(key_code)
            else:
                key_enum = getattr(Qt, f'Key_{key.capitalize()}', None)
                if key_enum and key_enum in self.current_mappings['standard']:
                    key_codes.append(self.current_mappings['standard'][key_enum])
                else:
                    self.logger.warning(f"未识别的键: {key}")

        # 如果没有 '+' 分隔符且字符串直接是修饰键之一
        if len(keys) == 1 and keys[0] in modifier_map:
            modifier |= self.current_mappings['modifiers'][modifier_map[keys[0]]]

        return modifier, key_codes

    def get_key_code(self, key: str) -> Optional[int]:
        """获取键码"""
        key = key.lower()
        if key == 'esc':
            return self.current_mappings['standard'][Qt.Key_Escape]
        key_enum = getattr(Qt, f'Key_{key.capitalize()}', None)
        if key_enum is not None and key_enum in self.current_mappings['standard']:
            return self.current_mappings['standard'][key_enum]
        self.logger.warning(f"未找到键码: {key}")
        return None

    def send_hid_report_raw(self, modifier: int, key_codes: List[int]) -> None:
        """发送原始HID报告"""
        if not self.hid_keyboard:
            return

        try:
            keys = key_codes[:6]
            keys.extend([0] * (6 - len(keys)))
            report = struct.pack('BBBBBBBB', modifier, 0, *keys)
            self._send_report(report)
        except Exception as e:
            self.logger.error(f"发送原始HID报告失败: {e}")

    def send_character(self, char: str) -> None:
        """发送字符"""
        try:
            report = self._create_char_report(char)
            if report:
                self._send_report(report)
                time.sleep(0.05)
                self.release_keys()
        except Exception as e:
            self.logger.error(f"发送字符'{char}'失败: {e}")

    def _create_char_report(self, char: str) -> Optional[bytes]:
        """创建字符报告"""
        if char in self.current_mappings['shift_chars']:
            return struct.pack('BBBBBBBB', 0x02, 0, 
                             self.current_mappings['shift_chars'][char], 0, 0, 0, 0, 0)
        elif char in self.current_mappings['chars']:
            return struct.pack('BBBBBBBB', 0x00, 0, 
                             self.current_mappings['chars'][char], 0, 0, 0, 0, 0)
        return None

    def release_keys(self) -> None:
        """释放所有按键"""
        empty_report = struct.pack('BBBBBBBB', 0, 0, 0, 0, 0, 0, 0, 0)
        self._send_report(empty_report)

    def _send_shortcut_sequence(self, modifier: int, key_codes: List[int]) -> None:
        """发送快捷键序列"""
        self.send_hid_report_raw(modifier, key_codes)
        time.sleep(0.1)
        self.send_hid_report_raw(0, [])
        time.sleep(0.2)