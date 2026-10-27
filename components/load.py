from .component import Component


class Load(Component):
    """Electrical demand connected to a bus."""

    def __init__(self, name: str, bus, demand: float):
        super().__init__(name)
        if demand < 0:
            raise ValueError("Demand cannot be negative.")

        self.bus = bus
        self.demand = float(demand)

    def get_demand(self) -> float:
        return self.demand

    def set_demand(self, demand: float) -> None:
        demand = float(demand)
        if demand < 0:
            raise ValueError("Demand cannot be negative.")
        self.demand = demand

    def info(self) -> str:
        return f"Load {self.name}: {self.demand:g} MW"
