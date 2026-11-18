
from simulator.wallbox import Wallbox


class ChargingController:
    def __init__(self):
        self.wallbox = Wallbox()

    def get_status(self):
        return self.wallbox.get_status()

    def start_charging(self):
        return self.wallbox.start_charging()

    def stop_charging(self):
        return self.wallbox.stop_charging()

    def set_current(self, current):
        return self.wallbox.set_current(current)
