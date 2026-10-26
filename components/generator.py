from .component import Component


class Generator(Component):
    """A generator with a maximum output and a simple marginal cost."""

    def __init__(self, name: str, bus: str, capacity_mw: float, marginal_cost: float):
        super().__init__(name)
        self.bus = bus
        self.capacity_mw = float(capacity_mw)
        self.marginal_cost = float(marginal_cost)
        self.output_mw = 0.0

    def generate(self, power_mw: float) -> None:
        if power_mw < 0 or power_mw > self.capacity_mw:
            raise ValueError(f"{self.name}: output must be between 0 and {self.capacity_mw} MW")
        self.output_mw = float(power_mw)

    def calculate_cost(self) -> float:
        return self.output_mw * self.marginal_cost

    def validate(self) -> bool:
        return self.capacity_mw >= 0 and self.marginal_cost >= 0 and 0 <= self.output_mw <= self.capacity_mw
