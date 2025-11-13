# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/core/utils/fonts.py

from pathlib import Path

# 使用 pathlib 定位字体文件的正确路径
# __file__ -> .../core/utils/fonts.py
# .parent -> .../core/utils/
# .parent.parent -> .../core/
# .parent.parent.parent -> .../WutheringWavesUID/
# 最终路径 -> .../WutheringWavesUID/assets/fonts/
FONTS_PATH = Path(__file__).parent.parent.parent / "assets" / "fonts"


class WavesFonts:
  """字体管理器"""

  # 将原有的 f-string 路径改为使用 Path 对象拼接，确保跨平台兼容性

  # 主字体
  waves_font = str(FONTS_PATH / "waves_fonts.ttf")

  # Emoji 字体
  emoji_font = str(FONTS_PATH / "NotoColorEmoji.ttf")

  # Arial (用于英文)
  arial_bold_font = str(FONTS_PATH / "arial-unicode-ms-bold.ttf")