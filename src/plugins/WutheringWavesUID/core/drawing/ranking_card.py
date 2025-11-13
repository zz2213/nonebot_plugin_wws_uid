# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/core/drawing/ranking_card.py

import asyncio
from io import BytesIO
from pathlib import Path
from typing import Dict, Any, List, Optional

from PIL import Image, ImageDraw, ImageFont
from nonebot.log import logger  # 替换 gsuid_core logger

# --- 导入我们迁移的工具 ---
from ..utils.fonts import WavesFonts
from ..utils.image_helpers import (
  get_waves_bg, get_square_avatar, get_square_weapon,
  get_role_pile_old, add_footer
)
from ..utils.drawing_helpers import draw_pic
from ..utils.scoring import get_score_level
from ..api.client import api_client  # 替换 gsuid_core sget

# --- 导入 API 模型 ---
from ..api.ranking_api import RankInfoData, RankDetail, TotalRankInfoData, TotalRankDetail

# --- 资源路径定义 ---
ASSETS_PATH = Path(__file__).parent.parent.parent / "assets"
# 适配修改：指向 assets/images/rank/
TEXT_PATH = ASSETS_PATH / "images" / "rank"


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


async def _draw_rank_info(
    img: Image.Image,
    detail: RankDetail
) -> Image.Image:
  """
  (辅助函数) 绘制单个角色排行条目
  (迁移自 darw_rank_card.py)
  """
  base_img = Image.new("RGBA", (1580, 168), (0, 0, 0, 0))
  bar_img = Image.open(TEXT_PATH / "bar1.png").convert("RGBA")
  base_img.paste(bar_img, (0, 0), bar_img)
  draw = ImageDraw.Draw(base_img)

  # 排名
  rank = detail.rank
  color = "white"
  if rank == 1:
    color = (255, 108, 108)
  elif rank == 2:
    color = (255, 165, 79)
  elif rank == 3:
    color = (255, 215, 0)

  draw.text((64, 84), str(rank), fill=color, font=WavesFonts.waves_font_30, anchor="mm")

  # 绘制头像
  avatar_img = await get_square_avatar(detail.char_id)
  avatar_img = avatar_img.resize((100, 100))
  base_img.paste(avatar_img, (110, 34), avatar_img)

  # 绘制昵称、UID、伤害
  draw.text((230, 48), str(detail.alias_name), fill="white", font=WavesFonts.waves_font_24)
  draw.text((230, 88), f"UID: {detail.waves_id}", fill="white", font=WavesFonts.waves_font_24)

  draw.text(
      (550, 84), f"{detail.expected_damage:.0f}", fill="white",
      font=WavesFonts.arial_bold_font_30, anchor="mm"
  )

  # 绘制武器
  weapon_bg = Image.open(TEXT_PATH / "weapon_icon_bg_5.png").convert("RGBA")
  weapon_img = await get_square_weapon(detail.weapon_id)
  weapon_img = weapon_img.resize((68, 68))
  weapon_bg.paste(weapon_img, (6, 6), weapon_img)
  weapon_bg = weapon_bg.resize((80, 80))
  base_img.paste(weapon_bg, (730, 44), weapon_bg)
  draw.text(
      (820, 84), f"Lv.{detail.weapon_level} (R{detail.weapon_reson_level})",
      fill="white", font=WavesFonts.waves_font_24, anchor="lm"
  )

  # 绘制声骸套装
  draw.text(
      (1040, 84), detail.sonata_name, fill="white",
      font=WavesFonts.waves_font_24, anchor="lm"
  )

  # 绘制声骸得分
  score_level_img = Image.open(TEXT_PATH / f"score_{detail.phantom_score_bg}.png")
  base_img.paste(score_level_img, (1340, 68), score_level_img)
  draw.text(
      (1400, 84), f"{detail.phantom_score:.0f}", fill="white",
      font=WavesFonts.arial_bold_font_30, anchor="lm"
  )

  img.paste(base_img, (30, 200 + (rank - 1) * 178), base_img)
  return img


