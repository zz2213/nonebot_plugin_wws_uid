# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/core/drawing/stamina_card.py

import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from PIL import Image, ImageDraw, ImageFont
from nonebot.log import logger  # 替换 gsuid_core logger

# --- 导入我们迁移的工具 ---
from ..utils.fonts import WavesFonts
from ..utils.image_helpers import add_footer, get_waves_bg
from ..utils.drawing_helpers import draw_pic  # 用于绘制头像

# --- 导入完成 ---


# --- 资源路径定义 ---
ASSETS_PATH = Path(__file__).parent.parent.parent / "assets"
# 适配修改：指向 assets/images/stamina/
TEXT_PATH = ASSETS_PATH / "images" / "stamina"


# --- 路径定义完成 ---


def _format_time(seconds: int) -> str:
  """将秒格式化为 00:00:00"""
  if seconds <= 0:
    return "00:00:00"
  m, s = divmod(seconds, 60)
  h, m = divmod(m, 60)
  return f"{h:02d}:{m:02d}:{s:02d}"


async def draw_stamina_card(
    user_info: Dict[str, Any],
    stats_data: Dict[str, Any],
    user_id: str
) -> Optional[Image.Image]:
  """
  绘制体力卡片
  (迁移自 draw_waves_stamina.py)
  :param user_info: 来自 game_service.get_user_info 的数据
  :param stats_data: 来自 game_service.get_game_stats 的数据
  :param user_id: 平台用户ID (e.g., QQ号) 用于绘制头像
  """
  try:
    # --- 1. 数据提取 ---
    stamina_info = stats_data.get("staminaInfo", {})
    cur_stamina = stamina_info.get("stamina", 0)
    max_stamina = stamina_info.get("maxStamina", 240)

    # 计算恢复时间
    recover_time_str = stamina_info.get("staminaRecoverTime", "0")
    recover_time_int = int(recover_time_str)

    full_time_str = "已回满"
    if cur_stamina < max_stamina and recover_time_int > 0:
      # recover_time_int 是时间戳 (秒)
      now = int(time.time())
      remaining_seconds = recover_time_int - now
      if remaining_seconds > 0:
        full_time_str = f"{_format_time(remaining_seconds)} 后回满"
      else:
        full_time_str = "已回满"  # 理论上已回满，但数据未刷新
        cur_stamina = max_stamina  # 手动校准

    # TODO: 体力阈值推送 (原 config.stamina_threshold) 暂不实现
    # is_full_tip = cur_stamina >= 200 # 假设阈值为 200

    # --- 2. 初始化画布 ---
    bg = get_waves_bg(1000, 300, "bg")  # 复用 bg.jpg
    base_img = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(base_img)

    title_bar = Image.open(TEXT_PATH / "title_bar.png").convert("RGBA")
    base_img.paste(title_bar, (0, 0), title_bar)

    # --- 3. 绘制头部信息 ---
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

    # --- 4. 绘制体力条 ---
    bar_down = Image.open(TEXT_PATH / "bar_down.png").convert("RGBA")
    main_bar = Image.open(TEXT_PATH / "main_bar.png").convert("RGBA")
    base_img.paste(bar_down, (60, 160), bar_down)

    # 计算体力条长度
    bar_width = int(880 * (cur_stamina / max_stamina))
    if bar_width > 0:
      main_bar = main_bar.crop((0, 0, bar_width, main_bar.height))
      base_img.paste(main_bar, (60, 160), main_bar)

    # 绘制体力文字
    draw.text(
        (500, 185), f"{cur_stamina} / {max_stamina}",
        fill="white", font=WavesFonts.waves_font_30, anchor="mm"
    )

    # 绘制恢复时间
    draw.text(
        (500, 230), full_time_str,
        fill="white", font=WavesFonts.waves_font_24, anchor="mm"
    )

    # --- 5. 绘制推送状态 (TODO) ---
    # 暂时写死为 "否"
    # yes = Image.open(TEXT_PATH / "yes.png").convert("RGBA")
    no = Image.open(TEXT_PATH / "no.png").convert("RGBA")
    draw.text(
        (820, 84), "体力推送:",
        fill="white", font=WavesFonts.waves_font_22
    )
    base_img.paste(no, (910, 80), no)

    # --- 6. 合成 ---
    bg.paste(base_img, (0, 0), base_img)
    bg = add_footer(bg)

    return bg

  except Exception as e:
    logger.error(f"绘制体力卡片失败 (uid: {user_info.get('uid')}): {e}")
    logger.exception(e)
    return None