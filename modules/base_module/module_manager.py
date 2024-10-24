# module_manager.py
import importlib
import os
import sys

# module_manager.py
class ModuleManager:
    def __init__(self):
        self.modules = []

    def register_routes(self, app):
        """Register all module routes with the Flask app."""
        for module in self.modules:
            routes = module.get_routes()
            for route in routes:
                if len(route) == 3:  # If the HTTP method is specified
                    app.add_url_rule(route[0], view_func=route[1], methods=route[2])
                else:  # Default to GET
                    app.add_url_rule(route[0], view_func=route[1], methods=['GET'])


    def add_module(self, module):
        """Add a module to the list of managed modules."""
        self.modules.append(module)

    def initialize_modules(self, module_instances):
        """Add and initialize all modules."""
        for module_instance in module_instances:
            self.add_module(module_instance)
