# Centralised decision-making logic

The robot's services are activated and managed by a centralised controller. It uses a hybrid architecture that consists of a reactive and deliberate layer. The reactive layer follows the subsumption design architecture, while the deliberate layer uses a finite state machine and a behavior tree to handle complex hierarchical or stateful behaviours. Both architectures work together to provide a flexible and capable control system.

1. The Reactive Layer immediately responds to critical conditions and can influence the high-level FSM to manage the overall state of the robot.
2. The High-Level FSM determines which behaviours should be active or inactive based on the robot's overarching state and signals from the reactive layer.
3. Behavior Trees execute specific behaviours and operate under the FSM's high-level state.

This architecture ensures the capability for concurrent, complex behaviours while providing a clear, high-level state representation. It also ensures that safety and reactive behaviours are promptly executed. This structured approach facilitates manageability, scalability, and safety in the robot.

In this centralised approach all the data is passed through the state machine i.e. micro services interact with the state machine only and edge services are the ones that interact with the sensors and actuators.

![High level state machine diagram](.../documentation/state_machine_architecture_diagram_V1.png)
