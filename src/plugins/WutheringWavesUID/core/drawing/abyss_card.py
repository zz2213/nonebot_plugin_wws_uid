# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/core/drawing/abyss_card.py

import asyncio
from io import BytesIO
from pathlib import Path
from typing import Dict, Any, Optional, List

from PIL import Image, ImageDraw, ImageFont
from nonebot.log import logger

# --- 导入我们迁移的工具 ---
from ..utils.fonts import WavesFonts
from ..utils.image_helpers import (
  add_footer, get_waves_bg, get_square_avatar, crop_center_img
)
from ..utils.drawing_helpers import draw_pic  # 用于绘制头像
from ..api.client import api_client

# --- 导入完成 ---


# --- 资源路径定义 ---
ASSETS_PATH = Path(__file__).parent.parent.parent / "assets"
# 适配修改：指向 assets/images/abyss/
TEXT_PATH = ASSETS_PATH / "images" / "abyss"


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


async def _draw_header(
    base_img: Image.Image,
    user_info: Dict[str, Any],
    user_id: str
) -> Image.Image:
  """绘制通用的头部信息"""
  draw = ImageDraw.Draw(base_img)

  title_bar = Image.open(TEXT_PATH / "title_bar.png").convert("RGBA")
  base_img.paste(title_bar, (0, 0), title_bar)

  # 绘制QQ头像
  avatar_img = await draw_pic(user_id)  # draw_pic 接收 qid
  if avatar_img:
    avatar_img = avatar_img.resize((100, 100))
    base_img.paste(avatar_img, (20, 20), avatar_img)

  # 绘制玩家信息
  draw.text(
      (140, 48), user_info.get("nickname", "Unknown"),
      fill="white", font=WavesFonts.waves_font_24
  )
  draw.text(
      (140, 84), f"UID: {user_info.get('uid', '...-...')}",
      fill="white", font=WavesFonts.waves_font_22
  )
  return base_img


# --- 1. 深境之塔 (Tower) ---

async def _draw_tower_bar(
    tower_item: Dict[str, Any]
) -> Image.Image:
  """(辅助函数) 绘制单个塔条目"""
  tower_name = tower_item.get("name", "Unknown")
  bg_name = "tower_name_bg1.png"  # 默认为残响之塔
  if "深境" in tower_name:
    bg_name = "tower_name_bg2.png"
  elif "回音" in tower_name:
    bg_name = "tower_name_bg3.png"

  base_img = Image.open(TEXT_PATH / bg_name).convert("RGBA")
  draw = ImageDraw.Draw(base_img)

  # 绘制塔名
  draw.text(
      (60, 40), tower_name,
      fill="white", font=WavesFonts.waves_font_24, anchor="lm"
  )

  # 绘制星级
  star_full = Image.open(TEXT_PATH / "star_full.png").convert("RGBA")
  star_empty = Image.open(TEXT_PATH / "star_empty.png").convert("RGBA")

  total_star = tower_item.get("totalStar", 0)
  max_star = 12  # 深塔每区都是12星

  star_x = 760
  for i in range(max_star):
    star_img = star_full if i < total_star else star_empty
    base_img.paste(star_img, (star_x + i * 40, 25), star_img)

  return base_img


async def draw_tower_card(
    user_info: Dict[str, Any],
    tower_data: Dict[str, Any],
    user_id: str
) -> Optional[Image.Image]:
  """
  绘制深境之塔卡片
  (迁移自 draw_abyss_card.py)
  """
  try:
    tower_list = tower_data.get("towerList", [])
    if not tower_list:
      return None

    # --- 1. 初始化画布 ---
    card_h = 90 * len(tower_list) + 240
    bg = get_waves_bg(1300, card_h, "abyss_bg_1")
    base_img = Image.new("RGBA", bg.size, (0, 0, 0, 0))

    base_img = await _draw_header(base_img, user_info, user_id)
    draw = ImageDraw.Draw(base_img)

    # 绘制总星数
    draw.text(
        (1260, 84), f"总星数: {tower_data.get('totalStar', 0)}",
        fill="white", font=WavesFonts.waves_font_24, anchor="rm"
    )

    # --- 2. 绘制条目 ---
    draw_tasks = [_draw_tower_bar(item) for item in tower_list]
    bar_images = await asyncio.gather(*draw_tasks)

    # --- 3. 粘贴条目 ---
    y_offset = 140
    for bar_img in bar_images:
      base_img.paste(bar_img, (60, y_offset), bar_img)
      y_offset += 90

    # --- 4. 合成 ---
    bg.paste(base_img, (0, 0), base_img)
    bg = add_footer(bg)

    return bg

  except Exception as e:
    logger.error(f"绘制深塔卡片失败 (uid: {user_info.get('uid')}): {e}")
    logger.exception(e)
    return None


# --- 2. 全息战略 (Challenge) ---

