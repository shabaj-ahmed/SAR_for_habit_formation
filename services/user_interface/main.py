from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import threading
import time
from datetime import datetime
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
from shared_libraries.event_dispatcher import EventDispatcher

# Setup logger
setup_logger()

logger = logging.getLogger(__name__)

# Persistent check in data
check_in_start_time = None
chat_history = []

volume_button_states = {
    'quiet': False,
    'default': False,
    'loud': False,
}
voice_button_states = {
    'robotic': False,
    'human': False,
}

# Global variable to store connection status
connection_status = {
    'robot': True, # Assume the robot is connected by default on startup
    'wifi': False,
    'mic': False,
    'cam': False,
    'wifi_download_speed': 0,
    'wifi_upload_speed': 0,
}

dispatcher = EventDispatcher()

communication_interface = CommunicationInterface(
    broker_address=os.getenv("MQTT_BROKER_ADDRESS"),
    port=int(os.getenv("MQTT_BROKER_PORT")),
    event_dispatcher=dispatcher
)

communication_interface.socketio = socketio

def _register_event_handlers():
    dispatcher.register_event("update_service_state", update_state)
    dispatcher.register_event("update_connectoin_status", handle_status_update)

implementationIntention = ""
start_date = None
study_duration = None
days_remaining = None
brightness_value = 50
reminder_time = datetime.now().time()
reminder_time_ampm = "AM"

def update_state(payload):
    global implementationIntention, start_date, study_duration, days_remaining, brightness_value, reminder_time, reminder_time_ampm
    logger.info(f"State update received in UI: {payload}")
    state_name = payload.get("state_name", "")
    if state_name== "implementation_intention":
        implementationIntention = payload.get("state_value", "")
        logger.info(f"Implementation intention updated: {implementationIntention}")
    elif state_name == "start_date":
        start_date = datetime.strptime(payload.get("state_value", ""), "%Y-%m-%d").date()
        if study_duration:
            days_remaining()
        logger.info(f"Start date updated: {start_date}")
    elif state_name == "study_duration":
        study_duration = int(payload.get("state_value", ""))
        logger.info(f"Study duration updated: {study_duration}")
        if start_date:
            days_remaining()
    elif state_name == "reminder_time_hr":
        reminder_time = reminder_time.replace(hour=int(payload.get("state_value", "")))
        logger.info(f"Reminder time updated: {reminder_time}")
    elif state_name == "reminder_time_min":
        reminder_time = reminder_time.replace(minute=int(payload.get("state_value", "")))
        logger.info(f"Reminder time updated: {reminder_time}")
    elif state_name == "reminder_time_ampm":
        reminder_time_ampm = payload.get("state_value", "")
        if reminder_time_ampm == "PM" and reminder_time.hour < 12:
            reminder_time = reminder_time.replace(hour=reminder_time.hour + 12)
            logger.info(f"Reminder time updated: {reminder_time}")
    elif state_name == "brightness":
        brightness_value = int(payload.get("state_value", ""))
        logger.info(f"Brightness updated: {brightness_value}")
        try:
            subprocess.run(
                f'echo {brightness_value} | sudo tee /sys/class/backlight/4-0045/brightness',
                shell=True,
                check=True
            )
            pass
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to set brightness: {e}")
        logger.info(f"Mapped brightness value: {brightness_value}")
    
    if state_name.startswith("reminder_time"):
        reminder_time = reminder_time.replace(second=0, microsecond=0)
        logger.info(f"Reminder time updated: {reminder_time}")
        socketio.emit('reminder_time_update', {"time": reminder_time.strftime('%H:%M'), "ampm": reminder_time_ampm})

def days_remaining():
    global days_remaining

    today = datetime.now().date()
    delta = today - start_date

    days_remaining = study_duration - delta.days

    if days_remaining < 0:
        days_remaining = 0

def publish_heartbeat():
    while True:
        # Publish heartbeat
        time.sleep(30)  # Publish heartbeat every 30 seconds

# Start heartbeat thread
threading.Thread(target=publish_heartbeat, daemon=True).start()

# TODO: Add dialogue message handler to event dispatcher
# message handler
def dialogue_message_handler(message):
    # Format the message
    formatted_message = {
        "sender": message.get("sender", "robot"),  # Default sender is robot
        "content": message.get("content", ""),
        "message_type": message.get("message_type", ""),
        "time": message.get("time", time.strftime("%H:%M %p | %B %d"))
    }
    # Add to chat history
    chat_history.append(formatted_message)
    logger.info(f"New message: {formatted_message}")
    # Emit the message to connected clients
    socketio.emit('new_message', formatted_message)

# Register the MQTT message handler
communication_interface.message_callback = dialogue_message_handler

@app.route('/')
def home():
    _register_event_handlers()
    serviceStatus = communication_interface.get_system_status()
    still_loading = False
    print(f"serviceStatus: {serviceStatus}")
    for key, value in serviceStatus.items():
        if value != "set_up":
            still_loading = True
    if still_loading or serviceStatus == {}:
        return render_template('system_boot_up.html')
    return render_template('home.html', implementationIntention=implementationIntention, days_remaining=days_remaining, reminder_time=reminder_time.strftime('%H:%M'), reminder_time_ampm=reminder_time_ampm)

@app.route('/wake_up_screen', methods=['POST'])
def wake_up_screen():
    communication_interface.wake_up_screen()
    return jsonify({'status': 'success', 'message': 'Screen woken up'}), 200

@socketio.on('ui_ready')
def handle_ui_ready():
    logger.info("UI is ready, sending system status update...")

    # Publish the UI status to the MQTT broker
    # communication_interface.publish_UI_status("set_up")

