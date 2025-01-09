from PyQt5.QtCore import QObject, Qt, QEvent, QPoint
from PyQt5.QtGui import QCursor
import struct
import logging
from time import time

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class MouseHandler(QObject):
    def __init__(self, parent, hid_mouse_absolute, hid_mouse_relative, screen_width, screen_height):
        super().__init__(parent)
        self.parent_window = parent  # 保存对主窗口的引用
        self.hid_mouse_absolute = hid_mouse_absolute
        self.hid_mouse_relative = hid_mouse_relative
        self.status = {'mouse_capture': True}
        self.button_state = 0   #按键的状态值
        self.mode = 'absolute'  # 默认为绝对模式
        self.last_x = screen_width // 2
        self.last_y = screen_height // 2
        self.viewport_width = screen_width  # 初始取景器宽度
        self.viewport_height = screen_height  # 初始取景器高度
        self.viewport_x_offset = 0 # 取景器的水平偏移
        self.viewport_y_offset = 0  # 取景器的垂直偏移
        self.relative_mode_margin = 50  # 添加边距阈值
        self.last_send_time = time()  # 添加上次发送时间记录
        self.min_movement_threshold = 5  # 最小移动距离阈值
        self.min_send_interval = 0.05  # 最小发送时间间隔(60ms)

        self._reset_hid_devices() # 初始化时重置HID设备，防止混乱的数据

    def _reset_hid_devices(self):
        logger.info("正在初始化重置HID鼠标设备")
        self.button_state = 0

        try:
            # 重置绝对模式设备
            if self.hid_mouse_absolute:
                absolute_report = struct.pack('<BHHHH', 0, 16383, 16383, 0, 0)  # 重置到屏幕中央
                self.send_hid_report(absolute_report, absolute=True)
            # 重置相对模式设备
            if self.hid_mouse_relative:
                relative_report = struct.pack('<BBBBB', 0, 0, 0, 0, 0)  # 所有值置零
                self.send_hid_report(relative_report, absolute=False)
            logger.info("HID鼠标设备重置完成")
        except Exception as e:
            logger.error(f"重置HID鼠标设备时出错: {e}")

    def update_viewport(self, viewport_width, viewport_height, x_offset, y_offset):
        """更新视口信息并重置鼠标位置"""
        self.viewport_width = max(1, viewport_width)  # 避免除以零
        self.viewport_height = max(1, viewport_height)
        self.viewport_x_offset = x_offset
        self.viewport_y_offset = y_offset
        
        # 在视口更新后重置鼠标位置到中心
        if self.mode == 'absolute':
            center_x = self.viewport_width // 2
            center_y = self.viewport_height // 2
            self._send_absolute(center_x + x_offset, center_y + y_offset)
        
        logger.info(f"取景器尺寸已更新: {viewport_width}x{viewport_height}")
        logger.info(f"取景器偏移已更新: x={x_offset}, y={y_offset}")

    def set_mode(self, mode):
        if mode in ['absolute', 'relative']:
            self.mode = mode
            self._reset_hid_devices()
            logger.info(f"鼠标模式已切换为: {mode}")
            if mode == 'relative':
                # 隐藏全局光标
                print("隐藏全局光标")
                self.parent().setCursor(Qt.BlankCursor)
        else:
            logger.error(f"无效的鼠标模式: {mode}")

    def mousePressEvent(self, event):
        logger.debug(f"鼠标按下事件: 按钮 = {event.button()}")
        if not self.status['mouse_capture']:
            return
        # 更新按钮状态
        if event.button() == Qt.LeftButton:
            self.button_state |= 1
            self.update_status_bar("左键按下")
        elif event.button() == Qt.RightButton:
            self.button_state |= 2
            self.update_status_bar("右键按下")
        elif event.button() == Qt.MidButton:
            self.button_state |= 4
            self.update_status_bar("中键按下")
        
        if self.mode == 'absolute':
            self._send_absolute(event.pos().x(), event.pos().y())
        else:
            self._send_relative(event.pos().x(), event.pos().y(), force_send=True)

    def mouseReleaseEvent(self, event):
        logger.debug(f"鼠标释放事件: 按钮 = {event.button()}")
        if not self.status['mouse_capture']:
            return
            
        # 更新按钮状态
        if event.button() == Qt.LeftButton:
            self.button_state &= ~1
            self.update_status_bar(None)
        elif event.button() == Qt.RightButton:
            self.button_state &= ~2
            self.update_status_bar(None)
        elif event.button() == Qt.MidButton:
            self.button_state &= ~4
            self.update_status_bar(None)
        
        if self.mode == 'absolute':
            self._send_absolute(event.pos().x(), event.pos().y())
        else:
            self._send_relative(event.pos().x(), event.pos().y(), force_send=True)

    def mouseMoveEvent(self, event):
        if not self.status['mouse_capture']:
            return
        if self.mode == 'absolute':
            self._send_absolute(event.pos().x(), event.pos().y())
        else:
            self._send_relative(event.pos().x(), event.pos().y())

    def update_status_bar(self, message):
        """更新状态栏显示"""
        if hasattr(self.parent_window, 'ui'):
            if message:
                self.parent_window.ui.statusbar.showMessage(f"鼠标状态: {message}")
            else:
                self.parent_window.ui.statusbar.clearMessage()

    def _send_absolute(self, x, y):
        # 调整x和y坐标，考虑取景器的偏移和实际显示区域
        x_adjusted = x - self.viewport_x_offset
        y_adjusted = y - self.viewport_y_offset

        # 确保坐标在取景器范围内
        if 0 <= x_adjusted < self.viewport_width and 0 <= y_adjusted < self.viewport_height:
            # 使用浮点数计算以提高精度
            x_hid = int((32767.0 * x_adjusted) / self.viewport_width)
            y_hid = int((32767.0 * y_adjusted) / self.viewport_height)
            
            # 确保值在有效范围内
            x_hid = max(0, min(32767, x_hid))
            y_hid = max(0, min(32767, y_hid))
            
            report = struct.pack('<BHHHH', self.button_state, x_hid, y_hid, 0, 0)
            self.send_hid_report(report, absolute=True)
            logger.debug(f"发送绝对坐标: 原始({x}, {y}) -> 调整后({x_adjusted}, {y_adjusted}) -> HID({x_hid}, {y_hid})")

    def _send_relative(self, x, y, force_send=False):
        # 计算相对移动
        dx = x - self.last_x
        dy = y - self.last_y
        
        current_time = time()
        time_elapsed = current_time - self.last_send_time
        movement_distance = (dx * dx + dy * dy) ** 0.5  # 计算移动距离
        
        # 检查是否需要发送数据（距离优先，时间次之）
        should_send = (force_send or  # 强制发送（用于按键事件）
                      movement_distance >= self.min_movement_threshold or 
                      (movement_distance > 0 and time_elapsed >= self.min_send_interval))
        
        # 检查是否接近窗口边缘
        near_edge = False
        if (x < self.relative_mode_margin or 
            x > self.viewport_width - self.relative_mode_margin or 
            y < self.relative_mode_margin or 
            y > self.viewport_height - self.relative_mode_margin):
            near_edge = True
            should_send = True  # 靠近边缘时强制发送
        
        if should_send:
            # 如果接近边缘，重置鼠标位置到中心
            if near_edge:
                center_x = self.viewport_width // 2
                center_y = self.viewport_height // 2
                self.parent_window.cursor().setPos(
                    self.parent_window.mapToGlobal(QPoint(center_x, center_y))
                )
                self.last_x = center_x
                self.last_y = center_y
            else:
                self.last_x, self.last_y = x, y
            
            # 限制移动范围在-127到127之间
            dx = max(-127, min(127, dx))
            dy = max(-127, min(127, dy))
            
            # 发送相对移动报告
            report = struct.pack('<BBBBB', self.button_state, dx & 0xFF, dy & 0xFF, 0, 0)
            self.send_hid_report(report, absolute=False)
            self.last_send_time = current_time  # 更新发送时间
            
            logger.debug(f"发送相对移动: dx={dx}, dy={dy}, 距离={movement_distance:.2f}, 间隔={time_elapsed*1000:.0f}ms")

    def send_hid_report(self, report, absolute):
        logger.info(f"准备发送HID报告: {report.hex()}")
        if absolute:
            hid_device = self.hid_mouse_absolute
        else:
            hid_device = self.hid_mouse_relative

        if hid_device:
            try:
                bytes_written = hid_device.write(report)
                if bytes_written != len(report):
                    logger.warning(f"未能完全发送报告。已发送 {bytes_written} 字节，总共 {len(report)} 字节")
                hid_device.flush()
                logger.info("HID报告发送成功")
            except IOError as e:
                logger.error(f"发送HID报告时出错: {e}")
                if e.errno == 108:  # Cannot send after transport endpoint shutdown
                    logger.error("USB连接可能已断开，尝试重新初始化设备")
                return 1
        else:
            logger.warning("HID鼠标设备未初始化")
        return 0

    def wheelEvent(self, event):
        if not self.status['mouse_capture']:
            return
        # 增加灵敏度系数
        sensitivity_factor = 2.0
        wheel_delta = int((event.angleDelta().y() / 120) * sensitivity_factor)
        logger.debug(f"滚轮值: {wheel_delta}")
        
        if self.mode == 'absolute':
            report = struct.pack('<BHHHH', self.button_state, 0xFFFF, 0xFFFF, wheel_delta & 0xFFFF, 0)
        else:
            report = struct.pack('<BBBBB', self.button_state, 0, 0, wheel_delta & 0xFF, 0)
        
        self.send_hid_report(report, absolute=(self.mode == 'absolute'))