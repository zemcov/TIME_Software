"""
kmirror_device.py:
Define the Device class.

Code implemented from
https://dev.to/karn/building-a-simple-state-machine-in-python
"""

from kmirror_states import Home
import state

class Device(object):
    """
    A simple state machine that mimics the functionality of a device from a
    high level
    """

    def __init__(self):
        """
        Initialize the components.
        """

        # Start with the default state.
        self.state = Home()

    def on_event(self, event):
        """
        This is the bread and butter of the state machine. Incoming events are
        delegated to the given states which then handle the event. The result
        is then assigned as the new state.
        """

        # The next state will be the result of the on_event function.
        self.state = self.state.on_event(event)

    def events(self):
        """
        Request for list of events is delegated to the current state and
        returned through here.
        """
        return self.state.events()
