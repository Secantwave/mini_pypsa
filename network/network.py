from components import Bus, Generator, Load, Storage, TransmissionLine


class Network:
    """Stores the objects that make up a virtual power grid."""

    def __init__(self, name: str = "Demo Grid"):
        self.name = name
        self.buses: list[Bus] = []
        self.generators: list[Generator] = []
        self.loads: list[Load] = []
        self.lines: list[TransmissionLine] = []
        self.storage_units: list[Storage] = []

    @property
    def components(self):
        return self.buses + self.generators + self.loads + self.lines + self.storage_units

    def _add_unique(self, items, item):
        if any(existing.name == item.name for existing in self.components):
            raise ValueError(f"Component name already exists: {item.name}")
        items.append(item)
        return item

    def add_bus(self, bus: Bus):
        return self._add_unique(self.buses, bus)

    def add_generator(self, generator: Generator):
        return self._add_unique(self.generators, generator)

    def add_load(self, load: Load):
        return self._add_unique(self.loads, load)

    def add_line(self, line: TransmissionLine):
        return self._add_unique(self.lines, line)

    def add_storage(self, storage: Storage):
        return self._add_unique(self.storage_units, storage)

    def get_bus(self, name: str) -> Bus:
        for bus in self.buses:
            if bus.name == name:
                return bus
        raise KeyError(f"Unknown bus: {name}")

    def validate(self) -> list[str]:
        errors = []
        bus_names = {bus.name for bus in self.buses}
        for component in self.components:
            if not component.validate():
                errors.append(f"Invalid values in {component.name}")
        for component in self.generators + self.loads + self.storage_units:
            if component.bus not in bus_names:
                errors.append(f"{component.name} is connected to missing bus '{component.bus}'")
        for line in self.lines:
            if line.from_bus not in bus_names or line.to_bus not in bus_names:
                errors.append(f"{line.name} refers to a missing bus")
        return errors
