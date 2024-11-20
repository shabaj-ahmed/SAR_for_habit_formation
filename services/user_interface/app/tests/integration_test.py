import pytest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest  # Import QTest for waiting
from PyQt6.QtCore import QCoreApplication

# Add the project root directory to sys.path
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
sys.path.insert(0, project_root)

from services.user_interface.app.src.communication_interface import CommunicationInterface
from services.user_interface.app.src.main import MainWindow  # Adjust the path to your MainWindow

@pytest.fixture
def app(qtbot):
    """Set up the PyQt application for integration testing."""
    app = QApplication([])  # Create the PyQt application
    mqtt_client = CommunicationInterface(broker_address='localhost',
                             port=1883)  # Use real MQTT broker
    window = MainWindow(mqtt_client)
    qtbot.addWidget(window)
    window.show()

    yield window, mqtt_client

    # Teardown logic: disconnect MQTT and close the PyQt app
    mqtt_client.disconnect()  # Ensure MQTT client is disconnected after test
    QTest.qWait(1000)  # Give some time for MQTT disconnection
    app.quit()  # Close the PyQt application properly
    QTest.qWait(500)  # Wait for app to process quit
    QApplication.processEvents()  # Ensure that all events are processed after quit


def test_mqtt_integration_with_real_broker(app, qtbot):
    """Test MQTT integration with a real Mosquitto broker."""
    window, mqtt_client = app

    # Simulate publishing a message to the MQTT broker to simulate mic turning on
    mqtt_client.mqtt_client.publish("robot/audioActive", "1")
    QTest.qWait(500)  # Wait for the message to be processed
    QCoreApplication.processEvents()  # Process any pending PyQt events
    assert window.notification_bar.micStatus.pixmap().toImage(
    ) == window.notification_bar.micOnPixmap.toImage()

    # Simulate another message to turn the mic off
    mqtt_client.mqtt_client.publish("robot/audioActive", "0")
    QTest.qWait(500)
    QCoreApplication.processEvents()  # Process any pending PyQt events
    assert window.notification_bar.micStatus.pixmap().toImage(
    ) == window.notification_bar.micOffPixmap.toImage()

    # Test the camera status similarly
    mqtt_client.mqtt_client.publish("robot/cameraActive", "1")
    QTest.qWait(500)
    QCoreApplication.processEvents()
    assert window.notification_bar.camStatus.pixmap().toImage(
    ) == window.notification_bar.camOnPixmap.toImage()

    mqtt_client.mqtt_client.publish("robot/cameraActive", "0")
    QTest.qWait(500)
    QCoreApplication.processEvents()
    assert window.notification_bar.camStatus.pixmap().toImage(
    ) == window.notification_bar.camOffPixmap.toImage()
