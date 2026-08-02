import os
import importlib

class PluginManager:

    def __init__(self):
        self.plugins = []
        self.load_plugins()

    def load_plugins(self):
        self.plugins.clear()

        plugin_dir = os.path.dirname(__file__)

        for filename in os.listdir(plugin_dir):

            if (
                filename.endswith(".py")
                and filename not in [
                    "__init__.py",
                    "plugin_manager.py",
                    "base_plugin.py"
                ]
            ):

                module_name = f"plugins.{filename[:-3]}"
                module = importlib.import_module(module_name)

                if hasattr(module, "Plugin"):
                    self.plugins.append(module.Plugin())