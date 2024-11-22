#!/bin/bash

# Define variables
PROJECT_DIR="~/Documents/hri_study/SAR_for_habit_formation"  # CHANGE THIS TO THE ROOT OF THE PROJECT DIRECTORY
VENV_DIR="$PROJECT_DIR/venv"         # Path to your virtual environment
SERVICES_DIR="$PROJECT_DIR/services" # Path to your services directory
REQUIREMENTS_FILE="$PROJECT_DIR/requirements.txt"

# MQTT broker setup
MQTT_BROKER_SERVICE="mosquitto"

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

# Start all services
start_services() {
    echo "Starting services..."
    for service_dir in "$SERVICES_DIR"/*/; do
        entry_point="$service_dir/app/src/main.py"
        if [ -f "$entry_point" ]; then
            echo "Starting service in $service_dir..."
            python "$entry_point" &
        else
            echo "No main.py found in $service_dir/app/src. Skipping..."
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
start_services

echo "All services are running. Press [ENTER] to stop the services and exit."

# Wait for the user to press [ENTER]
read -p ""

# Stop services gracefully
echo "Stopping services..."
for pid in $(jobs -p); do
    echo "Stopping process $pid..."
    kill $pid
done

echo "Cleanup complete. Exiting."
