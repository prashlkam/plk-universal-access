import sys, os, threading, time
from PyQt5 import QtWidgets, QtGui, QtCore
from prediction import PredictionModel
from popup import SuggestionPopup
from hooks import KeyHook
from settings_dialog import SettingsDialog
from config import Config
import platform

# choose caret module based on OS
caret = None
if platform.system() == 'Windows':
    try:
        import caret_win as caret_mod
        caret = caret_mod
    except Exception:
        caret = None
else:
    try:
        import caret_linux as caret_mod
        caret = caret_mod
    except Exception:
        caret = None

class TrayApp(QtWidgets.QSystemTrayIcon):
    def __init__(self, icon, model, config):
        super().__init__(icon)
        self.model = model
        self.config = config
        self.setToolTip('WordQ-like Predictor')
        menu = QtWidgets.QMenu()
        settings_action = menu.addAction('Settings')
        settings_action.triggered.connect(self.open_settings)
        quit_action = menu.addAction('Quit')
        quit_action.triggered.connect(QtWidgets.qApp.quit)
        self.setContextMenu(menu)
        self.activated.connect(self.on_activated)
        self.popup = SuggestionPopup()
        self.settings_dialog = SettingsDialog(self.config)
        # start key hook
        self.keyhook = KeyHook(self.on_key_event)
        self.keyhook.start()

    def on_activated(self, reason):
        if reason == QtWidgets.QSystemTrayIcon.Trigger:
            self.open_settings()

    def open_settings(self):
        self.settings_dialog.load_settings()
        if self.settings_dialog.exec_():
            # reload corpus if provided
            s = self.config.load()
            corpus = s.get('corpus','').strip()
            if corpus and os.path.exists(corpus):
                self.model.train_from_file(corpus)

    def show_suggestions_at(self, suggestions, pos):
        if not suggestions:
            self.popup.hide()
            return
        # Qt expects QPoint; pos is (x,y)
        p = QtCore.QPoint(pos[0], pos[1])
        self.popup.show_suggestions(suggestions, p)

    def on_key_event(self, text_buffer, key):
        # simple: get current word prefix (after last whitespace)
        prefix = text_buffer.rstrip().split(' ')[-1] if text_buffer else ''
        s = self.config.load()
        min_pref = s.get('min_prefix', 1)
        num = s.get('num_suggestions', 6)
        bw = s.get('bigram_weight', 0.7)
        if len(prefix) >= min_pref:
            # determine prev word
            parts = text_buffer.rstrip().split()
            prev = parts[-2] if len(parts) >= 2 else None
            suggestions = self.model.predict(prefix, prev_word=prev, k=num, lambda_context=bw)
            # get caret pos
            pos = None
            if caret and hasattr(caret, 'get_caret_position'):
                pos = caret.get_caret_position()
            if pos:
                # adjust a little downwards
                self.show_suggestions_at(suggestions, (pos[0], pos[1]+5))
            else:
                # no caret info: hide popup
                self.popup.hide()
        else:
            self.popup.hide()

def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    # tray icon
    icon = QtGui.QIcon.fromTheme('applications-education')
    if icon.isNull():
        # fallback to built-in
        icon = app.style().standardIcon(QtWidgets.QStyle.SP_FileDialogInfoView)
    cfg = Config()
    model = PredictionModel()
    # small demo training; user should load corpus from settings
    model.train_from_text('This is a demo corpus. The quick brown fox jumps over the lazy dog.')
    tray = TrayApp(icon, model, cfg)
    tray.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