async def draw_ranking_card(
    data: RankInfoData,
    char_id: int
) -> Optional[Image.Image]:
  """
  绘制角色伤害排行榜
  (迁移自 darw_rank_card.py)
  """
  try:
    bg = get_waves_bg(1640, 2000, "totalrank")  # 复用 totalrank 背景

    # 尝试获取角色立绘
    try:
      role_pic = await get_role_pile_old(char_id, custom=True)
      role_pic = role_pic.resize((int(role_pic.width * 1.2), int(role_pic.height * 1.2)))
      bg.paste(role_pic, (700, 200), role_pic)
    except Exception:
      pass  # 获取失败也无妨

    title_img = Image.open(TEXT_PATH / "title.png").convert("RGBA")
    bg.paste(title_img, (0, 0), title_img)

    # 绘制条目
    for detail in data.details:
      bg = await _draw_rank_info(bg, detail)

    bg = add_footer(bg)
    return bg.resize((820, 1000), Image.Resampling.LANCZOS)

  except Exception as e:
    logger.error(f"绘制角色排行失败 (char_id: {char_id}): {e}")
    logger.exception(e)
    return None


async def _draw_total_rank_info(
    img: Image.Image,
    detail: TotalRankDetail
) -> Image.Image:
  """
  (辅助函数) 绘制单个总分排行条目
  (迁移自 draw_total_rank_card.py)
  """
  base_img = Image.new("RGBA", (1580, 168), (0, 0, 0, 0))
  bar_img = Image.open(TEXT_PATH / "bar.png").convert("RGBA")
  base_img.paste(bar_img, (0, 0), bar_img)
  draw = ImageDraw.Draw(base_img)

  # 排名
  rank = detail.rank
  color = "white"
  if rank == 1:
    color = (255, 108, 108)
  elif rank == 2:
    color = (255, 165, 79)
  elif rank == 3:
    color = (255, 215, 0)

  draw.text((64, 84), str(rank), fill=color, font=WavesFonts.waves_font_30, anchor="mm")

  # 绘制QQ头像
  avatar_img = await draw_pic(detail.user_id)  # draw_pic 接收 qid
  if avatar_img:
    avatar_img = avatar_img.resize((100, 100))
    base_img.paste(avatar_img, (110, 34), avatar_img)

  # 绘制昵称、UID
  draw.text((230, 48), str(detail.alias_name), fill="white", font=WavesFonts.waves_font_24)
  draw.text((230, 88), f"UID: {detail.waves_id}", fill="white", font=WavesFonts.waves_font_24)

  # 绘制总分
  draw.text(
      (550, 84), f"{detail.total_score:.0f}", fill="white",
      font=WavesFonts.arial_bold_font_30, anchor="mm"
  )

  # 绘制角色分数详情
  char_details = sorted(detail.char_score_details, key=lambda x: x.phantom_score, reverse=True)

  icon_tasks = []
  for i, char in enumerate(char_details):
    if i >= 6:  # 最多显示6个
      break
    icon_tasks.append(get_square_avatar(char.char_id))

  icon_images = await asyncio.gather(*icon_tasks)

  x_offset = 730
  for i, (char, icon) in enumerate(zip(char_details, icon_images)):
    if i >= 6:
      break

    icon = icon.resize((80, 80))
    base_img.paste(icon, (x_offset, 44), icon)

    # 绘制分数
    score_level = get_score_level(char.phantom_score)
    score_img = Image.open(TEXT_PATH / f"score_{score_level}.png")
    base_img.paste(score_img, (x_offset + 80, 50), score_img)
    draw.text(
        (x_offset + 106, 68), f"{char.phantom_score:.0f}", fill="white",
        font=WavesFonts.arial_bold_font_18, anchor="lm"
    )
    x_offset += 140

  img.paste(base_img, (30, 200 + (rank - 1) * 178), base_img)
  return img


async def draw_total_ranking_card(data: TotalRankInfoData) -> Optional[Image.Image]:
  """
  绘制总分排行榜
  (迁移自 draw_total_rank_card.py)
  """
  try:
    bg = get_waves_bg(1640, 2000, "totalrank")
    title_img = Image.open(TEXT_PATH / "title2.png").convert("RGBA")
    bg.paste(title_img, (0, 0), title_img)

    # 绘制条目
    for detail in data.score_details:
      bg = await _draw_total_rank_info(bg, detail)

    bg = add_footer(bg)
    return bg.resize((820, 1000), Image.Resampling.LANCZOS)

  except Exception as e:
    logger.error(f"绘制总分排行失败: {e}")
    logger.exception(e)
    return None