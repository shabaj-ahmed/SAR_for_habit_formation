import unittest
import threading
import time
from queue import Queue
from unittest.mock import MagicMock

# Add the project root directory to sys.path
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
sys.path.insert(0, project_root)

from services.state_managment.app.reactive_layer.subsumption_layer import ReactiveLayer
import services.state_managment.app.deliberate_layer.finite_state_machine as fsm
from services.state_managment.app.deliberate_layer.behaviour_tree import BehaviorTree

class TestIntegrationStateMachines(unittest.TestCase):
    def setUp(self):
        # Create event queues
        self.subsumption_layer_event_queue = Queue()
        self.finite_state_machine_event_queue = Queue()
        self.behavior_tree_event_queue = Queue()

        # Create a mock MQTT client
        self.mock_mqtt_client = MagicMock()
        self.mock_mqtt_client.get_inputs.return_value = {
            'switch_state': None,
            'error': None
        }
        self.mock_mqtt_client.get_user_event.return_value = {
            'check_in': None,
            'configurations': None
        }
        self.mock_mqtt_client.get_behaviour_completion_status.return_value = {
            'reminder': False,
            'check_in': False,
            'configurations': False
        }

        # Instantiate layers
        self.reactive_layer = ReactiveLayer(
            mqtt_client=self.mock_mqtt_client,
            event_queue=self.subsumption_layer_event_queue
        )
        self.finite_state_machine_layer = fsm.FSM(
            mqtt_client=self.mock_mqtt_client,
            initial_state='Sleep',
            subsumption_layer_event_queue=self.subsumption_layer_event_queue,
            finite_state_machine_event_queue=self.finite_state_machine_event_queue,
            behavior_tree_event_queue=self.behavior_tree_event_queue
        )
        self.behavior_tree = BehaviorTree(
            mqtt_client=self.mock_mqtt_client,
            finite_state_machine_event_queue=self.finite_state_machine_event_queue,
            behavior_tree_event_queue=self.behavior_tree_event_queue
        )

        # Loop interval
        self.LOOP_INTERVAL = 0.1

        # Start threads for each layer
        self.subsumption_thread = threading.Thread(target=self.run_subsumption_layer, daemon=True)
        self.fsm_thread = threading.Thread(target=self.run_finite_state_machine, daemon=True)
        self.behavior_tree_thread = threading.Thread(target=self.run_behavior_tree, daemon=True)

        self.subsumption_thread.start()
        self.fsm_thread.start()
        self.behavior_tree_thread.start()

    def run_subsumption_layer(self):
        try:
            while True:
                self.reactive_layer.detect_critical_condition()
                time.sleep(self.LOOP_INTERVAL)
        except KeyboardInterrupt:
            print("Shutting down subsumption layer...")

    def run_finite_state_machine(self):
        try:
            while True:
                self.finite_state_machine_layer.update()
                time.sleep(self.LOOP_INTERVAL)
        except KeyboardInterrupt:
            print("Shutting down FSM...")

    def run_behavior_tree(self):
        try:
            while True:
                self.behavior_tree.update()
                time.sleep(self.LOOP_INTERVAL)
        except KeyboardInterrupt:
            print("Shutting down behavior tree...")

    def test_integration_active_state(self):
        # Test if the state machines integrate correctly when switching to 'active' state
        self.mock_mqtt_client.get_inputs.return_value = {
            'switch_state': True,
            'error': None
        }
        time.sleep(1)  # Allow some time for state propagation

        # Check if FSM transitioned to 'active' and behavior tree also picked up the state
        self.assertEqual(self.finite_state_machine_layer.get_state(), 'Active')
        self.assertEqual(self.behavior_tree.get_current_state(), 'Active')

    def test_integration_sleep_state(self):
        # Test if the state machines integrate correctly when switching to 'sleep' state
        self.mock_mqtt_client.get_inputs.return_value = {
            'switch_state': False,
            'error': None
        }
        time.sleep(1)  # Allow some time for state propagation

        # Check if FSM transitioned to 'sleep' and behavior tree also picked up the state
        self.assertEqual(self.finite_state_machine_layer.get_state(), 'Sleep')
        self.assertEqual(self.behavior_tree.get_current_state(), 'Sleep')

    def test_integration_error_state(self):
        # Test if the state machines integrate correctly when an error occurs
        self.mock_mqtt_client.get_inputs.return_value = {
            'switch_state': None,
            'error': True
        }
        time.sleep(1)  # Allow some time for state propagation

        # Check if FSM transitioned to 'Error' state
        self.assertEqual(self.finite_state_machine_layer.get_state(), 'Error')

    def test_integration_default_to_sleep_state(self):
        self.mock_mqtt_client.get_inputs.return_value = {
            'switch_state': None,
            'error': None
        }


    def tearDown(self):
        # Stop threads if needed
        pass

if __name__ == "__main__":
    unittest.main()
