import os

class PluginManager:
    def __init__(self, plugins_meta):
        self.plugins_meta = plugins_meta
        self.plugins = {}

    def load_plugins(self):
        plugin_dir = os.path.join(os.getcwd(), "plugins")
        if not os.path.exists(plugin_dir):
            print("Plugins directory not found.")
            return 0

        for item in os.listdir(plugin_dir):
            item_path = os.path.join(plugin_dir, item)
            if os.path.isdir(item_path):
                self.load_directory(item_path)
            elif os.path.isfile(item_path):
                self.load_file(item_path)

    def load_directory(self, dir_path):
        if self.is_valid_plugin(dir_path):
            self.plugins[dir_path] = None

        for item in os.listdir(dir_path):
            item_path = os.path.join(dir_path, item)
            if os.path.isfile(item_path) and os.access(item_path, os.X_OK):
                self.plugins[dir_path] = item_path

    def load_file(self, file_path):
        dir_path = os.path.dirname(file_path)
        if self.is_valid_plugin(dir_path):
            self.plugins[dir_path] = file_path

    def is_valid_plugin(self, path):
        return any(meta in path for meta in self.plugins_meta)
    
    def get_plugin_executable_path(self, plugin_name):
        for plugin_dir, plugin_path in self.plugins.items():
            if plugin_path and os.path.basename(plugin_path) == plugin_name:
                return plugin_path

        return None