# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/core/drawing/character_list_card.py

import asyncio
from io import BytesIO
from pathlib import Path
from typing import Dict, Any, List, Optional

from PIL import Image, ImageDraw, ImageFont
from nonebot.log import logger

# --- 导入我们迁移的工具 ---
from ..utils.fonts import WavesFonts
from ..utils.image_helpers import (
  get_waves_bg, get_square_avatar, get_square_weapon, add_footer
)
from ..utils.drawing_helpers import draw_pic
from ..utils.scoring import get_score_level
from ..api.client import api_client

# --- 导入完成 ---


# --- 资源路径定义 ---
ASSETS_PATH = Path(__file__).parent.parent.parent / "assets"
# 适配修改：指向 assets/images/charlist/
TEXT_PATH = ASSETS_PATH / "images" / "charlist"


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


async def _draw_role_bar(
    role_data: Dict[str, Any],
    total_score: float
) -> Image.Image:
  """
  (辅助函数) 绘制单个角色条目
  (迁移自 draw_char_list.py)
  """
  rarity = role_data.get("rarity", 4)
  bar_img = Image.open(TEXT_PATH / f"bar_{rarity}star.png").convert("RGBA")
  base_img = Image.new("RGBA", bar_img.size, (0, 0, 0, 0))
  base_img.paste(bar_img, (0, 0), bar_img)
  draw = ImageDraw.Draw(base_img)

  # 绘制头像
  avatar_img = await get_square_avatar(role_data.get("id"))
  avatar_img = avatar_img.resize((100, 100))
  base_img.paste(avatar_img, (20, 20), avatar_img)

  # 绘制名称, 等级
  draw.text(
      (136, 40), str(role_data.get("name")),
      fill="white", font=WavesFonts.waves_font_24
  )
  draw.text(
      (136, 80), f"Lv.{role_data.get('level')}",
      fill="white", font=WavesFonts.waves_font_22
  )

  # 绘制共鸣链
  chain_icon = Image.open(TEXT_PATH / "promote_icon.png").convert("RGBA")
  chain_icon = chain_icon.resize((24, 24))
  base_img.paste(chain_icon, (220, 80), chain_icon)
  draw.text(
      (250, 80), str(role_data.get("resonanceLevel", 0)),
      fill="white", font=WavesFonts.waves_font_22
  )

  # 绘制武器
  weapon = role_data.get("weapon", {})
  weapon_rarity = weapon.get("rarity", 3)
  weapon_bg = Image.open(TEXT_PATH / f"weapon_icon_bg_{weapon_rarity}.png")
  weapon_icon = await get_square_weapon(weapon.get("id", 0))
  weapon_icon = weapon_icon.resize((68, 68))
  weapon_bg.paste(weapon_icon, (6, 6), weapon_icon)
  weapon_bg = weapon_bg.resize((80, 80))
  base_img.paste(weapon_bg, (300, 30), weapon_bg)
  draw.text(
      (390, 48), f"Lv.{weapon.get('level', 1)}",
      fill="white", font=WavesFonts.waves_font_20
  )
  draw.text(
      (390, 80), f"R{weapon.get('resonanceLevel', 1)}",
      fill="white", font=WavesFonts.waves_font_20
  )

  # 绘制技能
  skill_bg = Image.open(TEXT_PATH / "skill_bg.png").convert("RGBA")
  skill_list = role_data.get("skillList", [])

  icon_tasks = [_download_icon(s.get("icon", "")) for s in skill_list[:5]]  # 最多5个
  icon_images = await asyncio.gather(*icon_tasks)

  x_offset = 510
  for i, (skill, icon) in enumerate(zip(skill_list, icon_images)):
    if i >= 5:
      break
    s_bg = skill_bg.copy()
    if icon:
      icon = icon.resize((48, 48))
      s_bg.paste(icon, (6, 6), icon)

    draw_s = ImageDraw.Draw(s_bg)
    draw_s.text(
        (30, 64), f"Lv.{skill.get('level', 1)}",
        fill="white", font=WavesFonts.waves_font_14, anchor="mm"
    )
    base_img.paste(s_bg, (x_offset, 35), s_bg)
    x_offset += 100

  # 绘制声骸总分
  score_level = get_score_level(total_score)
  score_img = Image.open(TEXT_PATH / f"score_{score_level}.png").convert("RGBA")
  base_img.paste(score_img, (1030, 50), score_img)
  draw.text(
      (1090, 68), f"{total_score:.1f}",
      fill="white", font=WavesFonts.arial_bold_font_30, anchor="lm"
  )

  return base_img


async def draw_character_list_card(data: Dict[str, Any], user_id: str) -> Optional[Image.Image]:
  """
  绘制角色列表图
  (迁移自 draw_char_list.py)
  """
  try:
    role_list = data.get("roleList", [])
    if not role_list:
      return None

    # 按等级排序
    role_list.sort(key=lambda x: x.get("level", 0), reverse=True)

    # --- 1. 初始化画布 ---
    card_h = 140 * len(role_list) + 240
    bg = get_waves_bg(1280, card_h)
    base_img = Image.new("RGBA", (1280, card_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(base_img)

    # 绘制标题栏
    title_bar = Image.open(TEXT_PATH / "title_bar.png").convert("RGBA")
    base_img.paste(title_bar, (0, 0), title_bar)

    # 绘制QQ头像
    avatar_img = await draw_pic(user_id)  # draw_pic 接收 qid
    if avatar_img:
      avatar_img = avatar_img.resize((100, 100))
      base_img.paste(avatar_img, (20, 20), avatar_img)

    # 绘制玩家信息
    draw.text(
        (140, 48), data.get("name", "Unknown"),
        fill="white", font=WavesFonts.waves_font_24
    )
    draw.text(
        (140, 84), f"UID: {data.get('uid', '...-...')}",
        fill="white", font=WavesFonts.waves_font_22
    )
    draw.text(
        (960, 84), f"总声骸得分: {data.get('totalAccountScore', 0.0):.1f}",
        fill="white", font=WavesFonts.waves_font_24, anchor="rm"
    )

    # --- 2. 绘制角色条目 ---
    draw_tasks = []
    for role in role_list:
      draw_tasks.append(_draw_role_bar(role, role.get("totalEchoScore", 0.0)))

    role_bar_images = await asyncio.gather(*draw_tasks)

    # --- 3. 粘贴条目 ---
    y_offset = 140
    for bar_img in role_bar_images:
      base_img.paste(bar_img, (40, y_offset), bar_img)
      y_offset += 140

    # --- 4. 合成最终图像 ---
    bg.paste(base_img, (0, 0), base_img)
    bg = add_footer(bg)

    return bg

  except Exception as e:
    logger.error(f"绘制角色列表失败 (uid: {data.get('uid')}): {e}")
    logger.exception(e)
    return None