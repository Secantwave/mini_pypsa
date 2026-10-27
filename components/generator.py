from .component import Component


class Generator(Component):
    """Power generator with a capacity and marginal operating cost."""

    def __init__(
        self,
        name: str,
        bus,
        capacity: float,
        marginal_cost: float,
        carrier: str | None = None,
    ):
        super().__init__(name)
        if capacity < 0:
            raise ValueError("Generator capacity cannot be negative.")
        if marginal_cost < 0:
            raise ValueError("Marginal cost cannot be negative.")

        self.bus = bus
        self.capacity = float(capacity)
        self.marginal_cost = float(marginal_cost)
        self.carrier = carrier or self._infer_carrier(name)
        self.output = 0.0

    @staticmethod
    def _infer_carrier(name: str) -> str:
        lower = name.lower()
        for carrier in ("solar", "wind", "gas", "coal", "hydro", "nuclear", "biomass", "oil"):
            if carrier in lower:
                return carrier
        return "generator"

    def generate(self, power: float) -> None:
        power = float(power)
        if power < 0:
            raise ValueError("Generation cannot be negative.")
        if power > self.capacity:
            raise ValueError(
                f"{self.name} cannot generate {power:g} MW; "
                f"capacity is {self.capacity:g} MW."
            )
        self.output = power

    def calculate_cost(self) -> float:
        return self.output * self.marginal_cost

    def info(self) -> str:
        return (
            f"Generator {self.name}: "
            f"{self.output:g}/{self.capacity:g} MW, "
            f"cost={self.marginal_cost:g}/MWh"
        )
