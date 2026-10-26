from .component import Component


class Storage(Component):
    """A simple battery model. The simulation interval is measured in hours."""

    def __init__(self, name: str, bus: str, capacity_mwh: float, max_power_mw: float, energy_mwh: float):
        super().__init__(name)
        self.bus = bus
        self.capacity_mwh = float(capacity_mwh)
        self.max_power_mw = float(max_power_mw)
        self.energy_mwh = float(energy_mwh)
        self.last_discharge_mw = 0.0
        self.last_charge_mw = 0.0

    def discharge(self, power_mw: float, hours: float = 1.0) -> float:
        if hours <= 0:
            raise ValueError("hours must be greater than zero")
        power = min(max(0.0, power_mw), self.max_power_mw, self.energy_mwh / hours)
        self.energy_mwh -= power * hours
        self.last_discharge_mw += power
        return power

    def charge(self, power_mw: float, hours: float = 1.0) -> float:
        if hours <= 0:
            raise ValueError("hours must be greater than zero")
        room = max(0.0, self.capacity_mwh - self.energy_mwh)
        power = min(max(0.0, power_mw), self.max_power_mw, room / hours)
        self.energy_mwh += power * hours
        self.last_charge_mw += power
        return power

    def validate(self) -> bool:
        return (
            self.capacity_mwh >= 0
            and self.max_power_mw >= 0
            and -1e-9 <= self.energy_mwh <= self.capacity_mwh + 1e-9
        )
