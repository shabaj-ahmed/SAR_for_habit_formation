#!/bin/bash

# Define variables
PROJECT_DIR="/home/pi/Documents/hri_study/SAR_for_habit_formation"  # CHANGE THIS TO THE ROOT OF THE PROJECT DIRECTORY
VENV_DIR="$PROJECT_DIR/.venv"         # Path to your virtual environment
REQUIREMENTS_FILE="$PROJECT_DIR/requirements.txt"
ENV_FILE="$PROJECT_DIR/configurations/.env"
SERVICES_DIR="$PROJECT_DIR/services" # Path to your services directory
FLASK_APP_URL="http://127.0.0.1:5000"  # Change this if using a custom host/port
BROWSER_CMD="chromium-browser --start-fullscreen"  # Command to open browser in full screen

# MQTT broker setup
MQTT_BROKER_SERVICE="mosquitto"

# Trap SIGINT and SIGTERM to clean up properly
cleanup() {
    echo "Performing cleanup..."
    echo "Stopping background processes..."
    pkill -P $$  # Kill all child processes of this script
    echo "Deactivating virtual environment..."
    deactivate 2>/dev/null || true  # Deactivate the virtual environment if active
    echo "Cleanup complete. Exiting."
    exit 0
}
trap cleanup SIGINT SIGTERM

# Debug: Print paths
echo "Project Directory: $PROJECT_DIR"
echo "Environment File: $ENV_FILE"
echo "Script Path: $SCRIPT_PATH"

# Change to the project directory
# Change to the project directory
if cd "$PROJECT_DIR"; then
    echo "Pulling latest changes from the remote repository..."
    git pull
    if [ $? -ne 0 ]; then
        echo "Error: 'git pull' failed. Please check the repository and resolve any issues."
        exit 1
    fi
else
    echo "Error: Cannot change to project directory $PROJECT_DIR. Exiting."
    exit 1
fi


start_mqtt_broker() {
    echo "Starting MQTT broker..."
    sudo apt install $MQTT_BROKER_SERVICE mosquitto-clients
    sudo systemctl start $MQTT_BROKER_SERVICE
    if [ $? -ne 0 ]; then
        echo "Failed to start MQTT broker. Please check your setup."
        exit 1
    fi
}

activate_virtualenv() {
    echo "Checking if virtual environment exists..."
    
    if [ ! -d "$VENV_DIR" ]; then
        echo "Virtual environment not found. Creating one..."
        python3 -m venv "$VENV_DIR"

        if [ $? -ne 0 ]; then
            echo "Error: Failed to create virtual environment. Exiting."
            exit 1
        fi

        echo "Virtual environment created successfully."
    fi

    echo "Activating virtual environment..."
    source "$VENV_DIR/bin/activate"
    if [ $? -ne 0 ]; then
        echo "Failed to activate virtual environment. Please check your setup."
        exit 1
    fi
}

install_requirements() {
    echo "Ensure system dependencies for PyAudio are installed"
    sudo apt-get install -y portaudio19-dev python3-pyaudio
    
    echo "Installing required libraries..."
    pip install -r "$REQUIREMENTS_FILE"
    if [ $? -ne 0 ]; then
        echo "Failed to install requirements. Please check your requirements.txt file."
        exit 1
    fi
}

update_anki_vector_library() {
    ANKI_VECTOR_DIR="$VENV_DIR/lib/python3.11/site-packages/anki_vector"
    VECTOR_SDK_UPDATES_DIR="$PROJECT_DIR/vector_sdk_updates"

    echo "Updating anki_vector library..."

    # Ensure the anki_vector directory exists
    if [ -d "$ANKI_VECTOR_DIR" ]; then
        # Remove the messaging directory and specified files
        echo "Removing old files and folders.."
        rm -rf "$ANKI_VECTOR_DIR/messaging"
        rm -f "$ANKI_VECTOR_DIR/connection.py"
        rm -f "$ANKI_VECTOR_DIR/events.py"

        # Copy new files from vector_sdk_updates
        echo "Copying updated files and folders..."
        cp -r "$VECTOR_SDK_UPDATES_DIR/messaging" "$ANKI_VECTOR_DIR/"
        cp "$VECTOR_SDK_UPDATES_DIR/connection.py" "$ANKI_VECTOR_DIR/"
        cp "$VECTOR_SDK_UPDATES_DIR/events.py" "$ANKI_VECTOR_DIR/"

        echo "anki_vector library updated successfully."
    else
        echo "Error: anki_vector library not found in virtual environment."
        exit 1
    fi
}


export_env_variables() {
    if [ ! -f "$ENV_FILE" ]; then
        echo "No .env file found. Skipping..."
        return
    else
        echo "Exporting environment variables..."
        set -o allexport
        source "$ENV_FILE"
        set +o allexport
    fi
}

# Start all services
start_services() {
    echo "Starting services..."
    declare -a pids=()  # Array to store PIDs of background processes

    for service_dir in "$SERVICES_DIR"/*; do

        if [ "$service_dir" == "$SERVICES_DIR/user_interface" ]; then
            export FLASK_APP=services.user_interface.main
            export FLASK_ENV=production

            flask run --host=0.0.0.0 &
            flask_pid=$!  # Capture Flask process PID
            pids+=("$flask_pid")  # Add PID to the array
            echo "Flask started with PID $flask_pid. Logs available at flask.log."
            sleep 2  # Give Flask some time to start

            echo "Opening browser in full screen..."
            $BROWSER_CMD "$FLASK_APP_URL" &
            browser_pid=$!  # Capture browser process PID
            pids+=("$browser_pid")  # Add PID to the array

            continue
        fi

        entry_point="$service_dir/app/main.py"

        if [ -f "$entry_point" ]; then
            echo "Starting service in $service_dir..."
            python "$entry_point" &
            service_pid=$!  # Capture service process PID
            pids+=("$service_pid")  # Add PID to the array
        else
            echo "No main.py found in $service_dir/app. Skipping..."
        fi
    done

    # Wait for all services to start
    echo "Waiting for services to start..."
    wait "${pids[@]}"
}

# Main script
echo "Initializing setup..."

# Step 1:
start_mqtt_broker

# Step 2:
activate_virtualenv

# Step 3:
install_requirements

# Step 4:
update_anki_vector_library

# Step 5:
export_env_variables

# Step 6:
start_services

echo "All services are running. Press [ENTER] to stop the services and exit."

# Keep the script running indefinitely
while true; do
    sleep 60
done

# Stop all background processes
cleanup