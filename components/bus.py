from .component import Component


class Bus(Component):
    """A connection point in the electrical network."""

    def __init__(self, name: str, voltage_kv: float = 11.0):
        super().__init__(name)
        self.voltage_kv = float(voltage_kv)

    def validate(self) -> bool:
        return self.voltage_kv > 0