async def _draw_challenge_bar(
    challenge_item: Dict[str, Any]
) -> Image.Image:
  """(辅助函数) 绘制单个全息条目"""
  base_img = Image.open(TEXT_PATH / "name_bg.png").convert("RGBA")
  draw = ImageDraw.Draw(base_img)

  # 绘制区域名
  draw.text(
      (60, 40), challenge_item.get("name", "Unknown"),
      fill="white", font=WavesFonts.waves_font_24, anchor="lm"
  )

  # 绘制难度
  difficulty = challenge_item.get("difficulty", 0)
  diff_img = Image.open(TEXT_PATH / f"difficulty_{difficulty}.png").convert("RGBA")
  base_img.paste(diff_img, (1100, 20), diff_img)

  # 绘制队伍
  team_list = challenge_item.get("team", [])
  icon_tasks = [get_square_avatar(role.get("id")) for role in team_list[:3]]
  icon_images = await asyncio.gather(*icon_tasks)

  team_bg = Image.open(TEXT_PATH / "char_bg4.png").convert("RGBA")
  x_offset = 700
  for icon in icon_images:
    icon = icon.resize((60, 60))
    bar_img = team_bg.copy()
    bar_img.paste(icon, (10, 10), icon)
    base_img.paste(bar_img, (x_offset, 0), bar_img)
    x_offset += 90

  return base_img


async def draw_challenge_card(
    user_info: Dict[str, Any],
    challenge_data: Dict[str, Any],
    user_id: str
) -> Optional[Image.Image]:
  """
  绘制全息战略卡片
  (迁移自 draw_challenge_card.py)
  """
  try:
    challenge_list = challenge_data.get("challengeList", [])
    if not challenge_list:
      return None

    # --- 1. 初始化画布 ---
    card_h = 90 * len(challenge_list) + 240
    bg = get_waves_bg(1300, card_h, "abyss_bg_2")
    base_img = Image.new("RGBA", bg.size, (0, 0, 0, 0))

    base_img = await _draw_header(base_img, user_info, user_id)

    # --- 2. 绘制条目 ---
    draw_tasks = [_draw_challenge_bar(item) for item in challenge_list]
    bar_images = await asyncio.gather(*draw_tasks)

    # --- 3. 粘贴条目 ---
    y_offset = 140
    for bar_img in bar_images:
      base_img.paste(bar_img, (60, y_offset), bar_img)
      y_offset += 90

    # --- 4. 合成 ---
    bg.paste(base_img, (0, 0), base_img)
    bg = add_footer(bg)

    return bg

  except Exception as e:
    logger.error(f"绘制全息卡片失败 (uid: {user_info.get('uid')}): {e}")
    logger.exception(e)
    return None


# --- 3. 冥歌海墟 (Slash) ---

async def _draw_slash_bar(
    slash_item: Dict[str, Any]
) -> Image.Image:
  """(辅助函数) 绘制单个冥海条目"""
  base_img = Image.open(TEXT_PATH / "name_bg.png").convert("RGBA")
  draw = ImageDraw.Draw(base_img)

  # 绘制区域名
  draw.text(
      (60, 40), slash_item.get("name", "Unknown"),
      fill="white", font=WavesFonts.waves_font_24, anchor="lm"
  )

  # 绘制评级
  score_level = slash_item.get("scoreLevel", "C").upper()
  try:
    score_img = Image.open(TEXT_PATH / f"score_{score_level.lower()}.png").convert("RGBA")
    base_img.paste(score_img, (1100, 20), score_img)
  except FileNotFoundError:
    logger.warning(f"Missing score image for: score_{score_level.lower()}.png")

  # 绘制队伍
  team_list = slash_item.get("team", [])
  icon_tasks = [get_square_avatar(role.get("id")) for role in team_list[:3]]
  icon_images = await asyncio.gather(*icon_tasks)

  team_bg = Image.open(TEXT_PATH / "char_bg4.png").convert("RGBA")
  x_offset = 700
  for icon in icon_images:
    icon = icon.resize((60, 60))
    bar_img = team_bg.copy()
    bar_img.paste(icon, (10, 10), icon)
    base_img.paste(bar_img, (x_offset, 0), bar_img)
    x_offset += 90

  return base_img


async def draw_slash_card(
    user_info: Dict[str, Any],
    slash_data: Dict[str, Any],
    user_id: str
) -> Optional[Image.Image]:
  """
  绘制冥歌海墟卡片
  (迁移自 draw_slash_card.py)
  """
  try:
    slash_list = slash_data.get("slashList", [])
    if not slash_list:
      return None

    # --- 1. 初始化画布 ---
    card_h = 90 * len(slash_list) + 240
    bg = get_waves_bg(1300, card_h, "abyss_bg_3")
    base_img = Image.new("RGBA", bg.size, (0, 0, 0, 0))

    base_img = await _draw_header(base_img, user_info, user_id)

    # --- 2. 绘制条目 ---
    draw_tasks = [_draw_slash_bar(item) for item in slash_list]
    bar_images = await asyncio.gather(*draw_tasks)

    # --- 3. 粘贴条目 ---
    y_offset = 140
    for bar_img in bar_images:
      base_img.paste(bar_img, (60, y_offset), bar_img)
      y_offset += 90

    # --- 4. 合成 ---
    bg.paste(base_img, (0, 0), base_img)
    bg = add_footer(bg)

    return bg

  except Exception as e:
    logger.error(f"绘制冥海卡片失败 (uid: {user_info.get('uid')}): {e}")
    logger.exception(e)
    return None