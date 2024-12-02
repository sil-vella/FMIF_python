import json
from plugins.main_plugin.main_plugin import Mainplugin
from plugins.login_plugin.login_plugin import Loginplugin

class pluginFactory:
    def __init__(self, config_file='plugins/base_plugin/config/plugin_conf.json'):
        self.config_file = config_file

    def load_plugins(self):
        """Manually load plugins based on config file and hardcoded plugin imports."""
        plugins = []

        # Dictionary to map plugin names and class names to the actual classes
        plugin_switch = {
            ("main_plugin", "Mainplugin"): Mainplugin,
            ("login_plugin", "Loginplugin"): Loginplugin
            # Add other plugins here when needed.
        }

        # Load the configuration file
        with open(self.config_file, 'r') as f:
            config = json.load(f)

        # Iterate over the plugins in the config file
        for plugin_conf in config['plugins']:
            if plugin_conf['enabled'] and plugin_conf['init_at_startup']:
                plugin_name = plugin_conf['name']
                class_name = plugin_conf['class_name']

                # Manually load plugins using the dictionary
                try:
                    plugin_class = plugin_switch.get((plugin_name, class_name))
                    if not plugin_class:
                        raise Exception(f"Unknown plugin or class: {plugin_name}.{class_name}")

                    # Initialize the plugin
                    plugin_instance = plugin_class()
                    plugin_instance.initialize()
                    plugins.append(plugin_instance)
                    print(f"plugin '{plugin_name}' ({class_name}) initialized.")
                except Exception as e:
                    print(f"Failed to load plugin '{plugin_name}': {e}")

        return plugins
