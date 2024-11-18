import time
from mqtt_client import MQTTClient
import threading
from queue import Queue
from reactive_layer.subsumption_layer import ReactiveLayer
import deliberate_layer.finite_state_machine as fsm
from deliberate_layer.behaviour_tree import BehaviorTree

# Initialise a shared event queue for communication
subsumption_layer_event_queue = Queue()
finite_state_machine_event_queue = Queue()
behavior_tree_event_queue = Queue()

# Initialise MQTT client
mqtt_client = MQTTClient(broker_address='localhost', port=1883)

# Instantiate High-Level FSM, Behavior Tree, and Reactive Layer
reactive_layer = ReactiveLayer(mqtt_client=mqtt_client, event_queue=subsumption_layer_event_queue)
finite_state_machine_layer = fsm.FSM(mqtt_client=mqtt_client, initial_state='Sleep', subsumption_layer_event_queue=subsumption_layer_event_queue, finite_state_machine_event_queue=finite_state_machine_event_queue, behavior_tree_event_queue=behavior_tree_event_queue)
deliberate_layer = BehaviorTree(mqtt_client=mqtt_client, finite_state_machine_event_queue=finite_state_machine_event_queue, behavior_tree_event_queue=behavior_tree_event_queue)

# Loop interval
LOOP_INTERVAL = 0.1

# Define each layer's main function to run in its own thread
def subsumption_layer():
    try:
        while True:
            reactive_layer.detect_critical_condition()
            time.sleep(LOOP_INTERVAL)
    except KeyboardInterrupt:
        print("Shutting down subsumption layer...")

def finite_state_machine():
    try:
        while True:
            finite_state_machine_layer.update()            
            time.sleep(LOOP_INTERVAL)
    except KeyboardInterrupt:
        print("Shutting down FSM...")

def behavior_tree():
    try:
        while True:
            deliberate_layer.update()
            time.sleep(LOOP_INTERVAL)
    except KeyboardInterrupt:
        print("Shutting down behavior tree...")

if __name__ == "__main__":
    subsumption_thread = threading.Thread(target=subsumption_layer, daemon=False)
    fsm_thread = threading.Thread(target=finite_state_machine, daemon=False)
    behavior_tree_thread = threading.Thread(target=behavior_tree, daemon=False)

    subsumption_thread.start()
    fsm_thread.start()
    behavior_tree_thread.start()

    # Keep the main thread alive to wait for KeyboardInterrupt
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
