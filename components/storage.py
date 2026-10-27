from .component import Component


class Storage(Component):
    """Simplified battery model."""

    def __init__(
        self,
        name: str,
        bus,
        capacity: float,
        max_power: float,
        initial_energy: float = 0.0,
    ):
        super().__init__(name)

        if capacity <= 0:
            raise ValueError("Storage capacity must be greater than zero.")
        if max_power <= 0:
            raise ValueError("Storage max_power must be greater than zero.")
        if not 0 <= initial_energy <= capacity:
            raise ValueError("Initial energy must lie between 0 and capacity.")

        self.bus = bus
        self.capacity = float(capacity)
        self.max_power = float(max_power)
        self.energy = float(initial_energy)

    def charge(self, power: float) -> float:
        """Charge and return the actual power stored."""
        power = float(power)
        if power < 0:
            raise ValueError("Charging power cannot be negative.")

        actual = min(power, self.max_power, self.capacity - self.energy)
        self.energy += actual
        return actual

    def discharge(self, power: float) -> float:
        """Discharge and return the actual power supplied."""
        power = float(power)
        if power < 0:
            raise ValueError("Discharge power cannot be negative.")

        actual = min(power, self.max_power, self.energy)
        self.energy -= actual
        return actual

    def info(self) -> str:
        return f"Storage {self.name}: {self.energy:g}/{self.capacity:g} MWh"

    @property
    def state_of_charge(self) -> float:
        return self.energy / self.capacity * 100.0
