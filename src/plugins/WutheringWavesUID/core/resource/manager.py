from pathlib import Path
from jinja2 import Template

class ResourceManager:
    """资源管理器"""

    def __init__(self):
        self.plugin_path = Path(__file__).parent.parent.parent
        self.assets_path = self.plugin_path / "assets"
        self.templates_path = self.assets_path / "templates"
        self.fonts_path = self.assets_path / "fonts"

    def get_template(self, template_name: str) -> Template:
        """获取模板"""
        template_file = self.templates_path / template_name
        if template_file.exists():
            with open(template_file, 'r', encoding='utf-8') as f:
                return Template(f.read())
        return Template("")  # 返回空模板

    def get_font_path(self, font_name: str) -> Path:
        """获取字体路径"""
        return self.fonts_path / font_name

    def render_template(self, template_name: str, **kwargs) -> str:
        """渲染模板"""
        template = self.get_template(template_name)
        return template.render(**kwargs)

resource_manager = ResourceManager()