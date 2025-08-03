
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton, QDialogButtonBox

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")

        self.layout = QVBoxLayout(self)

        # --- Default Mode --- 
        self.mode_label = QLabel("Default Mode on Startup:")
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Windowed", "Docked", "Fullscreen"])
        self.layout.addWidget(self.mode_label)
        self.layout.addWidget(self.mode_combo)

        # --- Docked Mode Settings ---
        self.dock_position_label = QLabel("Docked Position:")
        self.dock_position_combo = QComboBox()
        self.dock_position_combo.addItems(["Top", "Bottom", "Left", "Right"])
        self.layout.addWidget(self.dock_position_label)
        self.layout.addWidget(self.dock_position_combo)

        # --- Buttons ---
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

    def get_settings(self):
        return {
            "default_mode": self.mode_combo.currentText().lower(),
            "docked_position": self.dock_position_combo.currentText().lower()
        }

    def set_settings(self, settings):
        self.mode_combo.setCurrentText(settings.get("default_mode", "windowed").capitalize())
        self.dock_position_combo.setCurrentText(settings.get("docked_position", "top").capitalize())
