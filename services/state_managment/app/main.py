import time
from .mqtt_client import MQTTClient
from .reactive_layer.reactive_arbitrator import ReactiveLayer
# from .deliberate_layer.behaviour_tree import BehaviorTree
from .deliberate_layer.finite_state_machine import FSM

# Initialise MQTT client
mqtt_client = MQTTClient(broker_address='localhost', port=1883)

# Instantiate High-Level FSM, Behavior Tree, and Reactive Layer
fsm = FSM(initial_state='Sleep')
reactive_layer = ReactiveLayer(mqtt_client=mqtt_client, fsm=fsm)
# behavior_tree = BehaviorTree(fsm)

# Loop interval
LOOP_INTERVAL = 0.1  # Adjust as per your requirement

if __name__ == "__main__":
    try:
        while True:
            # Check reactive state machine for critical conditions and trigger reactive behaviors
            reactive_layer.detect_critical_condition()

            # If the FSM is in the 'Active' state, run behaviour tree
            # if fsm is 'ActiveMode':
            #       run behaviour tree

            # Pause before the next loop iteration
            time.sleep(LOOP_INTERVAL)
    except KeyboardInterrupt:
        print("Shutting down...")
