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

# Installation and set up
## Prerequisites
Before running the project, ensure you have:
- Debian Bookworm installed on your Raspberry Pi 5.
- Put google speech key.json in ~/.google-cloud directory
- Ensure that the Vector robot authentication certificate is located in the ~/.anki_vector directory and the sdk_config.ini is configured correctly
- API keys and hardware specifications are properly configured in the .env file (located in the configurations folder).

## Run Installation Script
The setup process is automated using a Bash script.
1. Ensure Correct File Path
set up the project in the following location:

```
~/Documents/hri_study/SAR_FOR_HABIT_FORMATION
```

Or you will have to modify the bash script

2. Run the setup script
Navigate to the project root directory and run:

```
$ chmod +x bash.sh
$ ./bash.sh
```

This script will:
- Pull the latest code from the repository.
- Install Mosquitto (MQTT broker) and all required dependencies.
- Create a Python virtual environment
- Install the required dependencies
- Update the Vector SDK
If successful a chromium window should open in full screen

## Hardware used
- Digital Dream Labs Vector 2.0,
- Raspberry Pi 5 8 GB,
- Micro SD card with Debian Bookworm installed,
- USB microphone,
- Raspberry Pi touch display 2,
- 5V power supplies,
- Mobile WiFi module

# License
This project is licensed under the MIT License.

# Contact
If you have questions or need assistance, feel free to reach out.
