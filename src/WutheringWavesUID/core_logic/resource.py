from pathlib import Path
from jinja2 import Template

# 资源路径管理
PLUGIN_PATH = Path(__file__).parent.parent
ASSETS_PATH = PLUGIN_PATH / "assets"
TEMPLATES_PATH = PLUGIN_PATH / "templates"

def get_template(template_name: str) -> Template:
    """获取模板"""
    template_file = TEMPLATES_PATH / template_name
    if template_file.exists():
        with open(template_file, 'r', encoding='utf-8') as f:
            return Template(f.read())
    return Template("")  # 返回空模板

# 字体路径
def get_font_path(font_name: str) -> Path:
    """获取字体路径"""
    return ASSETS_PATH / "fonts" / font_name