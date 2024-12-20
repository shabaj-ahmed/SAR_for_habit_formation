class EventDispatcher:
    '''
    EventDispatcher class is responsible for registering and dispatching events.
    The event dispatcher uses a dictionary to store event handlers, where the key is the event name and the value is a list of handlers (functions).
    Dispatching an event maps the event name to the list of handlers and calls each handler with the payload as an argument.
    '''
    def __init__(self):
        self.event_handlers = {}

    def register_event(self, event_name, handler):
        """Registers a handler for a specific event."""
        if event_name not in self.event_handlers:
            self.event_handlers[event_name] = []
        self.event_handlers[event_name].append(handler)

    def dispatch_event(self, event_name, payload = None):
        """Calls all handlers for a specific event."""
        handlers = self.event_handlers.get(event_name, [])
        for handler in handlers:
            try:
                handler(payload) if payload else handler()
            except Exception as e:
                print(f"Error dispatching event {event_name}: {e}")