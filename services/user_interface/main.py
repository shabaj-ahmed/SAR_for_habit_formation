from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import threading
import time
from .communication_interface import CommunicationInterface
import logging
import os
import sys
import subprocess

app = Flask(__name__)
app.config['SYSTEM_IS_STILL_LOADING'] = True
socketio = SocketIO(app)

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../../"))
sys.path.insert(0, project_root)
from shared_libraries.logging_config import setup_logger

# Setup logger
setup_logger()

logger = logging.getLogger(__name__)

# Persistent message storage
chat_history = []

communication_interface = CommunicationInterface(
    broker_address=os.getenv("MQTT_BROKER_ADDRESS"),
    port=int(os.getenv("MQTT_BROKER_PORT"))
)

communication_interface.socketio = socketio

volume_button_states = {
    'quiet': False,
    'default': False,
    'loud': False,
}
voice_button_states = {
    'robotic': False,
    'human': False,
}

def publish_heartbeat():
    while True:
        # Publish heartbeat
        time.sleep(30)  # Publish heartbeat every 30 seconds

# Start heartbeat thread
threading.Thread(target=publish_heartbeat, daemon=True).start()

# MQTT message handler
def on_mqtt_message(message):
    # Format the message
    formatted_message = {
        "sender": message.get("sender", "robot"),  # Default sender is robot
        "content": message.get("content", ""),
        "time": message.get("time", time.strftime("%H:%M %p | %B %d"))
    }
    # Add to chat history
    chat_history.append(formatted_message)
    logger.info(f"New message: {formatted_message}")
    # Emit the message to connected clients
    socketio.emit('new_message', formatted_message)

# Register the MQTT message handler
communication_interface.message_callback = on_mqtt_message

@app.route('/')
def home():
    serviceStatus = communication_interface.get_system_status()
    still_loading = False
    print(f"serviceStatus: {serviceStatus}")
    for key, value in serviceStatus.items():
        if value != "Awake":
            still_loading = True
    if still_loading or serviceStatus == {}:
        return render_template('system_boot_up.html')
    return render_template('home.html')

@socketio.on('ui_ready')
def handle_ui_ready():
    logger.info("UI is ready, sending system status update...")

    # Publish the UI status to the MQTT broker
    communication_interface.publish_UI_status("Awake")

@app.route('/check_in')
def check_in():
    return render_template('check_in.html', chat_history=chat_history)

@app.route('/history')
def history():
    return render_template('history.html')

@app.route('/settings')
def settings():
    return render_template('settings.html', volume_button_states=volume_button_states, voice_button_states=voice_button_states)

@app.route('/colour/<secected_colour>')
def colour_button_click(secected_colour):

    # Send colour chage command to robot
    communication_interface.change_colour(secected_colour)
    return jsonify({'status': 'success'})

@app.route('/volume/<button_name>')
def volume_button_click(button_name):
    if button_name in volume_button_states:
        # Set the state of all buttons to False
        for key in volume_button_states:
            volume_button_states[key] = False
        # Only set the state of the clicked button to True
        volume_button_states[button_name] = True
        logger.info(f"Volume button clicked: {button_name}")
        # Call the function in robot_controller
        communication_interface.change_volume(button_name)
    return jsonify({'status': 'success'})

@app.route('/brightness/<int:brightness_value>')
def brightness_slider_change(brightness_value):
    # Map the brightness value from range 1-100 to 1-255
    mapped_value = int(20 + (int(brightness_value) - 1) * 235 / 99)
    # logger.info(f"Brightness slider changed: {brightness_value}")
    try:
        # Update the brightness using the mapped value
        subprocess.run(
            f'echo {mapped_value} | sudo tee /sys/class/backlight/6-0045/brightness',
            shell=True,
            check=True
        )
        # Return a success response
        return f"Brightness successfully set to {mapped_value}", 200
    except subprocess.CalledProcessError as e:
        # Return an error response if the command fails
        return f"Failed to set brightness: {e}", 500

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/start_check_in', methods=['POST'])
def start_check_in():
    # Start the check-in process
    communication_interface.start_check_in()
    return jsonify({'status': 'success', 'message': 'Check-In command sent'})
# Asynchronous response returning true but the message channel closed before response received

@socketio.on('disconnect')
def handle_disconnect():
    logger.info('Client disconnected')

if __name__ == '__main__':
    try:
        socketio.run(port=8000, debug=True)
    except KeyboardInterrupt:
        logger.info("Exiting user interface service...")
    finally:
        communication_interface.disconnect()
