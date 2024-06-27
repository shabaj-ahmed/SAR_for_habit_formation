class State:
    def enter(self):
        pass

    def exit(self):
        pass

    def update(self):
        pass


class SleepState(State):
    def enter(self):
        print("Entering sleep state")

    def exit(self):
        print("Exiting sleep state")

    def update(self):
        pass


class AwakeState(State):
    def enter(self):
        print("Entering awake state")

    def exit(self):
        print("Exiting awake state")

    def update(self):
        pass


class IdleState:
    def enter(self):
        print("Entering idle state")

    def exit(self):
        print("Exiting idle state")

    def update(self):
        pass


class InteractingState:
    def enter(self):
        print("Entering interacting state")

    def exit(self):
        print("Exiting interacting state")

    def update(self):
        pass


class FSM:
    def __init__(self, initial_state):
        self.states = {
            'Sleep': SleepState(),
            'Awake': AwakeState(),
            'Idle': IdleState(),
            'Interacting': InteractingState(),
        }
        self.state = self.states[initial_state]
        self.state.enter()

    def update(self):
        self.state.update()

    def transition_to(self, state_name):
        if state_name in self.states:
            self.state.exit()
            self.state = self.states[state_name]
            self.state.enter()
        else:
            print(f"State {state_name} not found.")
