# SAR for Habit Formation

This repository contains the codebase for a study investigating how a Socially Assistive Robot (SAR) can foster long-term healthy behaviours. The primary focus is to explore how SARs can promote healthy lifestyle choices that improve both lifespan and healthspan. This research examines the psychological and behavioural effects of prolonged robot interaction and how SARs can encourage positive behaviour changes through habit formation.

## Project Overview
This project aims to contribute to the development of robot coaches that can coexist with humans and actively support their health and well-being. The study is structured around:
- A daily check-in that is based on motivational interviewing principles and uses decision tree driven dialogue.
- A microservice architecture that ensures scalability and modularity.
- A state-driven control system using finite state machines (FSM) and behaviour trees.

## Branches
- development branch – Active development takes place here.
- main branch – Stable releases and beta versions are published here.

## System Architecture
This project follows a microservice architecture where each service operates statelessly by storing configurations and states in a centralised database. MQTT is used as a message broker to handle inter-service communication.

The robot's behavior is governed by a three-layered control system:
1. High-Level Finite State Machine (FSM) – Manages primary system states.
2. Behavior Tree (BT) – Orchestrates complex behaviours.
3. Reactive Layer – Handles immediate responses to environmental stimuli.

This architecture provides a clear separation between reactive and deliberative actions while ensuring near real-time responsiveness.

### Advantages of This Approach
- Centralised Decision Making: The state machines act as central points for decision-making, ensuring that the robot's state is always considered before any action is taken.
- Simplified Debugging and Maintenance: With all decisions passing through a known point, tracking issues and understanding behaviour becomes more manageable.
- Consistency in Behaviour: Ensures predictable and logical interactions.

Note: This approach introduces some latency due to centralised processing. However, since this study is not time-sensitive or safety-critical, minor latency is acceptable.

---

# Installation and set up
The following are instructions to replicate our study. If you would like to collaborate or need help setting up your won system please get in contact with me.

## Hardware used
- Digital Dream Labs Vector 2.0,
- Raspberry Pi 5 8 GB,
- Micro SD card with Debian Bookworm installed,
- USB microphone,
- Raspberry Pi touch display 2,
- 5V power supplies,
- TP-Link M7350 4G LTE Mobile Wi-Fi Router with pre-paid data only SIM

All devices were powered by the Raspberry Pi's USB ports

## Prerequisites
Before running the project, ensure you have:
- Debian Bookworm installed on your Raspberry Pi 5.
- Ensure that the [Vector robot authentication](#authenticate-the-vector-robot) certificate is located in the ~/.anki_vector directory and the sdk_config.ini is configured correctly.
- Create a .env file in the /configuration directory using the example.env as a template
- Sign up for Google Cloud and create a project with speech-to-text. Retrieve the JSON API key and put google speech key.json in ~/.google-cloud directory. Add the file path to the Google API key to .env file.
- Add hardware configuration properties to the .env file

## Run Installation Script
The setup process is automated using a Bash script.
1. Ensure Correct File Path
set up the project in the following location:

```
~/Documents/hri_study
```

Or you will have to modify the bash script

2. clone the repository here using
Open a terminal and navigate to the hri_study directory and clone this repository

```
$ cd ~/Documents/hri_study
$ git clone https://github.com/msahmed1/SAR_for_habit_formation.git
```

3. Run the setup script
Before running the bash.sh ensure that the [prerequisites](#prerequisites) have are satisfied. Following this, navigate to the project root directory and make bash.sh executable before running it:

```
$ cd ~/Documents/hri_study/SAR_for_habit_formation
$ chmod +x bash.sh
$ ./bash.sh
```

This script will:
- Pull the latest code from the repository (continuous deployment).
- Install and start the Mosquitto MQTT broker
- Create a Python virtual environment
- Install the required packages and dependencies
- Update the Vector SDK
- Launch all services

If successful a chromium window should open in full-screen

---

# Authenticate the vector robot
The following steps have been used to authenticate a vector robot on a Raspberry Pi 5 running Debian version: 12 (bookworm). Ensure you have a WiFi network with internet access that allows devices on the same network to communicate with each other. The university Eduroam network will not work for this. You will then need to install and set up [Wire Pod](https://github.com/kercre123/wire-pod?tab=readme-ov-file), an open-source server for activating the vector robot. Open the terminal on the Pi and run the following:

```
cd ~
git clone https://github.com/kercre123/wire-pod --depth=1
cd ~/wire-pod
sudo STT=vosk ./setup.sh
sudo ./chipper/start.sh
```

Once it has completed installing, in the terminal you should see something similar to:

```
Initializing variables
SDK info path: /home/kerigan/.anki_vector/
API config JSON created
Initiating vosk voice processor with language 
Loading plugins
Wire-pod is not setup. Use the webserver at port 8080 to set up wire-pod.
Starting webserver at port 8080 (http://localhost:8080)
Starting SDK app
Starting server at port 80 for connCheck
Configuration page: http://192.168.1.221:8080
```

Open a browser and head to the **Configuration page**. In the example above this is http://192.168.1.221:8080

Press and hold the Vecrots power button for 15 seconds until you see a white LED and then release. Now open an incognito browser and head to https://wpsetup.keriganc.com/

Follow the instructions on the webpage to connect to the vector, you may have to attempt the connection a few times before it works.

Once the vector is activated, copy the serial number, located on the bottom of the vector into the .evn file.

# License
This project is licensed under the MIT License.

# Contact
If you have questions or need assistance, feel free to reach out.
