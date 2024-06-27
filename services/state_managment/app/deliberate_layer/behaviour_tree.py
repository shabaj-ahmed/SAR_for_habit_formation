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

    # Based on the state of the FSM, the behavior tree will be updated


class FaceTracking(Task):
    def start(self):
        print("Starting to track face")

    def update(self):
        print("Tracking face...")

    def end(self):
        print("Stopped tracking face")


class AutonomousBhaviour(Task):
    def start(self):
        print("Starting to autonomously behave")

    def update(self):
        print("Behaving autonimously...")

    def end(self):
        print("Stopped autonomous behaviour")


class Configurations(Task):
    def start(self):
        print("Starting to configure")

    def update(self):
        print("Configuring...")

    def end(self):
        print("Stopped configuring")


class EmotionGeneration(Task):
    def start(self):
        print("Starting to generate emotion")

    def update(self):
        print("Generating emotion...")

    def end(self):
        print("Stopped generating emotion")


class Dialog(Task):
    def start(self):
        print("Starting dialog")

    def update(self):
        print("Dialoging...")

    def end(self):
        print("Stopped dialog")


class AdministerSurvey(Task):
    def start(self):
        print("Starting survey")

    def update(self):
        print("Surveying...")

    def end(self):
        print("Stopped survey")


class taskScheduler(Task):
    def start(self):
        print("Starting task scheduler")

    def update(self):
        print("Scheduling tasks...")

    def end(self):
        print("Stopped task scheduler")
