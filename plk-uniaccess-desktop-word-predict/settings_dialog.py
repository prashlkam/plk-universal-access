from PyQt5 import QtWidgets, QtCore

class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.setWindowTitle("WordQ Settings")
        self.config = config
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        layout = QtWidgets.QFormLayout(self)
        self.suggestions_spin = QtWidgets.QSpinBox()
        self.suggestions_spin.setRange(1, 15)
        self.prefix_spin = QtWidgets.QSpinBox()
        self.prefix_spin.setRange(1, 5)
        self.bigram_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.bigram_slider.setRange(0, 100)

        self.corpus_path = QtWidgets.QLineEdit()
        browse = QtWidgets.QPushButton("Browse")
        browse.clicked.connect(self.browse_corpus)
        h = QtWidgets.QHBoxLayout()
        h.addWidget(self.corpus_path); h.addWidget(browse)

        layout.addRow("Number of suggestions:", self.suggestions_spin)
        layout.addRow("Min prefix length:", self.prefix_spin)
        layout.addRow("Bigram weight (%):", self.bigram_slider)
        layout.addRow("Corpus file:", h)

        btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Save | QtWidgets.QDialogButtonBox.Cancel)
        btns.accepted.connect(self.save_and_close)
        btns.rejected.connect(self.reject)
        layout.addRow(btns)

    def browse_corpus(self):
        fn, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open corpus", "", "Text files (*.txt);;All files (*)")
        if fn:
            self.corpus_path.setText(fn)

    def load_settings(self):
        s = self.config.load()
        self.suggestions_spin.setValue(s.get('num_suggestions', 6))
        self.prefix_spin.setValue(s.get('min_prefix', 1))
        self.bigram_slider.setValue(int(s.get('bigram_weight', 0.7) * 100))
        self.corpus_path.setText(s.get('corpus', ''))

    def save_and_close(self):
        s = {
            'num_suggestions': self.suggestions_spin.value(),
            'min_prefix': self.prefix_spin.value(),
            'bigram_weight': self.bigram_slider.value()/100.0,
            'corpus': self.corpus_path.text()
        }
        self.config.save(s)
        self.accept()
