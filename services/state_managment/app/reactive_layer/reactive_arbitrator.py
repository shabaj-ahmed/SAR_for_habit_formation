class ReactiveLayer:
    def __init__(self, mqtt_client, fsm):
        self.mqtt_client = mqtt_client
        self.fsm = fsm

    def detect_critical_condition(self):
        inputs = self.mqtt_client.get_inputs()

        # Transition logic
        if inputs['switch_state'] == True:
            self.fsm.transition_to('Active')
            # Need to acknowledge the switch state and switch it to None
            # or else the state will keep transitioning to Active
        elif inputs['switch_state'] == False:
            self.fsm.transition_to('Sleep')
        elif inputs['wake_word'] == True:
            self.fsm.transition_to('Active')
        elif inputs['error'] == True:
            self.fsm.transition_to('Error')
