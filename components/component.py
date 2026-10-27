from abc import ABC, abstractmethod


class Component(ABC):
    """Base class for all power-system components."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def info(self) -> str:
        """Return a human-readable description."""
        raise NotImplementedError
