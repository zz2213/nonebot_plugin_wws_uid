# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/core/drawing/stats_card.py

import asyncio
from io import BytesIO
from pathlib import Path
from typing import Dict, Any, List, Optional

from PIL import Image, ImageDraw, ImageFont
from nonebot.log import logger

# --- 导入我们迁移的工具 ---
from ..utils.fonts import WavesFonts
from ..utils.image_helpers import (
  add_footer, get_waves_bg, get_square_avatar, get_role_pile_old
)
from ..api.client import api_client

# --- 导入 API 模型 ---
from ..api.ranking_api import (
  RoleHoldRate, AbyssRecord, ABYSS_TYPE_MAP_REVERSE, SlashAppearRate
)

# --- 导入完成 ---


# --- 资源路径定义 ---
ASSETS_PATH = Path(__file__).parent.parent.parent / "assets"
# 适配修改：指向 assets/images/query/
TEXT_PATH = ASSETS_PATH / "images" / "query"


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


# --- 1. 角色持有率 (Hold Rate) ---

async def _draw_hold_rate_bar(
    role_data: RoleHoldRate
) -> Image.Image:
  """(辅助函数) 绘制单个角色持有率条目"""
  rarity = 5 if role_data.char_id > 1100 else 4  # 简易判断

  bg_img = Image.open(TEXT_PATH / f"star{rarity}_bg.png").convert("RGBA")
  fg_img = Image.open(TEXT_PATH / f"star{rarity}_fg.png").convert("RGBA")
  bar_img = Image.open(TEXT_PATH / "bar1.png").convert("RGBA")

  base_img = Image.new("RGBA", bg_img.size, (0, 0, 0, 0))
  draw = ImageDraw.Draw(base_img)

  # 角色头像
  avatar_img = await get_square_avatar(role_data.char_id)
  avatar_img = avatar_img.resize((100, 100))
  base_img.paste(avatar_img, (10, 10), avatar_img)

  # 粘贴背景和前景
  base_img.paste(bg_img, (0, 0), bg_img)
  base_img.paste(fg_img, (0, 0), fg_img)

  # 绘制持有率
  draw.text(
      (130, 44), f"持有率: {role_data.rate * 100:.1f}%",
      fill="white", font=WavesFonts.waves_font_24
  )

  # 绘制共鸣链进度条
  x_offset = 130
  total_chain = sum(role_data.chain_rate.values())

  for i in range(7):  # 0-6 链
    chain_rate = role_data.chain_rate.get(str(i), 0.0)
    if chain_rate == 0:
      continue

    bar_w = int(600 * (chain_rate / total_chain))
    if bar_w <= 0:
      continue

    chain_bar = bar_img.crop((0, 0, bar_w, bar_img.height))
    base_img.paste(chain_bar, (x_offset, 80), chain_bar)

    # 绘制共鸣链文字
    text_color = (50, 50, 50) if bar_w < 50 else "white"
    draw.text(
        (x_offset + 5, 84), f"{i}链",
        fill=text_color, font=WavesFonts.waves_font_16
    )
    x_offset += bar_w

  return base_img


async def draw_char_hold_rate_card(
    data: List[RoleHoldRate]
) -> Optional[Image.Image]:
  """
  绘制角色持有率图
  (迁移自 draw_char_hold_rate.py)
  """
  try:
    data.sort(key=lambda x: x.rate, reverse=True)

    # --- 1. 初始化画布 ---
    card_h = 130 * len(data) + 240
    bg = get_waves_bg(800, card_h)  # 复用 bg
    base_img = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(base_img)

    # 绘制标题栏
    title_img = Image.open(TEXT_PATH / "title1.png").convert("RGBA")
    base_img.paste(title_img, (0, 0), title_img)

    # --- 2. 绘制条目 ---
    draw_tasks = [_draw_hold_rate_bar(item) for item in data]
    bar_images = await asyncio.gather(*draw_tasks)

    # --- 3. 粘贴条目 ---
    y_offset = 140
    for bar_img in bar_images:
      base_img.paste(bar_img, (30, y_offset), bar_img)
      y_offset += 130

    # --- 4. 合成 ---
    bg.paste(base_img, (0, 0), base_img)
    bg = add_footer(bg)

    return bg

  except Exception as e:
    logger.error(f"绘制角色持有率失败: {e}")
    logger.exception(e)
    return None


