# plugin_manager.py
import importlib
import os
import sys

# plugin_manager.py
class pluginManager:
    def __init__(self):
        self.plugins = []

    def register_routes(self, app):
        """Register all plugin routes with the Flask app."""
        for plugin in self.plugins:
            routes = plugin.get_routes()
            for route in routes:
                if len(route) == 3:  # If the HTTP method is specified
                    app.add_url_rule(route[0], view_func=route[1], methods=route[2])
                else:  # Default to GET
                    app.add_url_rule(route[0], view_func=route[1], methods=['GET'])


    def add_plugin(self, plugin):
        """Add a plugin to the list of managed plugins."""
        self.plugins.append(plugin)

    def initialize_plugins(self, plugin_instances):
        """Add and initialize all plugins."""
        for plugin_instance in plugin_instances:
            self.add_plugin(plugin_instance)
