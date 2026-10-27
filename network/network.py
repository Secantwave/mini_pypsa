from dataclasses import dataclass, field


@dataclass
class Network:
    """Container for the complete simplified power-system model."""

    name: str
    buses: list = field(default_factory=list)
    generators: list = field(default_factory=list)
    loads: list = field(default_factory=list)
    lines: list = field(default_factory=list)
    storage_units: list = field(default_factory=list)

    def add_bus(self, bus) -> None:
        self.buses.append(bus)

    def add_generator(self, generator) -> None:
        self.generators.append(generator)
        generator.bus.connect(generator)

    def add_load(self, load) -> None:
        self.loads.append(load)
        load.bus.connect(load)

    def add_line(self, line) -> None:
        self.lines.append(line)
        line.from_bus.connect(line)
        line.to_bus.connect(line)

    def add_storage(self, storage) -> None:
        self.storage_units.append(storage)
        storage.bus.connect(storage)

    def total_generation(self) -> float:
        return sum(g.output for g in self.generators)

    def total_demand(self) -> float:
        return sum(load.demand for load in self.loads)

    def total_storage_discharge_available(self) -> float:
        return sum(
            min(storage.energy, storage.max_power)
            for storage in self.storage_units
        )

    def power_balance(self) -> float:
        return self.total_generation() - self.total_demand()

    def total_cost(self) -> float:
        return sum(g.calculate_cost() for g in self.generators)

    def reset_flows(self) -> None:
        for line in self.lines:
            line.set_flow(0.0)

    def summary(self) -> str:
        balance = self.power_balance()
        status = (
            "BALANCED"
            if abs(balance) < 1e-9
            else "SURPLUS"
            if balance > 0
            else "DEFICIT"
        )

        return (
            f"\n===== {self.name} =====\n"
            f"Buses       : {len(self.buses)}\n"
            f"Generators  : {len(self.generators)}\n"
            f"Loads       : {len(self.loads)}\n"
            f"Lines       : {len(self.lines)}\n"
            f"Storage     : {len(self.storage_units)}\n"
            f"Generation  : {self.total_generation():.2f} MW\n"
            f"Demand      : {self.total_demand():.2f} MW\n"
            f"Balance     : {balance:.2f} MW ({status})\n"
            f"Cost        : ₹{self.total_cost():.2f}/h\n"
        )
