# Initialize the High-Level FSM and other components
high_level_fsm = HighLevelStateMachine()
reactive_layer = ReactiveLayer()
behavior_tree = BehaviorTree()

while True:
    # Run the high-level FSM
    high_level_fsm.run()

    # Check reactive conditions and enforce reactive behaviors
    critical_condition = reactive_layer.check_critical_conditions()
    if critical_condition:
        # Handle the condition, possibly transitioning to a different state
        high_level_fsm.transition_to(SafetyStop())

    # If the FSM is in the 'Active' state, run behavior trees or other behaviors
    if isinstance(high_level_fsm.current_state, ActiveMode):
        behavior_tree.execute_behavior()

    # Pause before the next loop iteration
    time.sleep(LOOP_INTERVAL)
