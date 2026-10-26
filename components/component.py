from abc import ABC, abstractmethod


class Component(ABC):
    """Common base class for every power-grid component."""

    def __init__(self, name: str):
        self.name = name
        self.status = "active"

    def activate(self) -> None:
        self.status = "active"

    def deactivate(self) -> None:
        self.status = "inactive"

    def info(self) -> dict:
        return {"name": self.name, "status": self.status}

    @abstractmethod
    def validate(self) -> bool:
        """Return True when the component's values are valid."""
        raise NotImplementedError
