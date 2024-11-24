import time
import threading
from queue import Queue
from src.reactive_layer.reactive_layer import ReactiveLayer
import src.deliberate_layer.finite_state_machine as fsm
from src.deliberate_layer.behaviour_tree import BehaviorTree
from app.custom_logging.logging_config import setup_logger
import logging

setup_logger()

# Initialise a shared event queue for communication
subsumption_layer_event_queue = Queue()
finite_state_machine_event_queue = Queue()
behavior_tree_event_queue = Queue()

# Instantiate High-Level FSM, Behavior Tree, and Reactive Layer
reactive_layer = ReactiveLayer(event_queue=subsumption_layer_event_queue)
finite_state_machine_layer = fsm.FSM(subsumption_layer_event_queue=subsumption_layer_event_queue, finite_state_machine_event_queue=finite_state_machine_event_queue, behavior_tree_event_queue=behavior_tree_event_queue)
deliberate_layer = BehaviorTree(finite_state_machine_event_queue=finite_state_machine_event_queue, behavior_tree_event_queue=behavior_tree_event_queue)

# Loop interval
LOOP_INTERVAL = 0.1

# Define each layer's main function to run in its own thread
def subsumption_layer():
    logger = logging.getLogger("SubsumptionLayer")
    logger.info("Subsumption layer started.")
    try:
        while True:
            reactive_layer.detect_critical_condition()
            time.sleep(LOOP_INTERVAL)
    except KeyboardInterrupt:
        logger.info("Shutting down subsumption layer...")

def finite_state_machine():
    logger = logging.getLogger("FiniteStateMachine")
    logger.info("Finite state machine layer started.")
    try:
        while True:
            finite_state_machine_layer.update()            
            time.sleep(LOOP_INTERVAL)
    except KeyboardInterrupt:
        logger.info("Shutting down finite state machine...")

def behavior_tree():
    logger = logging.getLogger("BehaviorTree")
    logger.info("Behavior tree layer started.")
    try:
        while True:
            deliberate_layer.update()
            time.sleep(LOOP_INTERVAL)
    except KeyboardInterrupt:
        logger.info("Shutting down behavior tree...")

if __name__ == "__main__":
    logger = logging.getLogger("Main")

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
        logger.info("Exiting state managment service...")
        
