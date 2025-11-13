# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/core/drawing/echo_list_card.py

import asyncio
from io import BytesIO
from pathlib import Path
from typing import Dict, Any, List, Optional

from PIL import Image, ImageDraw, ImageFont
from nonebot.log import logger

# --- 导入我们迁移的工具 ---
from ..utils.fonts import WavesFonts
from ..utils.image_helpers import (
  get_waves_bg, add_footer, get_attribute_prop, WAVES_ECHO_MAP
)
from ..utils.drawing_helpers import draw_pic  # 用于绘制头像
from ..utils.scoring import get_score_level
from ..api.client import api_client

# --- 导入完成 ---


# --- 资源路径定义 ---
ASSETS_PATH = Path(__file__).parent.parent.parent / "assets"
# 适配修改：指向 assets/images/echo/
TEXT_PATH = ASSETS_PATH / "images" / "echo"


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


async def _draw_echo_bar(echo: Dict[str, Any], recommend_attrs: List[str]) -> Image.Image:
  """
  (辅助函数) 绘制单个声骸条目
  (迁移自 draw_echo_list.py)
  """
  base_img = Image.open(TEXT_PATH / "sh_bg.png").convert("RGBA")
  draw = ImageDraw.Draw(base_img)

  # 绘制 COST
  cost = echo.get("cost", 0)
  cost_color = WAVES_ECHO_MAP.get(echo.get("sonataName", ""), (255, 255, 255))
  draw.text(
      (28, 28), f"COST {cost}", fill=cost_color,
      font=WavesFonts.arial_bold_font_18
  )

  # 绘制声骸图标
  icon = await _download_icon(echo.get("icon", ""), (100, 100))
  if icon:
    base_img.paste(icon, (12, 54), icon)

  # 绘制声骸名称和等级
  draw.text(
      (118, 54), echo.get("name", "Unknown"), fill="white",
      font=WavesFonts.waves_font_24
  )
  draw.text(
      (118, 88), f"Lv.{echo.get('level', 0)}", fill=(160, 160, 160),
      font=WavesFonts.waves_font_20
  )

  # 绘制主词条
  main_entry = echo.get("mainEntry", {})
  main_name = main_entry.get("name", "Unknown")
  main_value = main_entry.get("value", 0.0)
  main_prop_icon = await get_attribute_prop(main_name)
  if main_prop_icon:
    main_prop_icon = main_prop_icon.resize((38, 38))
    base_img.paste(main_prop_icon, (24, 168), main_prop_icon)
  draw.text(
      (70, 178), f"{main_name} {main_value:.1f}%", fill="white",
      font=WavesFonts.waves_font_22
  )

  # 绘制副词条
  sub_entries = echo.get("subEntry", [])
  for j, sub in enumerate(sub_entries):
    sub_name = sub.get("key", "Unknown")
    sub_value = sub.get("value", 0.0)

    # 判断是否为推荐词条
    fill = (244, 191, 11) if sub_name in recommend_attrs else "white"

    val_str = f"{sub_value:.1f}%" if "%" in sub.get("unit", "") else str(int(sub_value))

    draw.text(
        (30, 222 + j * 24), f"· {sub_name} +{val_str}",
        fill=fill, font=WavesFonts.waves_font_18
    )

  # 绘制分数
  score = echo.get("score", 0.0)
  level = get_score_level(score)

  # 评级图片
  score_level_img = Image.open(TEXT_PATH / f"sh_title_{level.lower()}.png")
  base_img.paste(score_level_img, (154, 86), score_level_img)

  # 绘制具体分数
  draw.text(
      (204, 91), str(score), fill="white",
      font=WavesFonts.arial_bold_font_18, anchor="lt"
  )

  return base_img


async def draw_echo_list_card(data: Dict[str, Any], user_id: str) -> Optional[Image.Image]:
  """
  绘制角色声骸列表图
  (迁移自 draw_echo_list.py)
  :param data: 来自 character_service.get_character_panel_data 的数据
  :param user_id: 平台用户ID (e.g., QQ号) 用于绘制头像
  """
  try:
    echo_list = data.get("echoList", [])
    if not echo_list:
      return None

    # 按 COST 排序
    echo_list.sort(key=lambda x: x.get("cost", 0), reverse=True)

    recommend_attrs = data.get("recommendAttrs", [])

    # --- 1. 初始化画布 ---
    bg = get_waves_bg(1000, 1000)
    base_img = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(base_img)

    # 绘制标题栏
    title_bar = Image.open(TEXT_PATH / "title_bar.png").convert("RGBA")
    base_img.paste(title_bar, (0, 0), title_bar)

    # 绘制QQ头像
    avatar_img = await draw_pic(user_id)  # draw_pic 接收 qid
    if avatar_img:
      avatar_img = avatar_img.resize((100, 100))
      base_img.paste(avatar_img, (20, 20), avatar_img)

    # 绘制玩家信息 (显示的是角色名)
    draw.text(
        (140, 48), data.get("name", "Unknown"),
        fill="white", font=WavesFonts.waves_font_24
    )
    draw.text(
        (140, 84), f"UID: {data.get('uid', '...-...')}",
        fill="white", font=WavesFonts.waves_font_22
    )

    # 绘制声骸总分
    total_score = data.get("totalEchoScore", 0.0)
    score_level = get_score_level(total_score)
    score_level_img = Image.open(TEXT_PATH / f"sh_title_{score_level.lower()}.png")
    base_img.paste(score_level_img, (680, 78), score_level_img)
    draw.text(
        (740, 84), f"总分: {total_score:.1f}",
        fill="white", font=WavesFonts.waves_font_24, anchor="lm"
    )

    # --- 2. 绘制声骸条目 ---
    draw_tasks = []
    for echo in echo_list:
      draw_tasks.append(_draw_echo_bar(echo, recommend_attrs))

    echo_bar_images = await asyncio.gather(*draw_tasks)

    # --- 3. 粘贴条目 ---
    x_list = [24, 362, 700]
    y_list = [140, 480]

    idx = 0
    for y in y_list:
      for x in x_list:
        if idx < len(echo_bar_images):
          bar_img = echo_bar_images[idx]
          # 调整大小以适应 3x2 布局
          bar_img = bar_img.resize((276, 320), Image.Resampling.LANCZOS)
          base_img.paste(bar_img, (x, y), bar_img)
          idx += 1
        if idx >= 5:  # 角色最多装备5个
          break
      if idx >= 5:
        break

    # --- 4. 合成最终图像 ---
    bg.paste(base_img, (0, 0), base_img)
    bg = add_footer(bg)

    # 裁剪到合适的高度
    bg = bg.crop((0, 0, 1000, 840))

    return bg

  except Exception as e:
    logger.error(f"绘制声骸列表失败 (uid: {data.get('uid')}): {e}")
    logger.exception(e)
    return None