# --- 2. 深塔出场率 (Tower Appear Rate) ---

async def _draw_appear_rate_bar(
    char_data: AbyssUseRate,
    bg_img: Image.Image
) -> Image.Image:
  """(辅助函数) 绘制单个角色出场率条目"""
  base_img = Image.new("RGBA", bg_img.size, (0, 0, 0, 0))
  base_img.paste(bg_img, (0, 0), bg_img)
  draw = ImageDraw.Draw(base_img)

  # 头像
  avatar_img = await get_square_avatar(char_data.char_id)
  avatar_img = avatar_img.resize((60, 60))
  base_img.paste(avatar_img, (10, 10), avatar_img)

  # 出场率
  draw.text(
      (100, 40), f"{char_data.rate * 100:.1f}%",
      fill="white", font=WavesFonts.waves_font_24, anchor="lm"
  )
  return base_img


async def draw_tower_appear_rate_card(
    data: List[AbyssRecord]
) -> Optional[Image.Image]:
  """
  绘制深塔出场率图
  (迁移自 draw_tower_appear_rate.py)
  """
  try:
    bg = Image.open(TEXT_PATH / "tower.jpg").convert("RGBA")
    base_img = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(base_img)

    bar_img = Image.open(TEXT_PATH / "bar2.png").convert("RGBA")

    x_offset_map = {"l4": 80, "m4": 460, "r4": 840}

    for record in data:
      abyss_type = record.abyss_type
      if abyss_type not in x_offset_map:
        continue

      # 绘制区域标题
      title_img_name = f"tower_name_bg_{abyss_type}.png"
      title_img = Image.open(TEXT_PATH / title_img_name).convert("RGBA")
      base_img.paste(title_img, (x_offset_map[abyss_type] - 40, 40), title_img)

      # 绘制角色列表
      y_offset = 120
      draw_tasks = []

      # 排序并取前10
      use_rate_list = sorted(record.use_rate, key=lambda x: x.rate, reverse=True)[:10]

      for char in use_rate_list:
        draw_tasks.append(_draw_appear_rate_bar(char, bar_img))

      bar_images = await asyncio.gather(*draw_tasks)

      for bar_img_item in bar_images:
        base_img.paste(bar_img_item, (x_offset_map[abyss_type], y_offset), bar_img_item)
        y_offset += 90

    # --- 合成 ---
    bg.paste(base_img, (0, 0), base_img)
    bg = add_footer(bg, color="black")

    return bg

  except Exception as e:
    logger.error(f"绘制深塔出场率失败: {e}")
    logger.exception(e)
    return None


# --- 3. 冥海出场率 (Slash Appear Rate) ---

async def draw_slash_appear_rate_card(
    data: List[SlashAppearRate]
) -> Optional[Image.Image]:
  """
  绘制冥海出场率图
  (迁移自 draw_slash_appear_rate.py)
  """
  try:
    bg = Image.open(TEXT_PATH / "slash.jpg").convert("RGBA")
    base_img = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(base_img)

    title_img = Image.open(TEXT_PATH / "title2.png").convert("RGBA")
    base_img.paste(title_img, (0, 0), title_img)

    bar_img = Image.open(TEXT_PATH / "bar2.png").convert("RGBA")

    # 排序并取前10
    data.sort(key=lambda x: x.rate, reverse=True)
    top_10_list = data[:10]

    draw_tasks = []
    for char in top_10_list:
      draw_tasks.append(_draw_appear_rate_bar(char, bar_img))

    bar_images = await asyncio.gather(*draw_tasks)

    # 分成两列
    x_offsets = [80, 460]
    y_offset = 140
    col = 0

    for i, bar_img_item in enumerate(bar_images):
      if i == 5:  # 换列
        col = 1
        y_offset = 140

      base_img.paste(bar_img_item, (x_offsets[col], y_offset), bar_img_item)
      y_offset += 90

    # --- 合成 ---
    bg.paste(base_img, (0, 0), base_img)
    bg = add_footer(bg)

    return bg

  except Exception as e:
    logger.error(f"绘制冥海出场率失败: {e}")
    logger.exception(e)
    return None