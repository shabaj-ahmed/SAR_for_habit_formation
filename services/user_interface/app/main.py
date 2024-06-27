import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QTabWidget,
    QWidget,
    QVBoxLayout,
    QHBoxLayout
)
from PyQt6.QtGui import QPalette, QColor


class Color(QWidget):

    def __init__(self, color):
        super(Color, self).__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(color))
        self.setPalette(palette)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")

        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.TabPosition.West)
        tabs.setMovable(True)

        tabs.addTab(Color("red"), "Home")
        tabs.addTab(Color("blue"), "Check-In")
        tabs.addTab(Color("green"), "History")
        tabs.addTab(Color("yellow"), "Profile")

        verticalSpace = QVBoxLayout()
        horizontalSpace = QHBoxLayout()

        notificationBar = QLabel("Welcome to my app")

        verticalSpace.addWidget(notificationBar)
        verticalSpace.addWidget(tabs)

        widget = QWidget()
        widget.setLayout(verticalSpace)
        self.setCentralWidget(widget)


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()