@app.route('/reconnect', methods=['POST'])
def reconnect():
    logger.info("Received a reconnect request")
    communication_interface.publish_reconnect_request("UI_error_message")
    
    # Trigger the reconnect process asynchronously (e.g., send a message to a worker or robot controller)
    # Example: robot_controller.start_reconnect() or publish an MQTT message
    success = True  # Simulated for this example
    
    return jsonify({"status": "initiated", "message": "Reconnection process started"}), 202

@app.route('/check_in')
def check_in():
    global chat_history
    chat_history = []
    global check_in_start_time
    check_in_start_time = datetime.now()
    return render_template('check_in.html', chat_history=chat_history)

@app.route('/save-checkin', methods=['POST'])
def save_check_in():
    try:
        # Initialize lists to store questions and responses
        questions = []
        responses = []
        
        # Iterate through chat history to extract questions and responses
        for message in chat_history:
            print(f"Message: {message}")
            if message.get("message_type") == "question":
                print(f"Question: {message.get('content')}")
                questions.append(message.get("content"))
            elif message.get("message_type") == "response":
                print(f"Response: {message.get('content')}")
                responses.append(message.get("content"))
        
        # Ensure that questions and responses are aligned
        if len(questions) != len(responses):
            logging.warning("Mismatch between number of questions and responses. Data may be incomplete.")
        
        # Combine questions and responses into a dictionary
        chat_data = [{"question": q, "response": r} for q, r in zip(questions, responses)]
        print(f"Check-in data: {chat_data}")

        # Add metadata to the check-in data
        check_in_end_time = datetime.now()
        check_in_duration = (check_in_end_time - check_in_start_time).total_seconds()
        print(f"Check-in duration: {check_in_duration}")
        check_in_data = {
            "check_in_time": check_in_start_time.strftime("%H:%M:%S"),
            "check_in_duration_seconds": check_in_duration,
            "responses": chat_data}
        
        # Publish the check-in data to the MQTT broker
        communication_interface.save_check_in(check_in_data)
        logging.info("Check-in data sent to the database via MQTT.")
        
        return jsonify({"status": "success", "message": "Check-In data saved successfully"}), 200
    except Exception as e:
        logging.error(f"Error while saving Check-In: {e}")
        return jsonify({"status": "error", "message": "Failed to save Check-In data"}), 500

@app.route('/history')
def history():
    # Step 1: Load history page and show loading spinner
    # Step 2: Fetch history data from database
    # Step 3: Display history data on page and hide loading spinner
    communication_interface.request_study_history()
    return render_template('history.html')

@app.route('/settings')
def settings():
    communication_interface.configuration_controller("start")
    return render_template(
        'settings.html',
        time = reminder_time.strftime('%H:%M'),
        ampm = reminder_time_ampm,
        volume_button_states=volume_button_states,
        voice_button_states=voice_button_states,
        robot_enabled=os.getenv("ROBOT_ENABLED") == "True",
    )

@app.route('/exit_settings', methods=['POST'])
def exit_settings():
    logger.info("Exiting settings...")
    communication_interface.configuration_controller("end")
    return jsonify({'status': 'success', 'message': 'Settings exited'}), 200

@app.route('/action_page', methods=['POST'])
def process_form():
    hour = request.form.get('hour')
    minute = request.form.get('minute')
    ampm = request.form.get('ampm')
    
    formatted_time = f"{hour}:{minute} {ampm}"
    logger.info(f"Received time: {formatted_time}")

    communication_interface.set_reminder_time(hour, minute, ampm)

    return jsonify({'status': 'success', 'time': formatted_time}), 200

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
        # Call the function in robot_control
        communication_interface.change_volume(button_name)
    return jsonify({'status': 'success'})

@app.route('/brightness/<int:brightness_value>')
def brightness_slider_change(brightness_value):
    # Map the brightness value from range 1-100 to 0-31
    mapped_value = int(1 + ((31 - 1) / (100 - 1)) * (brightness_value - 1))


    logger.info(f"Brightness slider changed: {brightness_value}")
    try:
        # Update the brightness using the mapped value
        subprocess.run(
            f'echo {mapped_value} | sudo tee /sys/class/backlight/4-0045/brightness',
            shell=True,
            check=True
        )
        communication_interface.change_brightness(mapped_value)
        # Return a success response
        return f"Brightness successfully set to {mapped_value}", 200
    except subprocess.CalledProcessError as e:
        # Return an error response if the command fails
        payload = {
            "error": f"Failed to set brightness: {e}",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "service_name": "user_interface"
        }
        dispatcher.dispatch_event("send_service_error", payload)
        return f"send_service_error: {e}", 500

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/start_check_in', methods=['POST'])
def start_check_in():
    chat_history = []
    # Start the check-in process
    communication_interface.start_check_in()
    return jsonify({'status': 'success', 'message': 'Check-In command sent'})
# Asynchronous response returning true but the message channel closed before response received

@app.route('/update_connection_status', methods=['POST'])
def update_connection_status():
    global connection_status
    data = request.get_json()
    key = data.get('key')
    status = data.get('status')
    
    if key in connection_status:
        connection_status[key] = status
        return jsonify({'status': 'success', 'message': f'{key} status updated.'}), 200
    
    return jsonify({'status': 'error', 'message': 'Invalid key provided.'}), 400

@app.route('/get_connection_status')
def get_connection_status():
    return jsonify(connection_status)

def handle_status_update(data):
    global connection_status
    key = data.get('key')
    status = data.get('status')
    logger.info(f"Received status update for {key}: {status}")
    
    if key in connection_status:
        connection_status[key] = status
        socketio.emit('connection_status_update', connection_status)

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
