class State:
    def enter(self):
        pass

    def exit(self):
        pass

    def update(self):
        pass


class OffState(State):
    def __init__(self):
        self.stateName = 'Off'

    def enter(self):
        # Turn everything off
        pass

    def exit(self):
        pass

    def update(self):
        pass


class SleepState(State):
    def __init__(self):
        self.stateName = 'Sleep'

    def enter(self):
        # Turn everything off
            # Screen
            # Robot
            # Voice assistant
            # Task scheduler
        pass

    def exit(self):
        pass

    def update(self):
        pass


class ActiveState:
    def __init__(self):
        self.stateName = 'Active'

    def enter(self):
        # screen
        # Task scheduler
        pass

    def exit(self):
        pass

    def update(self):
        pass


class InteractingState:
    def __init__(self):
        self.stateName = 'Interacting'

    def enter(self):
        # Turn on critical services
            # Robot
            # screen
            # voice assistant
            # Data collection
        pass

    def exit(self):
        # Robot
        # voice assistant
        pass

    def update(self):
        pass

class ConfiguringState:
    def __init__(self):
        self.stateName = 'Configuring'

    def enter(self):
        # Turn on critical services
            # Robot
            # screen
        pass

    def exit(self):
        pass

    def update(self):
        pass

class ErrorState:
    def __init__(self):
        self.stateName = 'Error'

    def enter(self):
        pass

    def exit(self):
        pass

    def update(self):
        pass


class FSM:
    def __init__(self, mqtt_client, initial_state, subsumption_layer_event_queue, finite_state_machine_event_queue, behavior_tree_event_queue):
        self.mqtt_client = mqtt_client

        self.subsumption_layer_event_queue = subsumption_layer_event_queue
        self.finite_state_machine_event_queue = finite_state_machine_event_queue
        self.behavior_tree_event_queue = behavior_tree_event_queue

        self.states = {
            'Off': OffState(),
            'Sleep': SleepState(),
            'Active': ActiveState(),
            'Interacting': InteractingState(),
            'Configuring': ConfiguringState(),
            'Error': ErrorState()
        }
        self.currentState = self.states[initial_state]
        self.currentState.enter()
    
    def get_state(self):
        return self.currentState.stateName        
    
    def transition_to(self, state_name):
        if state_name in self.states:
            self.currentState.exit()
            self.currentState = self.states[state_name]
            self.currentState.enter()
            self.finite_state_machine_event_queue.put({"layer": "finite_state_machine", "state": state_name})
            self.mqtt_client.publish("finite_state_machine", state_name)
        else:
            print(f"State {state_name} not found.")
    
    def update(self):
        if not self.subsumption_layer_event_queue.empty():
            subsumption_event = self.subsumption_layer_event_queue.get()
            if subsumption_event is not None:
                if subsumption_event["state"] == "Error":
                    self.transition_to("Error")
                elif subsumption_event["state"] == "Sleep":
                    self.transition_to("Sleep")
                elif subsumption_event["state"] == "Active":
                    self.transition_to("Active")
                elif subsumption_event["state"] == "Off":
                    self.transition_to("Off")
        if not self.behavior_tree_event_queue.empty():
            behavior_tree_event = self.behavior_tree_event_queue.get()
            if behavior_tree_event is not None:
                if behavior_tree_event["state"] == "interacting":
                    self.transition_to("Interacting")
                elif behavior_tree_event["state"] == "configuring":
                    self.transition_to("Configuring")
        
        # Calls update method of the current state
        self.currentState.update()
    