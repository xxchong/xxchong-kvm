from PyQt5.QtCore import Qt
from typing import Dict, Any

# 基础字母键映射
BASE_KEYS = {
    Qt.Key_A: 0x04, Qt.Key_B: 0x05, Qt.Key_C: 0x06, Qt.Key_D: 0x07,
    Qt.Key_E: 0x08, Qt.Key_F: 0x09, Qt.Key_G: 0x0A, Qt.Key_H: 0x0B,
    Qt.Key_I: 0x0C, Qt.Key_J: 0x0D, Qt.Key_K: 0x0E, Qt.Key_L: 0x0F,
    Qt.Key_M: 0x10, Qt.Key_N: 0x11, Qt.Key_O: 0x12, Qt.Key_P: 0x13,
    Qt.Key_Q: 0x14, Qt.Key_R: 0x15, Qt.Key_S: 0x16, Qt.Key_T: 0x17,
    Qt.Key_U: 0x18, Qt.Key_V: 0x19, Qt.Key_W: 0x1A, Qt.Key_X: 0x1B,
    Qt.Key_Y: 0x1C, Qt.Key_Z: 0x1D,
}

# US布局特定映射
LAYOUT_SPECIFIC = {
    Qt.Key_Minus: 0x2D,        # -
    Qt.Key_Equal: 0x2E,        # =
    Qt.Key_BracketLeft: 0x2F,  # [
    Qt.Key_BracketRight: 0x30, # ]
    Qt.Key_Backslash: 0x31,    # \
    Qt.Key_Semicolon: 0x33,    # ;
    Qt.Key_Apostrophe: 0x34,   # '
    Qt.Key_QuoteLeft: 0x35,    # `
    Qt.Key_Comma: 0x36,        # ,
    Qt.Key_Period: 0x37,       # .
    Qt.Key_Slash: 0x38,        # /
}

# US布局的Shift字符映射
SHIFT_CHARS = {
    '!': 0x1E, '@': 0x1F, '#': 0x20, '$': 0x21, '%': 0x22,
    '^': 0x23, '&': 0x24, '*': 0x25, '(': 0x26, ')': 0x27,
    '_': 0x2D, '+': 0x2E, '{': 0x2F, '}': 0x30, '|': 0x31,
    ':': 0x33, '"': 0x34, '~': 0x35, '<': 0x36, '>': 0x37,
    '?': 0x38
}

# 其他通用映射（与布局无关）
NUMBER_KEYS = {
    Qt.Key_1: 0x1E, Qt.Key_2: 0x1F, Qt.Key_3: 0x20, Qt.Key_4: 0x21,
    Qt.Key_5: 0x22, Qt.Key_6: 0x23, Qt.Key_7: 0x24, Qt.Key_8: 0x25,
    Qt.Key_9: 0x26, Qt.Key_0: 0x27,
}

FUNCTION_KEYS = {
    Qt.Key_F1: 0x3A, Qt.Key_F2: 0x3B, Qt.Key_F3: 0x3C, Qt.Key_F4: 0x3D,
    Qt.Key_F5: 0x3E, Qt.Key_F6: 0x3F, Qt.Key_F7: 0x40, Qt.Key_F8: 0x41,
    Qt.Key_F9: 0x42, Qt.Key_F10: 0x43, Qt.Key_F11: 0x44, Qt.Key_F12: 0x45,
}

CONTROL_KEYS = {
    Qt.Key_Return: 0x28, Qt.Key_Escape: 0x29, Qt.Key_Backspace: 0x2A,
    Qt.Key_Tab: 0x2B, Qt.Key_Space: 0x2C, Qt.Key_CapsLock: 0x39,
    Qt.Key_Print: 0x46, Qt.Key_ScrollLock: 0x47, Qt.Key_Pause: 0x48,
    Qt.Key_Insert: 0x49, Qt.Key_Home: 0x4A, Qt.Key_PageUp: 0x4B,
    Qt.Key_Delete: 0x4C, Qt.Key_End: 0x4D, Qt.Key_PageDown: 0x4E,
    Qt.Key_NumLock: 0x53,
}

ARROW_KEYS = {
    Qt.Key_Right: 0x4F, Qt.Key_Left: 0x50, Qt.Key_Down: 0x51, Qt.Key_Up: 0x52,
}

MODIFIER_KEYS = {
    Qt.Key_Control: 0x01, Qt.Key_Shift: 0x02,
    Qt.Key_Alt: 0x04, Qt.Key_Meta: 0x08,
}

def merge_mappings(*args):
    """合并多个映射字典"""
    result = {}
    for mapping in args:
        result.update(mapping)
    return result

def create_us_mappings() -> Dict[str, Any]:
    """创建US键盘映射"""
    standard = merge_mappings(BASE_KEYS, NUMBER_KEYS, FUNCTION_KEYS, 
                            CONTROL_KEYS, ARROW_KEYS, LAYOUT_SPECIFIC)
    
    chars = {chr(k).lower(): v for k, v in BASE_KEYS.items()}
    chars.update({str(k)[-1]: v for k, v in NUMBER_KEYS.items()})
    chars.update({' ': 0x2C, '\n': 0x28})

    return {
        'standard': standard,
        'modifiers': MODIFIER_KEYS,
        'chars': chars,
        'shift_chars': SHIFT_CHARS,
    }

US_MAPPINGS = create_us_mappings()