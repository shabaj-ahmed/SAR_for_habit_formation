class ReactiveLayer:
    def __init__(self, mqtt_client, event_queue):
        self.mqtt_client = mqtt_client
        self.event_queue = event_queue
        self.previous_state = None

    def detect_critical_condition(self):
        inputs = self.mqtt_client.get_critical_events()

        # The logic below follows the subsumption design architecture. It monitors the
        # inputs from critical events. based on the priority of the event it would
        # trigger the appropriate state change.
        if inputs['error'] == True: # Heighest priority
            if self.previous_state != "Error":
                self.event_queue.put({"state": "Error"})
                self.previous_state = "Error"
        elif inputs['switch_state'] == False: # Emergency stop
            if self.previous_state != "Sleep":
                self.event_queue.put({"state": "Sleep"})
                self.previous_state = "Sleep"
        elif inputs['switch_state'] == True:
            if self.previous_state != "Active":
                self.event_queue.put({"state": "Active"})
                self.previous_state = "Active"
        elif inputs['reminder'] == True: # If user has turned the system off no reminder should be sent
            if self.previous_state != "Active":
                self.event_queue.put({"state": "Active"})
                self.previous_state = "Active"
        else: # default to sleep
            if self.previous_state != "Sleep":
                self.event_queue.put({"state": "Sleep"})
                self.previous_state = "Sleep"

        # If the transition from one state to another requires a specific sequence of events
        # to occur to safely transition, then the deliberate layer would be responsible for
        # managing it.