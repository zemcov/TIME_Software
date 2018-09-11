"""
kmirror_states.py:
Define all the State classes of the K-Mirror.

Code implemented from
https://dev.to/karn/building-a-simple-state-machine-in-python
"""

from state import State

# Start of our states.
class Home(State):
    """
    The state which indicates that the K-Mirror is home.
    """

    def __init__(self,verified=0):
        """
        Initialize Home state.
        """
        super(Home, self).__init__(verified)
        # Other Home tasks should be listed in this function.

    def on_event(self, event):
        """
        Process event action.
        """
        if event == 'turn_on':
            return Ready(self.verified)
        if event == 'error':
            return EmergencyStop()
        return self

    def events(self):
        """
        Give string list of applicable events for current state.
        """
        return ['turn_on', 'error']

class Ready(State):
    """
    The state which indicates that the K-Mirror is ready.
    """

    def __init__(self, verified):
        """
        Initialize Ready state.
        """
        super(Ready, self).__init__(verified)
        # Other Ready tasks should be listed in this function.


    def on_event(self, event):
        """
        Process event action.
        """
        if event == 'verify':
            return Verification()
        if event == 'start_tracking':
            if self.verified == 1:
                return Tracking(self.verified)
            print 'Error: K-Mirror must be verified to start tracking'
        if event == 'go_home':
            return Home()
        if event == 'error':
            return EmergencyStop()
        return self

    def events(self):
        """
        Give string list of applicable events for current state.
        """
        return ['verify', 'start_tracking', 'go_home', 'error']

class EmergencyStop(State):
    """
    The state which indicates that the K-Mirror has initiated an Emergency
    Stop.
    """

    def __init__(self, verified=0):
        """
        Initialize EmergencyStop state.
        """
        super(EmergencyStop, self).__init__(verified)
        # Other EmergencyStop tasks should be listed in this function.

    def on_event(self, event):
        """
        Process event action.
        """
        if event == 'turn_on':
            return Ready(self.verified)
        if event == 'reset':
            return Home()
        return self

    def events(self):
        """
        Give string list of applicable events for current state.
        """
        return ['turn_on','reset']

class Verification(State):
    """
    The state which indicates that the K-Mirror is verifying its functionality
    and going to a set position.
    """

    def __init__(self, verified=1):
        """
        Initialize Verification state.
        """
        super(Verification, self).__init__(verified)
        from rotate_motor import rotate_motor
        from encoder import get_pos, home_pos
        from util import deg_to_step
        import time

        problem = false
        while get_pos() < home_pos - 0.1 or get_pos() > home_pos + 0.1:
            steps = deg_to_step(home_pos) - deg_to_step(get_pos())
            rotate_motor(int(steps), 2000)
            time.sleep(abs(steps)/2000.0 + 0.1)
        print get_pos()
        self.auto_next_event = 'finished_verifying'

    def on_event(self, event):
        """
        Process event action.
        """
        if event == 'finished_verifying':
            return Ready(self.verified)
        if event == 'error':
            return EmergencyStop()
        return self

    def events(self):
        """
        Give string list of applicable events for current state.
        """
        return ['finished_verifying', 'error']

class Tracking(State):
    """
    The state which indicates that the K-Mirror is in Tracking mode.
    """

    def __init__(self, verified):
        """
        Initialize Tracking state.
        """
        super(Tracking, self).__init__(verified)
        # Other Tracking tasks should be listed in this function.
        from tracking import TrackingAlgorithm
        tracker = TrackingAlgorithm()
        tracker.track()
        # from kmirror_main import main
        # main()
        self.auto_next_event = 'end_tracking'

    def on_event(self, event):
        """
        Process event action.
        """
        if event == 'end_tracking':
            return Ready(self.verified)
        if event == 'error':
            return EmergencyStop()
        if safety.get_state[2]:
            return EmergencyStop()
        return self

    def events(self):
        """
        Give string list of applicable events for current state.
        """
        return ['end_tracking', 'error']
# End of states.
