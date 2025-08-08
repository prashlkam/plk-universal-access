# WordQ-like System-wide Predictor - Prototype (Windows + Linux/X11)

**What this is:** A prototype cross-platform (Windows + Linux/X11) desktop assistant that
shows word predictions system-wide. It includes a system tray app, global keyboard hook,
caret tracking modules for Windows and Linux (X11 / AT-SPI), a PyQt settings dialog, and a prediction model.

**Important:** This is a prototype. Some OS-level APIs require extra permissions and libraries:
- Python 3.9+ recommended
- Required Python packages: `PyQt5`, `pynput`. Optional: `pywin32` (or ctypes used), `pyatspi` (Linux AT-SPI), `xdotool` (Linux fallback).
  Install with: `pip install pyqt5 pynput`
- On Linux, enable Accessibility/AT-SPI (GNOME, etc.) or install `xdotool` for a fallback approximation.
- On Windows, run normally; some apps with custom rendering may not expose caret info.

**How to run (development):**
1. `pip install -r requirements.txt`
2. Run `python main.py`
3. The app creates a system tray icon. Open Settings from tray to configure corpus and options.

**Limitations & Notes:**
- Wayland is not fully supported here; consider integrating as an input method (IBus/Fcitx) for Wayland.
- Some applications (games, Electron apps with custom text rendering) may not report caret location.
- You may need to run with elevated permissions on some desktop environments to access other apps' caret.

**Files in this package:**
- main.py: entry point, tray and integration glue
- prediction.py: unigram+bigram prediction model
- popup.py: floating suggestion widget (PyQt5)
- hooks.py: global keyboard hook (pynput) integration
- caret_win.py: Windows caret fetching (ctypes)
- caret_linux.py: Linux caret fetching (AT-SPI or xdotool fallback)
- settings_dialog.py: PyQt settings dialog
- config.py: simple JSON settings persistence
- requirements.txt: suggested pip packages

Read code comments for further implementation/extension guidance.
