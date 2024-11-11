# test_finite_state_machine.py

import unittest
from unittest.mock import MagicMock
import sys
import os

# Add the project root directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
sys.path.insert(0, project_root)

from services.state_managment.app.deliberate_layer.finite_state_machine import FSM

from queue import Queue
subsumption_layer_event_queue = Queue()
finite_state_machine_event_queue = Queue()
behavior_tree_event_queue = Queue()

class TestReactiveLayer(unittest.TestCase):

    def setUp(self):
        # Clear the event queue to avoid interference between tests
        while not subsumption_layer_event_queue.empty():
            subsumption_layer_event_queue.get()
        while not finite_state_machine_event_queue.empty():
            finite_state_machine_event_queue.get()
        while not behavior_tree_event_queue.empty():
            behavior_tree_event_queue.get()

        # Create a mock MQTT client
        self.mock_mqtt_client = MagicMock()

        # Instantiate the FSM
        self.fsm = FSM(mqtt_client=self.mock_mqtt_client, initial_state='Sleep', subsumption_layer_event_queue=subsumption_layer_event_queue, finite_state_machine_event_queue=finite_state_machine_event_queue, behavior_tree_event_queue=behavior_tree_event_queue)

    def test_switch_to_active_state(self):
        subsumption_layer_event_queue.put({"layer": "subsumption", "state": "Active"})
        self.fsm.update()
        self.assertEqual(self.fsm.get_state(), 'Active')

    def test_switch_to_sleep_state(self):
        subsumption_layer_event_queue.put({"layer": "subsumption", "state": "Sleep"})
        self.fsm.update()
        self.assertEqual(self.fsm.get_state(), 'Sleep')

    def test_error_state(self):
        subsumption_layer_event_queue.put({"layer": "subsumption", "state": "Error"})
        self.fsm.update()
        self.assertEqual(self.fsm.get_state(), 'Error')
    
    def test_interacting_state(self):
        behavior_tree_event_queue.put({"layer": "behavior_tree", "state": "interacting"})
        self.fsm.update()
        self.assertEqual(self.fsm.get_state(), 'Interacting')
    
    def test_configuring_state(self):
        behavior_tree_event_queue.put({"layer": "behavior_tree", "state": "configuring"})
        self.fsm.update()
        self.assertEqual(self.fsm.get_state(), 'Configuring')
     
if __name__ == '__main__':
    unittest.main()
