import unittest
from finite_state_machine import SleepState, AwakeState


class TestStateMachine(unittest.TestCase):
    def test_state_transition(self):
        fsm = FSM(SleepState())
        self.assertIsInstance(fsm.state, SleepState)

        # Test transition to AwakeState
        fsm.update({'awake': True})
        self.assertIsInstance(fsm.state, AwakeState)

        # Test transition back to SleepState
        fsm.update({'sleep': True})
        self.assertIsInstance(fsm.state, SleepState)

    def test_state_behavior(self):
        # Test behavior of SleepState
        sleep_state = SleepState()
        self.assertEqual(sleep_state.update({'awake': False}), sleep_state)
        self.assertIsInstance(sleep_state.update({'awake': True}), AwakeState)

        # Test behavior of AwakeState
        awake_state = AwakeState()
        self.assertEqual(awake_state.update({'sleep': False}), awake_state)
        self.assertIsInstance(awake_state.update({'sleep': True}), SleepState)


if __name__ == '__main__':
    unittest.main()
