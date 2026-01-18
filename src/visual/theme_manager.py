import os
import yaml
from typing import Dict, Any


class ThemeManager:
    def __init__(self, plugin_root: str):
        self.plugin_root = plugin_root
        self.themes_dir = os.path.join(plugin_root, "assets", "themes")
        self.current_theme = "galgame"
        self._cache = {}

    def get_theme_config(self, theme_name: str = None) -> Dict[str, Any]:
        theme = theme_name or self.current_theme
        if theme in self._cache:
            return self._cache[theme]

        config_path = os.path.join(self.themes_dir, theme, "config.yaml")
        if not os.path.exists(config_path):
            raise ValueError(f"Theme {theme} not found at {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        self._cache[theme] = config
        return config

    def get_template_path(self, theme_name: str = None) -> str:
        theme = theme_name or self.current_theme
        return os.path.join(self.themes_dir, theme, "template.html")

    def get_asset_dir(self, theme_name: str = None) -> str:
        theme = theme_name or self.current_theme
        return os.path.join(self.themes_dir, theme, "assets")
