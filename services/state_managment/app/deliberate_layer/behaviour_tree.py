class Task:
    def start(self):
        pass

    def update(self):
        pass

    def end(self):
        pass


class BehaviorTree:
    def __init__(self, root):
        self.root = root

    def update(self):
        self.root.update()


class WakeWordTask(Task):
    def start(self):
        print("Starting to listen")

    def update(self):
        print("Listening...")

    def end(self):
        print("Stopped listening")
