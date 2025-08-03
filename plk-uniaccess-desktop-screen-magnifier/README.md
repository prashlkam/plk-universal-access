# Desktop Screen Magnifier

This is a cross-platform desktop screen magnifier application built with Python and PySide6. It provides a simple and effective way to magnify portions of your screen, with several modes and customization options.

## Features

*   **Three Magnification Modes:**
    *   **Windowed:** A resizable and movable window that displays a magnified view of the area around your mouse cursor.
    *   **Docked:** A stationary, full-width magnifier docked to an edge of your screen.
    *   **Fullscreen:** Magnifies the entire screen, with the view following your mouse cursor.
*   **Adjustable Zoom:** Zoom levels from 1.0x to 10.0x, with increments of 0.5x.
*   **Settings Dialog:** Configure and save your preferred settings, including:
    *   Default mode on startup.
    *   Docked mode position (top, bottom, left, or right).
*   **System Tray Integration:** The application can be minimized to the system tray for easy access.

## Requirements

*   Python 3.7+
*   PySide6
*   mss
*   Pillow
*   appdirs

All Python dependencies are listed in the `requirements.txt` file.

## Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/desktop-magnifier.git
    cd desktop-magnifier
    ```

2.  **Create a virtual environment:**

    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
    ```

3.  **Install the dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

## Usage

To run the application, execute the following command from the project's root directory:

```bash
python src/main.py
```

This will launch the main control window. From there, you can select the desired magnification mode, adjust the zoom level, and access the settings.

### Building from Source

To create a standalone executable, you can use PyInstaller:

1.  **Install PyInstaller:**

    ```bash
    pip install pyinstaller
    ```

2.  **Build the executable:**

    ```bash
    pyinstaller --onefile --windowed --icon=assets/icon.png src/main.py
    ```

    The executable will be created in the `dist` directory.

## Contributing

Contributions are welcome! If you find a bug or have a feature request, please open an issue on the project's GitHub page.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
