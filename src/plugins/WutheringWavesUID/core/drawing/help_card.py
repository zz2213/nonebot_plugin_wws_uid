# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/core/drawing/help_card.py

import json
from pathlib import Path
from typing import Dict, Any, Optional, List
import aiofiles
from PIL import Image, ImageDraw, ImageFont
from nonebot.log import logger

# --- 导入我们迁移的工具 ---
from ..utils.fonts import WavesFonts
from ..utils.image_helpers import crop_center_img, add_footer

# --- 导入完成 ---


# --- 资源路径定义 ---
# 适配修改：路径指向 core/data/help/
DATA_PATH = Path(__file__).parent.parent.parent / "core" / "data" / "help"
HELP_JSON_PATH = DATA_PATH / "help.json"
CHANGE_JSON_PATH = DATA_PATH / "change_help.json"

# 适配修改：路径指向 assets/images/help/ 下的对应子目录
# (基于你之前的迁移操作)
ASSETS_PATH = Path(__file__).parent.parent.parent / "assets" / "images" / "help"
BG_PATH = ASSETS_PATH / "texture2d"
ICON_PATH = ASSETS_PATH / "icon_path"
CHANGE_ICON_PATH = ASSETS_PATH / "change_icon_path"


# --- 路径定义完成 ---


async def _load_help_json() -> dict:
  """异步加载 help.json"""
  try:
    async with aiofiles.open(HELP_JSON_PATH, 'r', encoding='utf-8') as f:
      content = await f.read()
      return json.loads(content)
  except Exception as e:
    logger.error(f"Failed to load help.json: {e}")
    return {}


async def _load_change_json() -> dict:
  """异步加载 change_help.json"""
  try:
    async with aiofiles.open(CHANGE_JSON_PATH, 'r', encoding='utf-8') as f:
      content = await f.read()
      return json.loads(content)
  except Exception as e:
    logger.error(f"Failed to load change_help.json: {e}")
    return {}


async def draw_help_card() -> Optional[Image.Image]:
  """
  绘制帮助菜单图
  (迁移自 wutheringwaves_help/get_help.py)
  """
  try:
    # 1. 加载数据
    help_data = await _load_help_json()
    change_data = await _load_change_json()

    if not help_data or not change_data:
      logger.error("Help JSON data is missing.")
      return None

    all_cag = list(help_data.keys())
    all_change = list(change_data.keys())

    # 2. 初始化画布
    bg = Image.open(BG_PATH / "bg.jpg").convert("RGBA")
    base_img = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(base_img)

    # 3. 绘制标题
    banner_bg = Image.open(BG_PATH / "banner_bg.jpg").convert("RGBA")
    base_img.paste(banner_bg, (0, 0), banner_bg)
    draw.text(
        (500, 60), "鸣潮 UID 插件 帮助菜单",
        fill="white", font=WavesFonts.waves_font_36, anchor="mm"
    )
    draw.text(
        (500, 110), "发送 [鸣潮帮助 + 序号] 查看特定分类",
        fill="white", font=WavesFonts.waves_font_24, anchor="mm"
    )

    # 4. 绘制分类按钮 (change.json)
    change_bg = Image.open(BG_PATH / "cag_bg.png").convert("RGBA")
    x_c_offset = 50
    y_c_offset = 160
    for i, cag in enumerate(all_change):
      c_bg = change_bg.copy()
      draw_c = ImageDraw.Draw(c_bg)

      try:
        c_icon = Image.open(CHANGE_ICON_PATH / change_data[cag]).convert("RGBA")
        c_icon = c_icon.resize((50, 50))
        c_bg.paste(c_icon, (20, 20), c_icon)
      except Exception as e:
        logger.warning(f"Missing change icon {change_data[cag]}: {e}")

      draw_c.text(
          (80, 45), cag, fill="white",
          font=WavesFonts.waves_font_24, anchor="lm"
      )

      base_img.paste(c_bg, (x_c_offset, y_c_offset), c_bg)
      x_c_offset += 200
      if (i + 1) % 4 == 0:
        x_c_offset = 50
        y_c_offset += 100

    # 5. 绘制所有命令 (help.json)
    y_offset = y_c_offset + 100  # 接上一个模块的 Y 轴

    for cag in all_cag:
      # 绘制分类标题
      draw.text(
          (60, y_offset), cag,
          fill="white", font=WavesFonts.waves_font_28
      )
      y_offset += 60

      # 绘制命令
      item_bg = Image.open(BG_PATH / "item.png").convert("RGBA")
      x_offset = 50
      item_count = 0

      for item in help_data[cag]:
        i_bg = item_bg.copy()
        draw_i = ImageDraw.Draw(i_bg)

        try:
          i_icon = Image.open(ICON_PATH / item["icon"]).convert("RGBA")
          i_icon = i_icon.resize((50, 50))
          i_bg.paste(i_icon, (15, 20), i_icon)
        except Exception as e:
          logger.warning(f"Missing item icon {item['icon']}: {e}")

        draw_i.text(
            (70, 30), item["name"],
            fill="white", font=WavesFonts.waves_font_20
        )
        draw_i.text(
            (70, 60), item["introduce"],
            fill=(200, 200, 200), font=WavesFonts.waves_font_16
        )

        base_img.paste(i_bg, (x_offset, y_offset), i_bg)
        x_offset += 310
        item_count += 1
        if item_count % 3 == 0:
          x_offset = 50
          y_offset += 100

      # 换行
      if item_count % 3 != 0:
        y_offset += 100

      y_offset += 20  # 增加分类间距

    # --- 6. 合成 ---
    # 裁剪到实际高度
    base_img = base_img.crop((0, 0, 1000, y_offset + 60))

    # 创建一个匹配的新背景
    final_bg = Image.open(BG_PATH / "bg.jpg").convert("RGBA")
    final_bg = crop_center_img(final_bg, 1000, y_offset + 60)

    final_bg.paste(base_img, (0, 0), base_img)
    final_bg = add_footer(final_bg)

    return final_bg

  except Exception as e:
    logger.error(f"绘制帮助菜单失败: {e}")
    logger.exception(e)
    return None