import sys
import os
import json
from PySide6.QtWidgets import (QApplication, QWidget, QLabel, QMainWindow, 
                               QPushButton, QVBoxLayout, QHBoxLayout, QSlider, 
                               QSpinBox, QDialog, QSystemTrayIcon, QMenu)
from PySide6.QtGui import QPixmap, QImage, QCursor, QIcon, QAction
from PySide6.QtCore import Qt, QTimer, Slot
import mss
from PIL import Image
from appdirs import user_config_dir

from settings import SettingsDialog

class ConfigManager:
    def __init__(self):
        self.config_dir = user_config_dir("DesktopMagnifier", "Gemini")
        self.config_file = os.path.join(self.config_dir, "settings.json")
        os.makedirs(self.config_dir, exist_ok=True)
        self.settings = self.load_settings()

    def load_settings(self):
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return self.get_default_settings()

    def save_settings(self, settings):
        with open(self.config_file, 'w') as f:
            json.dump(settings, f, indent=4)
        self.settings = settings

    def get_default_settings(self):
        return {
            "default_mode": "windowed",
            "docked_position": "top",
            "zoom_level": 2.0
        }

class Magnifier(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.label = QLabel(self)
        self.sct = mss.mss()
        self.zoom_level = 2.0
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_magnifier)
        
        self.magnifier_size = 200

    def start(self):
        self.timer.start(16)  # ~60 FPS
        self.show()

    def stop(self):
        self.timer.stop()
        self.hide()

    def set_zoom(self, zoom):
        self.zoom_level = zoom

    def update_magnifier(self):
        pos = QCursor.pos()
        mouse_x, mouse_y = pos.x(), pos.y()

        width, height = self.magnifier_size, self.magnifier_size

        capture_width = int(width / self.zoom_level)
        capture_height = int(height / self.zoom_level)

        # Center the capture box around the mouse
        capture_x = mouse_x - capture_width // 2
        capture_y = mouse_y - capture_height // 2

        # Get monitor dimensions
        monitor = self.sct.monitors[1]

        # Clamp coordinates to be within the screen bounds
        capture_x = max(monitor["left"], min(capture_x, monitor["left"] + monitor["width"] - capture_width))
        capture_y = max(monitor["top"], min(capture_y, monitor["top"] + monitor["height"] - capture_height))

        grab_region = {
            "top": capture_y,
            "left": capture_x,
            "width": capture_width,
            "height": capture_height,
        }
        
        sct_img = self.sct.grab(grab_region)
        print(f"Screen shot taken: {sct_img}")

        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        print(f"PIL image created: {img}")

        magnified_img = img.resize((width, height), Image.Resampling.BICUBIC)
        print(f"Image resized: {magnified_img}")

        q_img = QImage(magnified_img.tobytes(), magnified_img.width, magnified_img.height, QImage.Format_RGB888)
        print(f"QImage created: {q_img}")

        pixmap = QPixmap.fromImage(q_img)
        print(f"Pixmap created: {pixmap}")
        
        self.label.setPixmap(pixmap)
        self.resize(width, height)
        
        # Offset the window so it doesn't cover the cursor
        self.move(mouse_x - width // 2, mouse_y - height // 2 - 120)

class MainWindow(QMainWindow):
    def __init__(self, config_manager):
        super().__init__()
        self.setWindowTitle("Desktop Magnifier")
        self.config_manager = config_manager

        self.magnifier = Magnifier()
        self.current_mode = None

        # --- Widgets ---
        self.mode_label = QLabel("Select Mode:")
        self.fullscreen_button = QPushButton("Fullscreen")
        self.docked_button = QPushButton("Docked")
        self.windowed_button = QPushButton("Windowed")
        
        self.zoom_label = QLabel("Zoom Level: 2.0x")
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setRange(2, 20) # Represents 1.0x to 10.0x in 0.5 steps
        self.zoom_slider.setTickInterval(1)
        
        self.settings_button = QPushButton("Settings")
        self.quit_button = QPushButton("Quit")

        # --- Layout ---
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(self.fullscreen_button)
        mode_layout.addWidget(self.docked_button)
        mode_layout.addWidget(self.windowed_button)
        
        main_layout.addWidget(self.mode_label)
        main_layout.addLayout(mode_layout)
        main_layout.addSpacing(20)
        main_layout.addWidget(self.zoom_label)
        main_layout.addWidget(self.zoom_slider)
        main_layout.addSpacing(20)
        main_layout.addWidget(self.settings_button)
        main_layout.addWidget(self.quit_button)
        
        self.setCentralWidget(central_widget)

        # --- System Tray ---
        self.tray_icon = QSystemTrayIcon(QIcon("assets/icon.png"), self)
        self.tray_icon.setToolTip("Desktop Magnifier")

        menu = QMenu(self)
        show_action = menu.addAction("Show")
        quit_action = menu.addAction("Quit")

        show_action.triggered.connect(self.show)
        quit_action.triggered.connect(QApplication.instance().quit)

        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()

        # --- Connections ---
        self.fullscreen_button.clicked.connect(self.activate_fullscreen_mode)
        self.docked_button.clicked.connect(self.activate_docked_mode)
        self.windowed_button.clicked.connect(self.activate_windowed_mode)
        self.zoom_slider.valueChanged.connect(self.update_zoom)
        self.settings_button.clicked.connect(self.open_settings)
        self.quit_button.clicked.connect(self.close)

        self.load_initial_settings()

    def load_initial_settings(self):
        settings = self.config_manager.load_settings()
        self.update_zoom(int(settings.get("zoom_level", 2.0) * 2))
        self.zoom_slider.setValue(int(settings.get("zoom_level", 2.0) * 2))
        
        default_mode = settings.get("default_mode", "windowed")
        if default_mode == "fullscreen":
            self.activate_fullscreen_mode()
        elif default_mode == "docked":
            self.activate_docked_mode()
        else:
            self.activate_windowed_mode()

    @Slot()
    def activate_fullscreen_mode(self):
        self.current_mode = "fullscreen"
        self.hide() # Hide main window
        self.magnifier.magnifier_size = self.screen().size().width()
        self.magnifier.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.magnifier.showFullScreen()
        self.magnifier.start()
        print("Fullscreen mode activated")

    @Slot()
    def activate_docked_mode(self):
        if self.current_mode == "fullscreen":
            self.magnifier.showNormal() # Exit fullscreen if active
        self.current_mode = "docked"
        self.show() # Ensure main window is visible
        
        screen_geometry = self.screen().geometry()
        dock_height = 200
        self.magnifier.magnifier_size = screen_geometry.width()
        self.magnifier.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.magnifier.setGeometry(0, 0, screen_geometry.width(), dock_height)
        self.magnifier.start()
        print("Docked mode activated")

    @Slot()
    def activate_windowed_mode(self):
        if self.current_mode == "fullscreen":
            self.magnifier.showNormal()
        self.current_mode = "windowed"
        self.show()
        
        self.magnifier.magnifier_size = 200
        # Make it a normal, movable window
        self.magnifier.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Tool) 
        self.magnifier.start()
        print("Windowed mode activated")

    @Slot(int)
    def update_zoom(self, value):
        zoom = value / 2.0
        self.magnifier.set_zoom(zoom)
        self.zoom_label.setText(f"Zoom Level: {zoom:.1f}x")

    @Slot()
    def open_settings(self):
        dialog = SettingsDialog(self)
        dialog.set_settings(self.config_manager.settings)
        if dialog.exec():
            self.config_manager.save_settings(dialog.get_settings())

    def closeEvent(self, event):
        event.ignore()
        self.hide()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    config_manager = ConfigManager()
    window = MainWindow(config_manager)
    window.show()
    sys.exit(app.exec())