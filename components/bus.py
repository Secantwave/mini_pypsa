from .component import Component


class Bus(Component):
    """Electrical connection point in the simplified grid."""

    def __init__(
        self,
        name: str,
        voltage: float = 11.0,
        x: float | None = None,
        y: float | None = None,
    ):
        super().__init__(name)
        self.voltage = voltage
        self.x = float(x) if x is not None else None
        self.y = float(y) if y is not None else None
        self.components = []

    def connect(self, component: Component) -> None:
        if component not in self.components:
            self.components.append(component)

    def info(self) -> str:
        return f"Bus {self.name}: {self.voltage:g} kV, {len(self.components)} connected components"
