from .component import Component


class TransmissionLine(Component):
    """Connection between two buses with a simplified power-flow limit."""

    def __init__(
        self,
        name: str,
        from_bus,
        to_bus,
        capacity: float,
    ):
        super().__init__(name)
        if capacity <= 0:
            raise ValueError("Line capacity must be greater than zero.")

        self.from_bus = from_bus
        self.to_bus = to_bus
        self.capacity = float(capacity)
        self.flow = 0.0

    def set_flow(self, flow: float) -> None:
        self.flow = float(flow)

    def check_capacity(self) -> bool:
        return abs(self.flow) <= self.capacity + 1e-9

    def loading_percent(self) -> float:
        return abs(self.flow) / self.capacity * 100.0

    def info(self) -> str:
        status = "NORMAL" if self.check_capacity() else "OVERLOADED"
        return (
            f"Line {self.name}: "
            f"{self.flow:g}/{self.capacity:g} MW, "
            f"{self.loading_percent():.1f}% - {status}"
        )
