from PyQt5 import QtWidgets, QtCore, QtGui
import re

class SuggestionPopup(QtWidgets.QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            QtCore.Qt.Tool |
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.X11BypassWindowManagerHint
        )
        self.setAttribute(QtCore.Qt.WA_ShowWithoutActivating)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setMaximumHeight(250)

    def show_suggestions(self, suggestions, pos_point):
        self.clear()
        for i, s in enumerate(suggestions, 1):
            item = QtWidgets.QListWidgetItem(f"{i}. {s}")
            self.addItem(item)
        if suggestions:
            self.setCurrentRow(0)
            self.move(pos_point)
            self.show()
        else:
            self.hide()

    def accept_current(self):
        row = self.currentRow()
        if row >= 0:
            return self.item(row).text().split('. ',1)[1]
        return None
