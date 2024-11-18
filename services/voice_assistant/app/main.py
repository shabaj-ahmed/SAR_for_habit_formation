from mqtt_client import MQTTClient
from decision_tree import DecisionTree

# Initialize the MQTT client
mqtt_client = MQTTClient("localhost", 1883)

# Initialize the decision tree
decision_tree = DecisionTree(mqtt_client)

# Main loop
def main():
    while True:
        # check mqtt for messages
        if mqtt_client.userEvents['check_in']:
        #     # Start the check-in process
            decision_tree.check_in()
            mqtt_client.publish_check_in_status("completed")

if __name__ == "__main__":
    main()