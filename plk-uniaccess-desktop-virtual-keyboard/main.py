import sys
import json
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QGridLayout, QVBoxLayout, QHBoxLayout, QComboBox, QLabel, QSpacerItem
from PyQt6.QtCore import Qt
from pynput.keyboard import Controller, Key
from languages_data import languages # Import the languages dictionary

class VirtualKeyboard(QWidget):
    def __init__(self):
        super().__init__()
        self.keyboard_controller = Controller()
        self.current_layout = None
        self.current_language_mappings = {}
        self.shift_active = False
        self.alt_gr_active = False

        self.languages = languages # Assign the imported dictionary

        # Define colors for key groups
        self.group_colors = {
            "alpha": "#ADD8E6",  # Light Blue
            "modifier": "#90EE90", # Light Green
            "special": "#FFB6C1", # Pink
            "function": "#DAA520", # Dark Yellow
            "space": "#C3B1E1",   # Indigo
            "arrow": "#D3D3D3",    # Light Gray (default for new groups)
            "symbol": "#ADD8E6" # Light Blue
        }
        self.color_pickers = {}

        self.initUI()

    def initUI(self):
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # Layout selection
        self.layout_selector = QComboBox()
        self.layout_selector.addItem("Android-like", "android_layout.json")
        self.layout_selector.addItem("PC-like", "pc_layout.json")
        self.layout_selector.currentIndexChanged.connect(self.change_layout)
        self.main_layout.addWidget(self.layout_selector)

        # Language selection
        self.language_selector = QComboBox()
        for lang_key, lang_data in self.languages.items():
            self.language_selector.addItem(lang_data['name'], lang_key)
        self.language_selector.currentIndexChanged.connect(self.change_language)
        self.main_layout.addWidget(self.language_selector)

        # Color selection for key groups
        self.color_selection_layout = QHBoxLayout()
        self.main_layout.addLayout(self.color_selection_layout)

        for group_id, default_color in self.group_colors.items():
            group_label = QLabel(f"{group_id.capitalize()} Keys:")
            color_picker = QComboBox()
            color_picker.addItem("Light Blue", "#ADD8E6")
            color_picker.addItem("Light Green", "#90EE90")
            color_picker.addItem("Pink", "#FFB6C1")
            color_picker.addItem("Dark Yellow", "#DAA520") # Updated to Dark Yellow
            color_picker.addItem("Indigo", "#C3B1E1")
            color_picker.addItem("Light Gray", "#D3D3D3")

            # Set initial selection
            index = color_picker.findData(default_color)
            if index != -1:
                color_picker.setCurrentIndex(index)

            color_picker.currentIndexChanged.connect(lambda index, g_id=group_id: self.change_group_color(g_id, color_picker.itemData(index)))
            self.color_pickers[group_id] = color_picker

            self.color_selection_layout.addWidget(group_label)
            self.color_selection_layout.addWidget(color_picker)

        self.keyboard_grid_layout = QGridLayout()
        self.keyboard_grid_layout.setSpacing(5)
        self.main_layout.addLayout(self.keyboard_grid_layout)

        self.load_layout("pc_layout.json") # Load PC layout by default
        self.load_language("english") # Load English by default

        self.setWindowTitle('Virtual Keyboard')
        self.show()

    def clear_keyboard_layout(self):
        # Remove all widgets from the grid layout
        for i in reversed(range(self.keyboard_grid_layout.count())):
            widget_to_remove = self.keyboard_grid_layout.itemAt(i).widget()
            if widget_to_remove:
                widget_to_remove.setParent(None)

    def load_language(self, language_key):
        if language_key in self.languages:
            self.current_language_mappings = self.languages[language_key]['mappings']
            self.update_key_labels()
        else:
            print(f"Error: Language {language_key} not found.")
            self.current_language_mappings = {}

    def change_language(self, index):
        language_key = self.language_selector.itemData(index)
        self.load_language(language_key)

    def load_layout(self, layout_file):
        self.clear_keyboard_layout()
        try:
            with open(f"layouts/{layout_file}", 'r', encoding='utf-8') as f:
                self.current_layout = json.load(f)
        except FileNotFoundError:
            print(f"Error: Layout file {layout_file} not found.")
            self.current_layout = None
            return

        if not self.current_layout:
            return

        # Iterate through all keys and add them to the grid layout using explicit positions
        for key_data in self.current_layout['keys']:
            label = key_data['label']
            key_code_str = key_data['key_code']
            width_factor = key_data.get('width_factor', 1)
            group_id = key_data.get('group_id', 'default') # Get group_id
            row = key_data['row']
            col = key_data['col']
            row_span = key_data.get('row_span', 1)
            col_span = key_data.get('col_span', 1) # Default to 1, not width_factor

            button = QPushButton(label)
            button.setFixedSize(int(40 * width_factor), 40)
            button.setProperty("key_data", key_data) # Store key data for easy access
            button.setProperty("group_id", group_id) # Store group_id
            button.clicked.connect(lambda checked, btn=button: self.on_key_press(btn))
            
            self.keyboard_grid_layout.addWidget(button, row, col, row_span, col_span)

        self.update_key_labels()

    def change_layout(self, index):
        layout_file = self.layout_selector.itemData(index)
        self.load_layout(layout_file)

    def on_key_press(self, button):
        key_data = button.property("key_data")
        key_code_str = key_data['key_code']
        label = key_data['label']

        # Handle special keys like Shift and AltGr
        if key_code_str == "Key.shift":
            self.shift_active = not self.shift_active
            self.update_key_labels()
            return
        elif key_code_str == "Key.alt_gr": # Assuming a key for AltGr
            self.alt_gr_active = not self.alt_gr_active
            self.update_key_labels()
            return

        # Determine the base character from the layout (English, potentially shifted)
        base_char_from_layout = label
        if self.shift_active and 'shift_label' in key_data:
            base_char_from_layout = key_data['shift_label']
        elif self.alt_gr_active and 'alt_gr_label' in key_data:
            base_char_from_layout = key_data['alt_gr_label']

        # Apply language mapping to the base character
        char_to_type = self.current_language_mappings.get(base_char_from_layout, base_char_from_layout)

        # Convert string key codes to pynput.keyboard.Key objects if necessary
        if isinstance(char_to_type, str) and char_to_type.startswith("Key."):
            try:
                pynput_key = getattr(Key, char_to_type.split('.')[1])
                self.keyboard_controller.press(pynput_key)
                self.keyboard_controller.release(pynput_key)
            except AttributeError:
                print(f"Warning: Unknown pynput Key: {char_to_type}")
        else:
            # For regular characters, use the determined char_to_type
            self.keyboard_controller.type(char_to_type)

        # Reset shift/alt_gr after a non-modifier key press (optional, depends on desired behavior)
        # self.shift_active = False
        # self.alt_gr_active = False
        # self.update_key_labels()

    def change_group_color(self, group_id, color_hex):
        self.group_colors[group_id] = color_hex
        self.update_key_labels() # Re-apply styles to all keys

    def get_luminance(self, hex_color):
        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        
        # Convert RGB to sRGB
        r_srgb = r / 255.0
        g_srgb = g / 255.0
        b_srgb = b / 255.0

        # Apply gamma correction
        r_linear = r_srgb / 12.92 if r_srgb <= 0.03928 else ((r_srgb + 0.055) / 1.055) ** 2.4
        g_linear = g_srgb / 12.92 if g_srgb <= 0.03928 else ((g_srgb + 0.055) / 1.055) ** 2.4
        b_linear = b_srgb / 12.92 if b_srgb <= 0.03928 else ((b_srgb + 0.055) / 1.055) ** 2.4

        # Calculate luminance
        luminance = 0.2126 * r_linear + 0.7152 * g_linear + 0.0722 * b_linear
        return luminance

    def get_contrast_ratio(self, color1_hex, color2_hex):
        L1 = self.get_luminance(color1_hex)
        L2 = self.get_luminance(color2_hex)
        
        # Ensure L1 is the lighter of the two colors
        if L2 > L1:
            L1, L2 = L2, L1

        return (L1 + 0.05) / (L2 + 0.05)

    def update_key_labels(self):
        if not self.current_layout or not self.current_language_mappings:
            return

        # Iterate through all widgets in the grid layout
        for i in range(self.keyboard_grid_layout.count()):
            item = self.keyboard_grid_layout.itemAt(i)
            button = item.widget()
            if button and button.property("key_data"):
                key_data = button.property("key_data")
                label = key_data['label']
                shift_label = key_data.get('shift_label')
                alt_gr_label = key_data.get('alt_gr_label')
                group_id = button.property("group_id") # Get group_id from button

                # Determine the base character for display (English, potentially shifted)
                display_base_char = label
                if self.shift_active and shift_label:
                    display_base_char = shift_label
                elif self.alt_gr_active and alt_gr_label:
                    display_base_char = alt_gr_label
                
                # Apply language mapping for display
                display_label = self.current_language_mappings.get(display_base_char, display_base_char)

                button.setText(display_label)

                # Apply background color based on group_id
                background_color = self.group_colors.get(group_id, "#D3D3D3") # Default to light gray
                
                # Determine font color based on contrast ratio
                font_color = "black"
                if self.get_contrast_ratio(background_color, "#000000") >= 3:
                    font_color = "black"
                elif self.get_contrast_ratio(background_color, "#FFFFFF") >= 3:
                    font_color = "white"
                else:
                    # Fallback if neither black nor white provides enough contrast
                    # This case should ideally not be reached with the chosen light colors
                    font_color = "black" 

                button.setStyleSheet(f"background-color: {background_color}; color: {font_color};")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    vk = VirtualKeyboard()
    sys.exit(app.exec())