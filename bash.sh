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
cd "$PROJECT_DIR" || { echo "Error: Cannot change to project directory $PROJECT_DIR"; exit 1; }


start_mqtt_broker() {
    echo "Starting MQTT broker..."
    sudo systemctl start $MQTT_BROKER_SERVICE
    if [ $? -ne 0 ]; then
        echo "Failed to start MQTT broker. Please check your setup."
        exit 1
    fi
}

activate_virtualenv() {
    echo "Activating virtual environment..."
    source "$VENV_DIR/bin/activate"
    if [ $? -ne 0 ]; then
        echo "Failed to activate virtual environment. Please check your setup."
        exit 1
    fi
}

install_requirements() {
    echo "Installing required libraries..."
    pip install -r "$REQUIREMENTS_FILE"
    if [ $? -ne 0 ]; then
        echo "Failed to install requirements. Please check your requirements.txt file."
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
    for service_dir in "$SERVICES_DIR"/*; do

        if [ "$service_dir" == "$SERVICES_DIR/user_interface" ]; then
            export FLASK_APP=main
            export FLASK_ENV=production

            flask run --host=0.0.0.0 &
            flask_pid=$!  # Capture Flask process PID
            echo "Flask started with PID $flask_pid. Logs available at flask.log."
            sleep 2  # Give Flask some time to start

            echo "Opening browser in full screen..."
            $BROWSER_CMD "$FLASK_APP_URL" &
            browser_pid=$!  # Capture browser process PID

            continue
        fi

        entry_point="$service_dir/app/main.py"

        if [ -f "$entry_point" ]; then
            echo "Starting service in $service_dir..."
            python "$entry_point" &
        else
            echo "No main.py found in $service_dir/app. Skipping..."
        fi
    done
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
export_env_variables

# Step 5:
start_services

echo "All services are running. Press [ENTER] to stop the services and exit."

# Wait for user input
read -r

# Stop all background processes
cleanup