# test_behaviour_tree.py

import unittest
from unittest.mock import MagicMock
import sys
import os

# Add the project root directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
sys.path.insert(0, project_root)

from services.state_managment.app.deliberate_layer.behaviour_tree import BehaviorTree

from queue import Queue 

subsumption_layer_event_queue = Queue()
finite_state_machine_event_queue = Queue()
behavior_tree_event_queue = Queue()

class TestBehaviourTree(unittest.TestCase):

    def setUp(self):
        print("-----------------")
        # Clear the event queue to avoid interference between tests
        while not subsumption_layer_event_queue.empty():
            subsumption_layer_event_queue.get()
        while not finite_state_machine_event_queue.empty():
            finite_state_machine_event_queue.get()
        while not behavior_tree_event_queue.empty():
            behavior_tree_event_queue.get()

        # Create a mock MQTT client
        self.mock_mqtt_client = MagicMock()
        self.mock_mqtt_client.get_behaviour_completion_status.return_value = {
            'reminder': False,
            'check_in': False,
            'configurations': False
        }

        # Instantiate the FSM
        self.BT = BehaviorTree(
            mqtt_client=self.mock_mqtt_client,
            finite_state_machine_event_queue=finite_state_machine_event_queue,
            behavior_tree_event_queue=behavior_tree_event_queue
        )
        
    def test_switch_to_active_state(self):
        print("Test switch to active state")
        self.mock_mqtt_client.get_user_event.return_value = {
            'check_in': None,
            'configurations': None
        }

        finite_state_machine_event_queue.put({"state": "Active"})
        for i in range(10):
            self.BT.update()
        self.assertEqual(self.BT.get_current_state(), 'Active')

    def test_switch_to_sleep_state(self):
        print("Test switch to sleep state")
        self.mock_mqtt_client.get_user_event.return_value = {
            'check_in': None,
            'configurations': None
        }

        finite_state_machine_event_queue.put({"state": "Sleep"})
        for i in range(10):
            self.BT.update()
        self.assertEqual(self.BT.get_current_state(), 'Sleep')
    
    def test_transition_to_configurations_branch(self):
        print("Test transition to configurations branch")
        self.mock_mqtt_client.get_user_event.return_value = {
            'check_in': None,
            'configurations': True
        }

        # MQTT message should trigger the transition to the reminder branch
        for i in range(10):
            self.BT.update()
        self.assertEqual(self.BT.get_current_branch(), "configurations")

    def test_transition_to_check_in_branch(self):
        print("Test transition to check-in branch")
        self.mock_mqtt_client.get_user_event.return_value = {
            'check_in': True,
            'configurations': None
        }
        
        # MQTT message should trigger the transition to the check_in branch
        for i in range(10):
            self.BT.update()
        self.assertEqual(self.BT.get_current_branch(), "check_in")

    def test_transition_back_to_reminder_branch(self):
        print("Test transition back to reminder branch")
        self.mock_mqtt_client.get_user_event.return_value = {
            'check_in': True,
            'configurations': None
        }

        # MQTT message should trigger the transition to the reminder branch
        for i in range(10):
            self.BT.update()
        # self.assertEqual(self.BT.get_current_branch(), "check_in")

        self.mock_mqtt_client.get_user_event.return_value = {
            'check_in': None,
            'configurations': None
        }
        # publish a message to the MQTT client to confirm check-in is complete
        self.mock_mqtt_client.get_behaviour_completion_status.return_value = {
            'reminder': False,
            'check_in': True,
            'configurations': False
        }

        for i in range(10):
            self.BT.update()

        self.mock_mqtt_client.get_behaviour_completion_status.return_value = {
            'reminder': False,
            'check_in': False,
            'configurations': False
        }

        for i in range(10):
            self.BT.update()
        self.assertEqual(self.BT.get_current_branch(), "reminder")
    
    def test_transition_accross_multiple_branches(self):
        print("Test transition accross multiple branches")
        self.mock_mqtt_client.get_user_event.return_value = {
            'check_in': None,
            'configurations': None
        }
        self.mock_mqtt_client.get_behaviour_completion_status.return_value = {
            'reminder': False,
            'check_in': False,
            'configurations': False
        }

        for i in range(10):
            self.BT.update()

        finite_state_machine_event_queue.put({"state": "Active"})

        # for i in range(10):
        #     self.BT.update()

        # self.mock_mqtt_client.get_user_event.return_value = {
        #     'check_in': True,
        #     'configurations': None
        # }

        # self.BT.update()

        # self.mock_mqtt_client.get_user_event.return_value = {
        #     'check_in': None,
        #     'configurations': None
        # }

        # # MQTT message should trigger the transition to the configurations branch
        # for i in range(10):
        #     self.BT.update()
        
        # self.assertEqual(self.BT.get_current_branch(), "check_in")

        # self.mock_mqtt_client.get_behaviour_completion_status.return_value = {
        #     'reminder': False,
        #     'check_in': True,
        #     'configurations': False
        # }

        # self.BT.update()

        # self.mock_mqtt_client.get_behaviour_completion_status.return_value = {
        #     'reminder': False,
        #     'check_in': False,
        #     'configurations': False
        # }

        # # MQTT message should trigger the transition to the reminder branch
        # for i in range(10):
        #     self.BT.update()
        
        # self.assertEqual(self.BT.get_current_branch(), "reminder")
     
if __name__ == '__main__':
    unittest.main()
