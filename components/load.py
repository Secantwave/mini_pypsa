from .component import Component


class Load(Component):
    """An electricity consumer connected to a bus."""

    def __init__(self, name: str, bus: str, demand_mw: float):
        super().__init__(name)
        self.bus = bus
        self.demand_mw = float(demand_mw)

    def set_demand(self, demand_mw: float) -> None:
        if demand_mw < 0:
            raise ValueError("Demand cannot be negative")
        self.demand_mw = float(demand_mw)

    def validate(self) -> bool:
        return self.demand_mw >= 0
