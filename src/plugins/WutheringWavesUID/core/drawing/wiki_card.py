# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/core/drawing/wiki_card.py

import asyncio
from io import BytesIO
from pathlib import Path
from typing import Dict, Any, Optional, List

from PIL import Image, ImageDraw, ImageFont
from nonebot.log import logger

# --- 导入我们迁移的工具 ---
from ..utils.fonts import WavesFonts
from ..utils.image_helpers import (
  add_footer, get_waves_bg, get_square_avatar, get_square_weapon,
  get_attribute_prop, get_attribute, get_weapon_type,
  WAVES_SHUXING_MAP
)
from ..api.client import api_client

# --- 导入完成 ---


# --- 资源路径定义 ---
ASSETS_PATH = Path(__file__).parent.parent.parent / "assets"
# 适配修改：指向 assets/images/wiki/
TEXT_PATH = ASSETS_PATH / "images" / "wiki"


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


# --- 1. 角色图鉴 (Char Wiki) ---

async def draw_char_wiki_card(data: Dict[str, Any]) -> Optional[Image.Image]:
  """
  绘制角色图鉴卡
  (迁移自 draw_char.py)
  """
  try:
    bg = get_waves_bg(1000, 1000, "bg")  # 复用 bg.jpg
    base_img = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(base_img)

    # 角色立绘
    card_url = data.get("card", "")
    if card_url:
      role_pic = await _download_icon(card_url)
      if role_pic:
        role_pic = role_pic.resize((1000, 1000))
        base_img.paste(role_pic, (0, 0), role_pic)

    # 遮罩
    mask = Image.open(TEXT_PATH / "title_bg.png").convert("RGBA")
    base_img.paste(mask, (0, 0), mask)

    # 头像
    avatar_img = await get_square_avatar(data.get("id"))
    avatar_img = avatar_img.resize((100, 100))
    base_img.paste(avatar_img, (20, 20), avatar_img)

    # 标题
    draw.text(
        (140, 48), data.get("name", "Unknown"),
        fill="white", font=WavesFonts.waves_font_24
    )
    # 稀有度
    rarity = data.get("rarity", 4)
    rarity_img = Image.open(TEXT_PATH / f"rarity_{rarity}.png").convert("RGBA")
    base_img.paste(rarity_img, (140, 80), rarity_img)

    # 属性
    attr_name = data.get("attribute", "default")
    attr_icon = await get_attribute(attr_name)
    attr_icon = attr_icon.resize((40, 40))
    base_img.paste(attr_icon, (300, 80), attr_icon)

    # 武器类型
    weapon_type = data.get("weaponType", "default")
    weapon_icon = await get_weapon_type(weapon_type)
    weapon_icon = weapon_icon.resize((40, 40))
    base_img.paste(weapon_icon, (350, 80), weapon_icon)

    # 技能
    y_offset = 140
    skill_list = data.get("skill", [])
    icon_tasks = [_download_icon(s.get("icon", ""), (60, 60)) for s in skill_list]
    icon_images = await asyncio.gather(*icon_tasks)

    for skill, icon in zip(skill_list, icon_images):
      if icon:
        base_img.paste(icon, (30, y_offset), icon)
      draw.text(
          (100, y_offset), skill.get("name", ""),
          fill="white", font=WavesFonts.waves_font_22
      )
      draw.text(
          (100, y_offset + 30), skill.get("desc", ""),
          fill=(200, 200, 200), font=WavesFonts.waves_font_18
      )
      y_offset += 70

    # 共鸣链
    y_offset = 600
    chain_list = data.get("resonance", [])
    icon_tasks = [_download_icon(c.get("icon", ""), (50, 50)) for c in chain_list]
    icon_images = await asyncio.gather(*icon_tasks)

    for chain, icon in zip(chain_list, icon_images):
      mz_bg = Image.open(TEXT_PATH / "mz_bg.png").convert("RGBA")
      if icon:
        mz_bg.paste(icon, (10, 10), icon)
      base_img.paste(mz_bg, (30, y_offset), mz_bg)

      draw.text(
          (100, y_offset + 5), chain.get("name", ""),
          fill="white", font=WavesFonts.waves_font_22
      )
      draw.text(
          (100, y_offset + 35), chain.get("desc", ""),
          fill=(200, 200, 200), font=WavesFonts.waves_font_18
      )
      y_offset += 65

    # 合成
    bg.paste(base_img, (0, 0), base_img)
    bg = add_footer(bg)
    return bg

  except Exception as e:
    logger.error(f"绘制角色图鉴失败 (name: {data.get('name')}): {e}")
    logger.exception(e)
    return None


# --- 2. 武器图鉴 (Weapon Wiki) ---

