import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QSizePolicy
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtMultimedia import QCamera, QCameraInfo
from PyQt5.QtMultimediaWidgets import QCameraViewfinder

class VideoCaptureApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("视频采集软件")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.viewfinder = QCameraViewfinder()
        self.viewfinder.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout.addWidget(self.viewfinder)

        self.controls_layout = QHBoxLayout()
        self.camera_combo = QComboBox()
        self.resolution_combo = QComboBox()
        self.start_button = QPushButton("开始")
        self.stop_button = QPushButton("停止")

        self.controls_layout.addWidget(QLabel("摄像头:"))
        self.controls_layout.addWidget(self.camera_combo)
        self.controls_layout.addWidget(QLabel("分辨率:"))
        self.controls_layout.addWidget(self.resolution_combo)
        self.controls_layout.addWidget(self.start_button)
        self.controls_layout.addWidget(self.stop_button)

        self.layout.addLayout(self.controls_layout)

        self.camera = None
        self.available_cameras = QCameraInfo.availableCameras()
        self.setup_ui()
        self.set_background_color()  # 添加这一行


    def setup_ui(self):
        for camera in self.available_cameras:
            self.camera_combo.addItem(camera.description())
        
        self.camera_combo.currentIndexChanged.connect(self.select_camera)
        self.resolution_combo.currentIndexChanged.connect(self.change_resolution)
        self.start_button.clicked.connect(self.start_camera)
        self.stop_button.clicked.connect(self.stop_camera)

        self.select_camera(1)

    def select_camera(self, index):
        self.stop_camera()
        self.camera = QCamera(self.available_cameras[index])
        self.camera.setViewfinder(self.viewfinder)
        
        self.resolution_combo.clear()
        supported_resolutions = self.camera.supportedViewfinderResolutions()
        for resolution in supported_resolutions:
            self.resolution_combo.addItem(f"{resolution.width()}x{resolution.height()}")

    def change_resolution(self, index):
        if self.camera:
            resolution = self.camera.supportedViewfinderResolutions()[index]
            viewfinder_settings = self.camera.viewfinderSettings()
            viewfinder_settings.setResolution(resolution)
            self.camera.setViewfinderSettings(viewfinder_settings)

    def start_camera(self):
        if self.camera:
            self.camera.start()
            self.viewfinder.show()

    def stop_camera(self):
        if self.camera:
            self.camera.stop()

    def set_background_color(self):
        palette = self.palette()
        palette.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(palette)
        self.setAutoFillBackground(True)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.set_background_color()  # 添加这一行

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoCaptureApp()
    window.show()
    sys.exit(app.exec_())
    