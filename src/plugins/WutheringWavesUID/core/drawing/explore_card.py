# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/core/drawing/explore_card.py

from pathlib import Path
from typing import Dict, Any, Optional, List

from PIL import Image, ImageDraw, ImageFont
from nonebot.log import logger

# --- 导入我们迁移的工具 ---
from ..utils.fonts import WavesFonts
from ..utils.image_helpers import add_footer, get_waves_bg, crop_center_img
from ..utils.drawing_helpers import draw_pic  # 用于绘制头像

# --- 导入完成 ---


# --- 资源路径定义 ---
ASSETS_PATH = Path(__file__).parent.parent.parent / "assets"
# 适配修改：指向 assets/images/explore/
TEXT_PATH = ASSETS_PATH / "images" / "explore"


# --- 路径定义完成 ---


async def _draw_explore_bar(
    explore_item: Dict[str, Any]
) -> Image.Image:
  """
  (辅助函数) 绘制单个探索度条目
  (迁移自 draw_explore_card.py)
  """
  base_img = Image.new("RGBA", (580, 80), (0, 0, 0, 0))
  draw = ImageDraw.Draw(base_img)

  # 底条
  bar_bg = Image.open(TEXT_PATH / "explore_frame.png").convert("RGBA")
  base_img.paste(bar_bg, (0, 0), bar_bg)

  # 进度条
  explore_bar = Image.open(TEXT_PATH / "explore_bar.png").convert("RGBA")
  percent = explore_item.get("percent", 0.0) / 100.0
  bar_width = int(570 * percent)
  if bar_width > 0:
    explore_bar = explore_bar.crop((0, 0, bar_width, explore_bar.height))
    base_img.paste(explore_bar, (5, 5), explore_bar)

  # 区域名
  draw.text(
      (30, 40), explore_item.get("name", "Unknown"),
      fill="white", font=WavesFonts.waves_font_24, anchor="lm"
  )
  # 百分比
  draw.text(
      (550, 40), f"{percent * 100:.0f}%",
      fill="white", font=WavesFonts.arial_bold_font_24, anchor="rm"
  )

  # 100% 标签
  if percent >= 1.0:
    tag = Image.open(TEXT_PATH / "tag_yes.png").convert("RGBA")
  else:
    tag = Image.open(TEXT_PATH / "tag_no.png").convert("RGBA")

  base_img.paste(tag, (440, 20), tag)

  return base_img


async def draw_explore_card(
    user_info: Dict[str, Any],
    explore_data: Dict[str, Any],
    user_id: str
) -> Optional[Image.Image]:
  """
  绘制探索度卡片
  (迁移自 draw_explore_card.py)
  :param user_info: 来自 game_service.get_user_info 的数据
  :param explore_data: 来自 game_service.get_explore_info 的数据
  :param user_id: 平台用户ID (e.g., QQ号) 用于绘制头像
  """
  try:
    explore_list: List[Dict] = explore_data.get("exploreList", [])
    if not explore_list:
      return None

    # --- 1. 初始化画布 ---
    card_h = 90 * len(explore_list) + 240
    bg = get_waves_bg(800, card_h, "bg")  # 复用 bg.jpg
    base_img = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(base_img)

    title_bar = Image.open(TEXT_PATH / "title_bar.png").convert("RGBA")
    base_img.paste(title_bar, (0, 0), title_bar)

    # --- 2. 绘制头部信息 ---
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

    # 绘制总探索度
    title_icon = Image.open(TEXT_PATH / "explore_title.png").convert("RGBA")
    base_img.paste(title_icon, (500, 70), title_icon)
    total_percent = explore_data.get("totalPercent", 0.0)
    draw.text(
        (760, 84), f"{total_percent:.1f}%",
        fill="white", font=WavesFonts.arial_bold_font_30, anchor="rm"
    )

    # --- 3. 绘制探索度条目 ---
    draw_tasks = []
    for item in explore_list:
      draw_tasks.append(_draw_explore_bar(item))

    explore_bar_images = await asyncio.gather(*draw_tasks)

    # --- 4. 粘贴条目 ---
    y_offset = 140
    for bar_img in explore_bar_images:
      base_img.paste(bar_img, (110, y_offset), bar_img)
      y_offset += 90

    # --- 5. 合成 ---
    bg.paste(base_img, (0, 0), base_img)
    bg = add_footer(bg)

    return bg

  except Exception as e:
    logger.error(f"绘制探索度卡片失败 (uid: {user_info.get('uid')}): {e}")
    logger.exception(e)
    return None