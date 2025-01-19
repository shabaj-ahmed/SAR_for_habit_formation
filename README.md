This code is for developing a study in which a Socially Assistive Robot (SAR) is used to aid in fostering long-term healthy behaviours. The main focus of this study is to understand how SARs can promote healthy lifestyle choices that can improve both lifespan and health span. My research explores the psychological and behavioural effects of prolonged robot interaction and how SARs can be used to encourage positive behavioural changes. Unlike traditional methods that rely on reflective behavioural change, my research focuses on habitual behaviour modification. The aim is to empower individuals to adopt healthier routines naturally. Through my work, I want to contribute to the development of robots that can coexist with humans and actively support their health and success.

Current development will be done in the _development branch_ and published on the _main branch_ when it is ready for beta testing.

## Control flow

This code is built using a microservice architecture to ensure scalability. To make each service as stateless as possible, all service states and configurations are stored in a centralised database and loaded upon request. MQTT is used as the message broker to exchange messages and commands between the services.

I have used a centralised control system that uses state machines to orchestrate behaviour, ensuring that the robot's behaviour is coherent and appropriate. The robot's behaviour is divided into three layers:
1. High-level finite state machine (FSM),
2. Behaviour tree for orchestrating complex behaviour,
3. Reactive layer for responding to environmental stimuli.
   This architecture provides a clear separation between reactive and deliberative actions while ensuring real-time responsiveness.

- Centralised Decision Making: The state machines act as central points for decision-making, ensuring that the robot's state is always considered before any action is taken.
- Simplified Debugging and Maintenance: With all decisions passing through a known point, tracking issues and understanding behaviour becomes more manageable.
- Consistency in Behaviour: Ensures that the robot's actions are always consistent with its current state, as defined by the state machines.

However, this approach may introduce latency since the state machines must process every piece of data synchronously before any action is taken. Nevertheless, we chose a centralised approach for decision-making over a direct-to-service invocation since this system is not time-sensitive or safety-critical, and a little latency can be tolerated.

# Set up

Activate the Python environment from the root directory:
`source .venv/bin/activate`

## Install libraries

`pip3 install -r requirements`

## Install Mosquitto MQTT broker

Set up the MQTT client so that messages are propagated properly
Start Mosquitto server using the following

### MacOS

`brew install mosquitto`
`brew services start mosquitto`

## Run bash
In the root of the project there is a .bach.sh file, which will set up and run the project.

# Hardware used

- Digital Dream Labs Vector 2.0,
- Raspberry Pi 5 8 GB,
- Micro SD card,
- USB microphone,
- Raspberry Pi touch display 2,
- 5V power supplies,
- Mobile WiFi module

## Sensors

- Microphone
- Touch interface to interact with user interface

## Actuators

- Speaker
