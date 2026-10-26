from .component import Component


class TransmissionLine(Component):
    """A line between two buses. Flow sign follows from_bus -> to_bus."""

    def __init__(self, name: str, from_bus: str, to_bus: str, capacity_mw: float):
        super().__init__(name)
        self.from_bus = from_bus
        self.to_bus = to_bus
        self.capacity_mw = float(capacity_mw)
        self.flow_mw = 0.0

    @property
    def loading_percent(self) -> float:
        if self.capacity_mw <= 0:
            return 0.0
        return abs(self.flow_mw) / self.capacity_mw * 100

    @property
    def is_overloaded(self) -> bool:
        return abs(self.flow_mw) > self.capacity_mw + 1e-9

    def validate(self) -> bool:
        return self.capacity_mw > 0 and self.from_bus != self.to_bus
