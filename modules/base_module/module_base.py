from abc import ABC, abstractmethod

class ModuleBase(ABC):
    """
    Base class for all modules.
    Modules should inherit from this class and implement the required methods.
    """

    @abstractmethod
    def initialize(self):
        """Initialize the module. This will be called when the module is loaded."""
        pass

    @abstractmethod
    def get_routes(self):
        """Return the Flask routes (if any) that the module provides."""
        return []
