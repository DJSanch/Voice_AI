import importlib
import inspect
import os

from plugins.base_plugin import BasePlugin


class PluginManager:

    def __init__(self):
        self.plugins = []

    def register(self, plugin):
        if plugin is None:
            return

        self.plugins.append(plugin)
        print(f"Loaded plugin: {plugin.name}")

    def load_plugins(self, services, plugin_folder="installed"):
        """Load installed plugins from the plugins.installed package."""

        self.plugins.clear()

        package_name = f"{__package__}.{plugin_folder}"
        plugin_dir = os.path.join(
            os.path.dirname(__file__),
            plugin_folder
        )

        for filename in sorted(os.listdir(plugin_dir)):
            if not filename.endswith(".py") or filename == "__init__.py":
                continue

            module_name = f"{package_name}.{filename[:-3]}"
            module = importlib.import_module(module_name)
            plugin_class = self._find_plugin_class(module)

            if plugin_class is None:
                continue

            plugin = self._create_plugin(plugin_class, services)
            self.register(plugin)

    def _find_plugin_class(self, module):
        for attribute_name in dir(module):
            attribute = getattr(module, attribute_name)

            if (
                inspect.isclass(attribute)
                and issubclass(attribute, BasePlugin)
                and attribute is not BasePlugin
            ):
                return attribute

        return None

    def _create_plugin(self, plugin_class, services):
        signature = inspect.signature(plugin_class.__init__)
        kwargs = {}

        for parameter_name, parameter in list(signature.parameters.items())[1:]:
            if parameter_name in services:
                kwargs[parameter_name] = services[parameter_name]
                continue

            if parameter_name.endswith("_service"):
                alias = parameter_name[: -len("_service")]

                if alias in services:
                    kwargs[parameter_name] = services[alias]
                    continue

            if parameter_name in {"manager", "plugin_manager"}:
                kwargs[parameter_name] = services.get(
                    "plugin_manager",
                    services.get("manager")
                )
                continue

            if parameter_name == "tts" and "tts" in services:
                kwargs[parameter_name] = services["tts"]
                continue

            print(
                f"Skipping plugin {plugin_class.__name__}:"
                f" missing dependency '{parameter_name}'"
            )

            return None

        return plugin_class(**kwargs)

    def find_plugin(self, command):
        for plugin in self.plugins:
            if plugin.can_handle(command):
                return plugin

        return None

    def list_plugins(self):
        result = "Installed plugins:\n\n"

        for plugin in self.plugins:
            result += (
                f"{plugin.name}\n"
                f"Version: {plugin.version}\n"
                f"{plugin.description}\n\n"
            )

        return result