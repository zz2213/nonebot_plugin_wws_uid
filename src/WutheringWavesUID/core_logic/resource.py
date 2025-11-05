# wws_native/core_logic/resource.py
from pathlib import Path
from PIL import ImageFont
from nonebot.log import logger

# [重构] 彻底移除 gsuid_core 依赖
# 路径基准点: .../WutheringWavesUID/core_logic/resource.py
# 我们需要定位到 .../WutheringWavesUID/assets/
ASSETS_PATH = Path(__file__).parent.parent / "assets"
FONTS_PATH = ASSETS_PATH / "fonts"


# --- [重构] 移植自 WutheringWavesUID/utils/fonts/waves_fonts.py ---
# 并修正了您的指正：使用这三个正确的字体

class WutheingWavesFont:
  """字体加载器，基于原项目代码重构"""

  def __init__(
      self,
      font_name: str = "waves_fonts.ttf",
      font2_name: str = "arial-unicode-ms-bold.ttf",
      emoji_name: str = "NotoColorEmoji.ttf"
  ):
    font_path = FONTS_PATH / font_name
    font2_path = FONTS_PATH / font2_name
    emoji_path = FONTS_PATH / emoji_name

    # 验证字体文件是否存在
    for path in [font_path, font2_path, emoji_path]:
      if not path.exists():
        logger.error(f"字体文件缺失! {path} 不存在。")
        logger.error("请从 WutheringWavesUID/utils/fonts/ 目录将字体复制到 /assets/fonts/ 目录中")

    self.font_list = [str(font_path), str(font2_path), str(emoji_path)]
    logger.info(f"已加载字体: {self.font_list}")

  def get_font(self, font_size: int, font_name: str | None = None) -> ImageFont.FreeTypeFont:
    """
    根据字号和字体名称获取Pillow字体对象
    (原项目`get_font`的简化版，只处理 FreeType)
    """
    path = font_name or self.font_list[0]
    try:
      return ImageFont.truetype(path, font_size)
    except IOError:
      logger.warning(f"字体 {path} 加载失败！将使用默认字体。")
      return ImageFont.load_default()


# 实例化一个全局字体对象，供绘图模块使用
WavesFont = WutheingWavesFont()


# --- 字体部分结束 ---

# --- [重构] 移植自 WutheringWavesUID/utils/resource/RESOURCE_PATH.py ---
# 我们不再需要 PARENT_PATH，而是直接提供函数

def get_font(size: int) -> ImageFont.FreeTypeFont:
  """获取指定大小的主字体"""
  return WavesFont.get_font(size)


def get_texture_path(name: str) -> Path:
  """
  [原生实现] 从 assets 目录获取图片资源
  (这是对原项目 `get_res_path` 的功能替换)
  """
  # 在 assets 根目录查找
  path = ASSETS_PATH / name
  if path.exists():
    return path

  # 如果找不到，也去 texture2d 子目录(为了兼容旧逻辑)
  path = ASSETS_PATH / "texture2d" / name
  if path.exists():
    return path

  logger.warning(f"资源文件 {name} 未在 assets/ 或 assets/texture2d/ 中找到！")
  return path  # 返回一个不存在的路径，调用处会处理 FileNotFoundError


# --- 占位符 ---
def get_icon_path(name: str, h: bool = False) -> Path:
  # 随着功能迁移，我们需要从原项目 WutheringWavesUID/wutheringwaves_help/icon_path 等
  # 目录中把图片复制到 assets/icons/ 目录，然后在这里实现
  return ASSETS_PATH / "icons" / f"{name}.png"