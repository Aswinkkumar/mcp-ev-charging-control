
class Wallbox:
    def __init__(self):
        self.status = "Available"
        self.charging_current = 0
        self.max_current = 16
        self.energy_wh = 0.0

    def get_status(self):
        return {
            "status": self.status,
            "current_a": self.charging_current,
            "max_current_a": self.max_current,
            "energy_wh": self.energy_wh
        }

    def start_charging(self):
        if self.status == "Charging":
            return "Charging is already active."

        self.status = "Charging"
        self.charging_current = 10

        return "Simulated charging started."

    def stop_charging(self):
        if self.status != "Charging":
            return "Charging is not active."

        self.status = "Available"
        self.charging_current = 0

        return "Simulated charging stopped."

    def set_current(self, current):
        if isinstance(current, bool) or not isinstance(
            current, (int, float)
        ):
            return "Invalid current value."

        if not 6 <= current <= self.max_current:
            return (
                f"Current must be between 6 and "
                f"{self.max_current} A."
            )

        if self.status != "Charging":
            return "Start charging before setting current."

        self.charging_current = current

        return f"Charging current set to {current} A."
