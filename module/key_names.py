from PyQt5.QtCore import Qt

# 修饰键名称
MODIFIER_NAMES = {
    Qt.Key_Control: "Ctrl",
    Qt.Key_Shift: "Shift",
    Qt.Key_Alt: "Alt",
    Qt.Key_Meta: "Meta"
}

# 特殊键名称
SPECIAL_KEYS = {
    Qt.Key_Space: "Space",
    Qt.Key_Return: "Enter",
    Qt.Key_Escape: "Esc",
    Qt.Key_Tab: "Tab",
    Qt.Key_Backspace: "Backspace",
    Qt.Key_Delete: "Delete",
    Qt.Key_Left: "Left",
    Qt.Key_Right: "Right",
    Qt.Key_Up: "Up",
    Qt.Key_Down: "Down",
    Qt.Key_Home: "Home",
    Qt.Key_End: "End",
    Qt.Key_PageUp: "PageUp",
    Qt.Key_PageDown: "PageDown",
    Qt.Key_Insert: "Insert",
    Qt.Key_F1: "F1",
    Qt.Key_F2: "F2",
    Qt.Key_F3: "F3",
    Qt.Key_F4: "F4",
    Qt.Key_F5: "F5",
    Qt.Key_F6: "F6",
    Qt.Key_F7: "F7",
    Qt.Key_F8: "F8",
    Qt.Key_F9: "F9",
    Qt.Key_F10: "F10",
    Qt.Key_F11: "F11",
    Qt.Key_F12: "F12",
    Qt.Key_CapsLock: "CapsLock",
    Qt.Key_NumLock: "NumLock",
    Qt.Key_ScrollLock: "ScrollLock",
    Qt.Key_Print: "PrintScreen",
    Qt.Key_Pause: "Pause",
    Qt.Key_Menu: "Menu"
}