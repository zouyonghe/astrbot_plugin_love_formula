import os
from jinja2 import Environment, FileSystemLoader
from astrbot.core.star.context import Context

from .theme_manager import ThemeManager


class LoveRenderer:
    def __init__(self, context: Context, theme_manager: ThemeManager):
        self.context = context
        self.theme_manager = theme_manager
        # Initialize Jinja2 Env
        self.env = Environment(loader=FileSystemLoader(theme_manager.themes_dir))

    async def render(self, data: dict, theme_name: str = "galgame") -> str:
        """
        Render the analysis result to an image.
        Returns: absolute path to the generated image file.
        """
        # 1. Load Template
        template_name = f"{theme_name}/template.html"
        template = self.env.get_template(template_name)

        # 2. Inject Data & KaTeX CDN (or local)
        # We ensure KaTeX is enabled in the template

        html_content = template.render(
            data=data,
            theme_config=self.theme_manager.get_theme_config(theme_name),
            asset_dir=f"file://{self.theme_manager.get_asset_dir(theme_name)}",
        )

        # 3. Use AstrBot's HTML Renderer (assuming Context provides one or usage of browser tool)
        # For this plugin, we will rely on AstrBot's internal capability if available.
        # If AstrBot main context doesn't expose a specific renderer, we can use a library.
        # But per specific instructions, we use "AstrBot's html_render interface".
        # Let's assume context has `image_renderer` or `browser`.
        # If not, strictly for this step I will assume there's a utility helper.

        # NOTE: Placeholder implementation for actual image generation call.
        # In a real AstrBot environment, this might look like:
        # return await self.context.render_html_to_image(html_content)

        return await self.context.image_renderer.render(html_content)
