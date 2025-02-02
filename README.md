# SAR for Habit Formation

This repository contains the codebase for a study investigating how a Socially Assistive Robot (SAR) can foster long-term healthy behaviours. The primary focus is to explore how SARs can promote healthy lifestyle choices that improve both lifespan and healthspan. This research examines the psychological and behavioural effects of interacting with a SAR for three weeks and how SARs can encourage positive behaviour changes through habit formation.

This is the first attempt at an ecologically valid long-term interaction with a robot for behaviour change. The codebase has been developed as part of a PhD research project, with a focus on designing a reliable and scalable system that enables coaching through decision-tree-driven dialogues. For a detailed project description, please refer to the [project WiKi](https://github.com/msahmed1/SAR_for_habit_formation/wiki)


## Project Overview

This project aims to contribute to the development of robot coaches that can coexist with humans and actively support their health and well-being. The study is structured around:
- A daily check-in that is based on motivational interviewing principles and uses decision tree driven dialogue.
- A microservice architecture that ensures scalability and modularity.
- A state-driven control system using finite state machines (FSM) and behaviour trees.


## Interaction design

During the three-week study, participants interact with the SAR twice daily:
- Morning Reminder: The robot provides a brief motivational prompt based on the participant’s implementation intention.
- Evening Check-In: A 3–5 minute structured dialogue based on motivational interviewing principles to track progress, address challenges, and encourage reflection. A decision tree controls the conversational flow, adapting questions based on responses.


## Branches

- **Development** branch – Active development takes place here.
- **Master** branch – Stable releases and beta versions are published here.

For the final implementation, a Bash script automates code updates by pulling the latest version from the repository, enabling a continuous deployment setup.


# System Architecture

This project follows a microservice architecture where each service operates statelessly by storing configurations and states in a centralised database. MQTT is used as a message broker to handle inter-service communication.

The robot's behaviour is governed by a two-layered control system:
1. Reactive Layer – Handles immediate responses to environmental stimuli.
2. Deliberate Layer - High-Level Finite State Machine to manage primary system states and a behaviour Tree to orchestrate complex behaviours.

This architecture provides a clear separation between reactive and deliberative actions while ensuring near real-time responsiveness.


## Advantages of This Approach

- Centralised Decision Making: The state machines act as central points for decision-making, ensuring that the robot's state is always considered before any action is taken.
- Simplified Debugging and Maintenance: With all decisions passing through a known point, tracking issues and understanding behaviour becomes more manageable.
- Consistency in Behaviour: Ensures predictable and logical interactions.

Note: This approach introduces some latency due to centralised processing. However, since this study is not time-sensitive or safety-critical, minor latency is acceptable.


# Installation and set up

The following are instructions on how to replicate our study. If you would like to collaborate or need help with replicating this setup please get in contact with me.


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
- This project uses Google Cloud for Speech-to-Text (STT) recognition. We found its accuracy to be much better than local STT. To use this project as it is you will need to sign up for Google Cloud and create a project with speech-to-text. Retrieve the JSON API key and create the directory ~/.google-cloud to store it in. Add the file path to the Google API key to .env file.
- Add the remaining hardware configuration properties to the .env file


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
- Update the Vector SDK Library by updating the Protobuf files and parching broken code
- Launch all services

If successful a chromium window should open in full-screen


# License

This project is licensed under the MIT License.


# Contact

If you have questions or need assistance, feel free to reach out.
