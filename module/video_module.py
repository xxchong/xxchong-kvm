import os
from datetime import datetime
from PyQt5.QtCore import QTimer, QSettings
from PyQt5.QtWidgets import QMessageBox, QFileDialog
from PyQt5.QtMultimedia import QCamera, QCameraInfo, QCameraViewfinderSettings, QCameraImageCapture
from PyQt5.QtMultimediaWidgets import QCameraViewfinder
import logging

class VideoHandler:
    def __init__(self, main_window, central_widget):
        self.main_window = main_window
        self.central_widget = central_widget
        self.camera = None
        self.camera_started = False
        self.image_capture = None
        self.online_webcams = QCameraInfo.availableCameras()
        self.camera_config = {
            'device_No': 0,
            'resolution_X': 1280,
            'resolution_Y': 720,
            'device_name': []
        }
        self.settings = QSettings("YourCompany", "YourApp")
        self.save_path = self.settings.value("save_path", os.path.join(os.path.dirname(os.path.abspath(__file__)), "Screenshots"))

    def refresh_input_devices(self):
        self.online_webcams = QCameraInfo.availableCameras()
        return self.online_webcams

    def select_camera(self, index):
        self.camera_config['device_No'] = index
        try:
            self.set_webcam(True)
            return True
        except Exception as e:
            logging.error(f"选择摄像头错误: {e}")
            return False

    def set_webcam(self, s):
        if s:
            try:
                if self.camera:
                    self.camera.stop()
                    self.camera.unload()
                    self.camera = None

                self.camera = QCamera(self.online_webcams[self.camera_config['device_No']])
                self.camera.setViewfinder(self.central_widget)
                self.camera.setCaptureMode(QCamera.CaptureStillImage)
                self.camera.error.connect(lambda: self.alert(self.camera.errorString()))
                
                view_finder_settings = QCameraViewfinderSettings()
                view_finder_settings.setResolution(self.camera_config['resolution_X'], self.camera_config['resolution_Y'])
                view_finder_settings.setMinimumFrameRate(30)
                self.camera.setViewfinderSettings(view_finder_settings)
                
                self.image_capture = QCameraImageCapture(self.camera)
                self.image_capture.setCaptureDestination(QCameraImageCapture.CaptureToFile)
                self.image_capture.error.connect(lambda error_code, error_string: self.alert(error_string))
                self.image_capture.imageSaved.connect(self.on_image_saved)
                
                self.camera.start()
                logging.info("摄像头已成功启动")
                self.camera_started = True
                return True
                
            except Exception as e:
                logging.error(f"摄像头启动错误: {e}")
                self.camera_started = False
                self.alert(f"摄像头启动错误: {e}")
                return False
        else:
            if self.camera:
                self.camera.stop()
                self.camera.unload()
                self.camera = None
            if self.image_capture:
                self.image_capture = None
            logging.info("摄像头已停止")
            self.camera_started = False
            return True
        
    def is_camera_started(self):
        return self.camera_started


    def take_screenshot(self):
        if not self.camera or not self.image_capture:
            QMessageBox.warning(self.central_widget, "警告", "请先选择输入设备", QMessageBox.Ok)
            return "请先选择输入设备"

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"screenshot_{timestamp}.jpg"
        capture_path = os.path.join(self.save_path, file_name)

        try:
            self.image_capture.capture(capture_path)
            return f"正在保存图片: {capture_path}"
        except Exception as e:
            logging.error(f"截图时出错: {e}")
            return f"截图失败: {str(e)}"

    def set_save_path(self):
        new_path = QFileDialog.getExistingDirectory(self.main_window, "选择保存路径", self.save_path)
        if new_path:
            self.save_path = new_path
            self.settings.setValue("save_path", self.save_path)
            
            if not os.access(self.save_path, os.W_OK):
                logging.warning(f"无法写入选择的路径: {self.save_path}")
                return f"无法写入选择的路径: {self.save_path}\n请选择其他路径或检查权限。"
            return f"文件保存路径已更新: {self.save_path}"
        return None

    def on_image_saved(self, id, filename):
        logging.info(f"图像已保存，ID: {id}, 文件名: {filename}")
        if os.path.exists(filename):
            return f"截图已保存: {filename}"
        else:
            return "图片保存失败"

    def alert(self, s):
        err = QMessageBox(self.main_window)
        err.setWindowTitle('Error')
        err.setText(s)
        err.exec()
        print(s)

    def get_camera_info(self):
        if self.camera_config['device_No'] < len(self.online_webcams):
            camera_info = self.online_webcams[self.camera_config['device_No']]
            return f"当前摄像头: {camera_info.description()} | 分辨率: {self.camera_config['resolution_X']}x{self.camera_config['resolution_Y']}"
        return "未选择摄像头"

    def update_resolution(self, width, height):
        self.camera_config['resolution_X'] = width
        self.camera_config['resolution_Y'] = height
        if self.camera:
            self.set_webcam(True)


    def get_camera_config(self):
        return self.camera_config


