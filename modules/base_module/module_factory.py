import json
from modules.main_module.main_module import MainModule
from modules.login_module.login_module import LoginModule

class ModuleFactory:
    def __init__(self, config_file='modules/base_module/config/module_conf.json'):
        self.config_file = config_file

    def load_modules(self):
        """Manually load modules based on config file and hardcoded module imports."""
        modules = []

        # Dictionary to map module names and class names to the actual classes
        module_switch = {
            ("main_module", "MainModule"): MainModule,
            ("login_module", "LoginModule"): LoginModule
            # Add other modules here when needed.
        }

        # Load the configuration file
        with open(self.config_file, 'r') as f:
            config = json.load(f)

        # Iterate over the modules in the config file
        for module_conf in config['modules']:
            if module_conf['enabled'] and module_conf['init_at_startup']:
                module_name = module_conf['name']
                class_name = module_conf['class_name']

                # Manually load modules using the dictionary
                try:
                    module_class = module_switch.get((module_name, class_name))
                    if not module_class:
                        raise Exception(f"Unknown module or class: {module_name}.{class_name}")

                    # Initialize the module
                    module_instance = module_class()
                    module_instance.initialize()
                    modules.append(module_instance)
                    print(f"Module '{module_name}' ({class_name}) initialized.")
                except Exception as e:
                    print(f"Failed to load module '{module_name}': {e}")

        return modules
