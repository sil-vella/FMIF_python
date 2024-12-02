from abc import ABC, abstractmethod

class pluginBase(ABC):
    """
    Base class for all plugins.
    plugins should inherit from this class and implement the required methods.
    """

    @abstractmethod
    def initialize(self):
        """Initialize the plugin. This will be called when the plugin is loaded."""
        pass

    @abstractmethod
    def get_routes(self):
        """Return the Flask routes (if any) that the plugin provides."""
        return []
