# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/core/drawing/gacha_card.py

from pathlib import Path
from typing import Dict, Any, Optional, List

from PIL import Image, ImageDraw, ImageFont
from nonebot.log import logger

# --- 导入我们迁移的工具 ---
from ..utils.fonts import WavesFonts
from ..utils.image_helpers import add_footer, get_waves_bg
from ..utils.drawing_helpers import draw_pic  # 用于绘制头像

# --- 导入完成 ---


# --- 资源路径定义 ---
ASSETS_PATH = Path(__file__).parent.parent.parent / "assets"
# 适配修改：指向 assets/images/gachalog/
TEXT_PATH = ASSETS_PATH / "images" / "gachalog"


# --- 路径定义完成 ---


async def draw_gacha_card(
    summary: Dict[str, Any],
    user_id: str
) -> Optional[Image.Image]:
  """
  绘制抽卡记录统计图
  (迁移自 draw_gachalogs.py)
  :param summary: 来自 gacha_service.get_gacha_summary 的数据
  :param user_id: 平台用户ID (e.g., QQ号) 用于绘制头像
  """
  try:
    pools_data = summary.get("pools", [])
    if not pools_data:
      return None  # 没有数据

    # --- 1. 初始化画布 ---
    card_h = 300 * len(pools_data) + 240
    bg = get_waves_bg(1000, card_h, "bg")  # 复用 bg.jpg
    base_img = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(base_img)

    # 绘制标题栏
    title_bar = Image.open(TEXT_PATH / "title.png").convert("RGBA")
    base_img.paste(title_bar, (0, 0), title_bar)

    # --- 2. 绘制头部信息 ---
    # 绘制QQ头像
    avatar_img = await draw_pic(user_id)  # draw_pic 接收 qid
    if avatar_img:
      avatar_img = avatar_img.resize((100, 100))
      base_img.paste(avatar_img, (20, 20), avatar_img)

    # 绘制玩家信息
    draw.text(
        (140, 48), f"UID: {summary.get('uid', '...-...')}",
        fill="white", font=WavesFonts.waves_font_24
    )
    draw.text(
        (140, 84), f"总抽数: {summary.get('total', 0)}",
        fill="white", font=WavesFonts.waves_font_22
    )

    # --- 3. 绘制卡池条目 ---
    y_offset = 140
    for pool in pools_data:
      pool_bg = Image.open(TEXT_PATH / "info_block.png").convert("RGBA")
      p_draw = ImageDraw.Draw(pool_bg)

      # 卡池名
      p_draw.text(
          (40, 30), pool.get("name", "Unknown"),
          fill="white", font=WavesFonts.waves_font_24
      )
      # 总抽数
      p_draw.text(
          (40, 70), f"总抽数: {pool.get('total', 0)}",
          fill=(200, 200, 200), font=WavesFonts.waves_font_20
      )

      # 5星
      star_5_count = pool.get('star_5_count', 0)
      star_5_rate = (star_5_count / pool.get('total', 1) * 100)
      p_draw.text(
          (200, 70), f"5星: {star_5_count} ({star_5_rate:.1f}%)",
          fill=(255, 215, 0), font=WavesFonts.waves_font_20
      )

      # 4星
      star_4_count = pool.get('star_4_count', 0)
      star_4_rate = (star_4_count / pool.get('total', 1) * 100)
      p_draw.text(
          (450, 70), f"4星: {star_4_count} ({star_4_rate:.1f}%)",
          fill=(180, 120, 255), font=WavesFonts.waves_font_20
      )

      # 5星平均
      p_draw.text(
          (650, 70), f"5星平均: {pool.get('avg_5_pity', 0.0)}",
          fill=(200, 200, 200), font=WavesFonts.waves_font_20
      )

      # 5星保底
      pity_5 = pool.get('pity_5', 0)
      pity_text = f"当前 {pity_5} 抽未出5星"
      # 进度条
      bar_bg = Image.open(TEXT_PATH / "bar.png").convert("RGBA")
      pity_bar_w = int(380 * (pity_5 / 80))  # 假设80保底
      if pity_bar_w > 0:
        pity_bar = Image.new("RGBA", (pity_bar_w, 20), (255, 215, 0))
        bar_bg.paste(pity_bar, (5, 5), pity_bar)
      pool_bg.paste(bar_bg, (40, 100), bar_bg)
      p_draw.text(
          (430, 115), pity_text,
          fill="white", font=WavesFonts.waves_font_18, anchor="lm"
      )

      # 5星列表
      star_5_list = pool.get("star_5_list", [])
      y_list_offset = 140
      for item in star_5_list[-5:]:  # 最多显示最近5个
        p_draw.text(
            (60, y_list_offset), f"[{item.get('pity')}抽] {item.get('name')}",
            fill=(255, 215, 0), font=WavesFonts.waves_font_20
        )
        y_list_offset += 28

      base_img.paste(pool_bg, (40, y_offset), pool_bg)
      y_offset += 300

    # --- 4. 合成 ---
    bg.paste(base_img, (0, 0), base_img)
    bg = add_footer(bg)

    return bg

  except Exception as e:
    logger.error(f"绘制抽卡卡片失败 (uid: {summary.get('uid')}): {e}")
    logger.exception(e)
    return None