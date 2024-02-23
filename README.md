This code is for developing a study in which a Socially Assistive Robot (SAR) is used to aid in fostering long-term healthy behaviours. The main focus of this study is to understand how SARs can promote lifestyle choices that can improve both lifespan and health span. My research explores the psychological and behavioural effects of prolonged robot interaction and how SARs can be used to encourage positive behavioural changes. Unlike traditional methods that rely on reflective behavioural change, my research focuses on habitual behaviour modification. The aim is to empower individuals to adopt healthier routines naturally. Through my work, I want to contribute to the development of robots that can coexist with humans and actively support their health and success.

# How To use

Current development will be done in the _development branch_ and published on the _main branch_ when it is ready for production.

## Control flow

This code is built using a microservice architecture to ensure scalability. To make each service as stateless as possible, all service states and configurations are stored in a centralised database and loaded upon request. MQTT is used as the message broker to exchange messages, commands, and images between the services.

I have used a centralised control system that uses state machines to orchestrate behaviour, ensuring that the robot's behaviour is coherent and appropriate. The robot's behaviour is divided into three layers:

1. High-level finite state machine (FSM),
2. Behaviour tree for planned actions,
3. Reactive layer for responding to environmental stimuli.
   This architecture provides a clear separation between reactive and deliberative actions while ensuring real-time responsiveness.

Centralised data processing through state machines is used, meaning that all data and signals first pass through the state machines before being processed by any service. This approach has several benefits, including:

- Centralised Decision Making: The state machines act as central points for decision-making, ensuring that the robot's state is always considered before any action is taken.
- Simplified Debugging and Maintenance: With all decisions passing through a known point, tracking issues and understanding behaviour becomes more manageable.
- Consistency in Behaviour: Ensures that the robot's actions are always consistent with its current state, as defined by the state machines.

However, this approach may introduce latency since the state machines must process every piece of data before any action is taken. Nevertheless, we chose a centralised approach for decision-making over a direct-to-service innovation since this system is not time-sensitive or safety-critical, and latency can be tolerated. If timing and safety were critical, the microservices could bypass the state machine and communicate directly.

# Set up

Activate the Python environment from the root directory:
`source .venv/bin/activate`

# Install libraries

`pip3 install -r requirements`

# Install Mosquitto MQTT broker

Set up the MQTT client so that messages are propagated properly
Start Mosquitto server using the following

## MacOS

`brew install mosquitto`
`brew services start mosquitto`

# Robot Hardware that will be used

I am currently operating a Picoh robot using a Raspberry Pi with an attached touchscreen LCD. This controller is designed for a socially assistive robot, which means that it is not equipped with any physical movement abilities or the ability to interact with the environment. The robot's functions are limited to expressing emotions and conversing with individuals. The following components are used in the setup:

- Picoh,
- Raspberry Pi 5,
- Micro SD card,
- Raspberry Pi camera 3,
- USB microphone,
- 7-inch touchscreen display,
- USB speaker,
- two 5V power supplies,
- Mobile WiFi module,
- Mechanical switch.

# Sensor input that will be used

- Microphone
- User interface
- Camera
