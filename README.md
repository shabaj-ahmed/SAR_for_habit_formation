This code is for the development of a study in which a Socially Assistive Robot (SAR) is used to aid in fostering long-term healthy behaviours. The main focus of this study is to understand how SARs can promote lifestyle choices that can improve both lifespan and health span. My research explores the psychological and behavioural effects of prolonged robot interaction and how SARs can be used to encourage positive behavioural changes. Unlike traditional methods that rely on reflective behavioural change, my research focuses on habitual behaviour modification. The aim is to empower individuals to adopt healthier routines naturally. Through my work, I hope to contribute to the development of robots that can coexist with humans and actively support their health and success.

# Set up

## Avtivate python enviroment from the root directory

source .venv/bin/activate

# Install libraries

pip3 install -r requirements

# Install Mosquitto MQTT broker

Set up the MQTT client so that messages are propagated properly
Start Mosquitto server using the following

## MacOS

brew install mosquitto
brew services start mosquitto

# Robot Hardware that will be used

- Picoh
- Raspberry Pi
- Micro SD card
- Raspberry pi camera
- Microphone
- 7 inch touch screen display
- Speaker
- Two 5v power supplies

# Sensor input that will be used

- Microphone
- User interface
- Camera
