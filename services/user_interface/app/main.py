import sys
from mqtt_client import MQTTClient

from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QTabWidget,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
)
from PyQt6.QtGui import QPalette, QColor, QIcon, QPixmap
from PyQt6.QtCore import Qt, QSize


class Color(QWidget):

    def __init__(self, color):
        super(Color, self).__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(color))
        self.setPalette(palette)


class DashboardScreen(QWidget):
    def __init__(self):
        super().__init__()

        vLayout = QVBoxLayout()

        vLayout.addWidget(QLabel("Implementation intention"))

        hLayout = QHBoxLayout()
        hLayout.addWidget(QLabel("Check in Date and Time"))
        hLayout.addWidget(QLabel("Days remaining"))

        vLayout.addLayout(hLayout)
        self.setLayout(vLayout)


class NotificationBar(QWidget):
    def __init__(self):
        super().__init__()

        appBarLayout = QHBoxLayout()

        infoLayout = QHBoxLayout()
        # infoLayout.addWidget(QLabel("contact"))
        contactButton = QPushButton(
            # Icon made by alimasykurm from @flaticon
            icon=QIcon("./support_alimasykurm.png"),
            text="Contact",
            parent=self
        )
        contactButton.clicked.connect(self.button_clicked)
        # self.setCentralWidget(button)
        infoLayout.addWidget(contactButton)
        # infoLayout.addWidget(QLabel("help"))
        helpButton = QPushButton(
            # Icon made by Freepik from @flaticon
            icon=QIcon("./question_Freepik.png"),
            text="Help",
            parent=self
        )
        helpButton.clicked.connect(self.button_clicked)
        infoLayout.addWidget(helpButton)
        timeLayout = QHBoxLayout()
        timeLayout.addWidget(QLabel("time"))

        indicatorLayout = QHBoxLayout()

        # wifiStatus = QLabel(self)
        # pixmap = QPixmap('wifi_redempticon.png')
        # wifiStatus.setPixmap(pixmap)
        # self.setCentralWidget(wifiStatus)
        # self.resize(pixmap.width(), pixmap.height())

        wifiStatus = QLabel(self)
        pixmap = QPixmap('wifi_redempticon.png')
        scaled_pixmap = pixmap.scaled(
            QSize(24, 24), Qt.AspectRatioMode.KeepAspectRatio)
        wifiStatus.setPixmap(scaled_pixmap)
        indicatorLayout.addWidget(wifiStatus)

        indicatorLayout.addWidget(QLabel("Mic"))
        # Dave Gandy for microphone on and off image

        indicatorLayout.addWidget(QLabel("Cam"))
        # icon_small for videocam on image
        # icon_small for videocam off image

        appBarLayout.addLayout(infoLayout)
        appBarLayout.addLayout(timeLayout)
        appBarLayout.addLayout(indicatorLayout)

        self.setLayout(appBarLayout)

    def button_clicked(self, s):
        dlg = QMessageBox.about(
            self, "about", "If you need help or encounter any issued with the system please dont hesitate to contact Shabaj using the following contact details:\nEmail:\nPhone:")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App ")

        verticalSpace = QVBoxLayout()

        verticalSpace.addWidget(NotificationBar())
        verticalSpace.addWidget(self.buildTab())

        widget = QWidget()
        widget.setLayout(verticalSpace)
        self.setCentralWidget(widget)

    def buildTab(self):
        dashboard = DashboardScreen()

        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.TabPosition.West)
        tabs.setMovable(True)

        tabs.addTab(dashboard, "Home")
        tabs.addTab(Color("blue"), "Check-In")
        tabs.addTab(Color("green"), "History")
        tabs.addTab(Color("yellow"), "Profile")

        return tabs


def main():
    # Replace with your MQTT broker address
    broker_address = 'localhost'
    port = 1883  # Replace with the correct port if needed

    # Initialise MQTT client
    mqtt_client = MQTTClient(broker_address, port)

    app = QApplication(sys.argv)

    window = MainWindow()

    try:
        window.show()
    except KeyboardInterrupt:
        print("Exiting program...")
    finally:
        mqtt_client.disconnect()
        app.exec()


if __name__ == "__main__":
    main()