async def draw_weapon_wiki_card(data: Dict[str, Any]) -> Optional[Image.Image]:
  """
  绘制武器图鉴卡
  (迁移自 draw_weapon.py)
  """
  try:
    bg = get_waves_bg(1000, 600, "bg")
    base_img = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(base_img)

    # 遮罩
    mask = Image.open(TEXT_PATH / "weapon_bg.png").convert("RGBA")
    base_img.paste(mask, (0, 0), mask)

    # 武器图标
    weapon_id = data.get("id")
    rarity = data.get("rarity", 3)
    weapon_bg = Image.open(TEXT_PATH / f"weapon_icon_bg_{rarity}.png")
    weapon_icon = await get_square_weapon(weapon_id)
    weapon_icon = weapon_icon.resize((100, 100))
    weapon_bg.paste(weapon_icon, (10, 10), weapon_icon)
    weapon_bg = weapon_bg.resize((120, 120))
    base_img.paste(weapon_bg, (30, 30), weapon_bg)

    # 标题
    draw.text(
        (170, 48), data.get("name", "Unknown"),
        fill="white", font=WavesFonts.waves_font_24
    )
    # 稀有度
    rarity_img = Image.open(TEXT_PATH / f"rarity_{rarity}.png").convert("RGBA")
    base_img.paste(rarity_img, (170, 80), rarity_img)

    # 武器类型
    weapon_type = data.get("type", "default")
    weapon_icon = await get_weapon_type(weapon_type)
    weapon_icon = weapon_icon.resize((40, 40))
    base_img.paste(weapon_icon, (330, 80), weapon_icon)

    # 属性
    y_offset = 170
    prop_icon = await get_attribute_prop(data.get("main", "default"))
    prop_icon = prop_icon.resize((38, 38))
    base_img.paste(prop_icon, (30, y_offset), prop_icon)
    draw.text(
        (80, y_offset + 5),
        f"主属性: {data.get('mainValue', 0)}",
        fill="white", font=WavesFonts.waves_font_22
    )

    y_offset += 50
    prop_icon = await get_attribute_prop(data.get("sub", "default"))
    prop_icon = prop_icon.resize((38, 38))
    base_img.paste(prop_icon, (30, y_offset), prop_icon)
    draw.text(
        (80, y_offset + 5),
        f"副属性: {data.get('subValue', 0)}",
        fill="white", font=WavesFonts.waves_font_22
    )

    # 技能
    y_offset = 280
    skill_list = data.get("skill", [])
    for skill in skill_list:
      draw.text(
          (40, y_offset), skill.get("desc", ""),
          fill=(200, 200, 200), font=WavesFonts.waves_font_18
      )
      y_offset += 25

    # 合成
    bg.paste(base_img, (0, 0), base_img)
    bg = add_footer(bg)
    return bg

  except Exception as e:
    logger.error(f"绘制武器图鉴失败 (name: {data.get('name')}): {e}")
    logger.exception(e)
    return None


# --- 3. 声骸图鉴 (Echo Wiki) ---

async def draw_echo_wiki_card(data: Dict[str, Any]) -> Optional[Image.Image]:
  """
  绘制声骸/套装图鉴卡
  (迁移自 draw_echo.py)
  """
  try:
    bg = get_waves_bg(1000, 600, "bg")
    base_img = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(base_img)

    # 遮罩
    mask = Image.open(TEXT_PATH / "weapon_bg.png").convert("RGBA")
    base_img.paste(mask, (0, 0), mask)

    name = data.get("name", "Unknown")

    # 标题
    draw.text(
        (40, 48), name,
        fill="white", font=WavesFonts.waves_font_24
    )

    if data.get("type") == "sonata":
      # 绘制套装
      y_offset = 100
      for item in data.get("ascensions", []):
        num = item.get('active_num')
        effect = item.get('effect')
        draw.text(
            (40, y_offset), f"[{num}件套]",
            fill=(255, 215, 0), font=WavesFonts.waves_font_22
        )
        draw.text(
            (140, y_offset), effect,
            fill="white", font=WavesFonts.waves_font_20
        )
        y_offset += 40

    elif data.get("type") == "echo":
      # 绘制单个声骸
      rarity = data.get("rarity", 4)
      rarity_img = Image.open(TEXT_PATH / f"rarity_{rarity}.png").convert("RGBA")
      base_img.paste(rarity_img, (40, 80), rarity_img)

      # 属性
      y_offset = 140
      draw.text(
          (40, y_offset), f"COST: {data.get('cost', 0)}",
          fill="white", font=WavesFonts.waves_font_22
      )
      y_offset += 40

      # 技能
      skill = data.get("skill", {})
      draw.text(
          (40, y_offset), skill.get("name", ""),
          fill=(255, 215, 0), font=WavesFonts.waves_font_22
      )
      y_offset += 30
      draw.text(
          (40, y_offset), skill.get("desc", ""),
          fill="white", font=WavesFonts.waves_font_20
      )

    # 合成
    bg.paste(base_img, (0, 0), base_img)
    bg = add_footer(bg)
    return bg

  except Exception as e:
    logger.error(f"绘制声骸图鉴失败 (name: {data.get('name')}): {e}")
    logger.exception(e)
    return None