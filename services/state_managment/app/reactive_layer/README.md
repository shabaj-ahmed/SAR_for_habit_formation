# Reactive Layer Interaction

Behavior Classes in behavior.py

Each Behavior class receives sensory data, processes it, and generates an output or action.
The behaviors are designed to operate independently, producing outputs based on the current sensory data.
Arbitrator Class in arbitrator.py

The Arbitrator receives the outputs from each behavior.
It decides which behavior’s output should be allowed to control the robot based on priority or other criteria
