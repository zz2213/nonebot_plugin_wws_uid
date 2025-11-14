# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/core/drawing/materials_card.py

import asyncio
from io import BytesIO
from pathlib import Path
from typing import Dict, Any, Optional, List

from PIL import Image, ImageDraw, ImageFont
from nonebot.log import logger

# --- 导入我们迁移的工具 ---
from ..utils.fonts import WavesFonts
from ..utils.image_helpers import add_footer, get_waves_bg, get_square_avatar
from ..api.client import api_client
# 导入 WikiService 以使用其 ID->Name 映射
from ..services.wiki_service import wiki_service
# 导入日历数据模型
from ..services.calendar_service import CalendarData

# --- 导入完成 ---


# --- 资源路径定义 ---
ASSETS_PATH = Path(__file__).parent.parent.parent / "assets"
# 适配修改：指向 assets/images/develop/
TEXT_PATH = ASSETS_PATH / "images" / "develop"


# --- 路径定义完成 ---


async def _download_icon(url: str, size: Optional[tuple[int, int]] = None) -> Optional[Image.Image]:
  """使用 api_client 下载图标"""
  if not url:
    return None
  try:
    resp = await api_client.get(url)
    resp.raise_for_status()
    icon = Image.open(BytesIO(resp.content)).convert("RGBA")
    if size:
      icon = icon.resize(size, Image.Resampling.LANCZOS)
    return icon
  except Exception as e:
    logger.warning(f"Failed to download icon {url}: {e}")
    return None


async def draw_material_card(data: CalendarData) -> Optional[Image.Image]:
  """
  绘制每日材料图
  (迁移自 wutheringwaves_develop/develop.py)
  """
  try:
    # 确保 wiki_service 的 id->name 映射已加载
    await wiki_service._load_maps()
    id_name_map = wiki_service._id_name_map or {}

    def get_material_name_by_id(mat_id: int) -> str:
      """(辅助函数) 从 id_name.json 获取材料名"""
      return id_name_map.get(str(mat_id), f"ID:{mat_id}")

    # --- 1. 提取数据 ---
    today_weekday = data.weekday
    char_materials = data.develop.char
    weapon_materials = data.develop.weapon

    # --- 2. 初始化画布 ---
    card_h = 240 + 120 * (len(char_materials) + len(weapon_materials))
    bg = get_waves_bg(800, card_h)
    base_img = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(base_img)

    # 绘制标题栏
    top_bg = Image.open(TEXT_PATH / "top-bg.png").convert("RGBA")
    base_img.paste(top_bg, (0, 0), top_bg)
    draw.text(
        (400, 60), f"今日 {today_weekday} 可刷取材料",
        fill="white", font=WavesFonts.waves_font_36, anchor="mm"
    )

    # --- 3. 绘制条目 ---
    y_offset = 120

    # 绘制角色材料
    if char_materials:
      header_img = Image.open(TEXT_PATH / "material-header.png").convert("RGBA")
      base_img.paste(header_img, (20, y_offset), header_img)
      draw.text(
          (60, y_offset + 30), "角色天赋材料",
          fill="white", font=WavesFonts.waves_font_24
      )
      y_offset += 60

      for mat_id in char_materials:
        mat_name = get_material_name_by_id(mat_id)
        # TODO: 缺少材料图标下载逻辑，暂时使用角色头像
        icon = await get_square_avatar(mat_id)

        bar_bg = Image.open(TEXT_PATH / "material-star-5.png").convert("RGBA")
        if icon:
          icon = icon.resize((80, 80))
          bar_bg.paste(icon, (20, 20), icon)
        draw_bar = ImageDraw.Draw(bar_bg)
        draw_bar.text(
            (120, 60), mat_name,
            fill="white", font=WavesFonts.waves_font_24, anchor="lm"
        )
        base_img.paste(bar_bg, (40, y_offset), bar_bg)
        y_offset += 120

    # 绘制武器材料
    if weapon_materials:
      header_img = Image.open(TEXT_PATH / "material-header.png").convert("RGBA")
      base_img.paste(header_img, (20, y_offset), header_img)
      draw.text(
          (60, y_offset + 30), "武器突破材料",
          fill="white", font=WavesFonts.waves_font_24
      )
      y_offset += 60

      for mat_id in weapon_materials:
        mat_name = get_material_name_by_id(mat_id)
        # TODO: 缺少材料图标下载逻辑，暂时使用武器图标
        icon = await get_square_weapon(mat_id)

        bar_bg = Image.open(TEXT_PATH / "material-star-5.png").convert("RGBA")
        if icon:
          icon = icon.resize((80, 80))
          bar_bg.paste(icon, (20, 20), icon)
        draw_bar = ImageDraw.Draw(bar_bg)
        draw_bar.text(
            (120, 60), mat_name,
            fill="white", font=WavesFonts.waves_font_24, anchor="lm"
        )
        base_img.paste(bar_bg, (40, y_offset), bar_bg)
        y_offset += 120

    # --- 4. 合成 ---
    bg.paste(base_img, (0, 0), base_img)
    bg = add_footer(bg)

    return bg

  except Exception as e:
    logger.error(f"绘制每日材料失败: {e}")
    logger.exception(e)
    return None