# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/core/drawing/calendar_card.py

import asyncio
from io import BytesIO
from pathlib import Path
from typing import Dict, Any, Optional, List

from PIL import Image, ImageDraw, ImageFont
from nonebot.log import logger

# --- 导入我们迁移的工具 ---
from ..utils.fonts import WavesFonts
from ..utils.image_helpers import (
    add_footer, get_waves_bg, get_square_avatar, get_square_weapon, crop_center_img
)
from ..api.client import api_client
# 导入 WikiService 以使用其 ID->Name 映射
from ...services.wiki_service import wiki_service
# 导入数据模型
from ...services.calendar_service import CalendarData
from ..api.ranking_api import PoolData

# --- 导入完成 ---


# --- 资源路径定义 ---
ASSETS_PATH = Path(__file__).parent.parent.parent / "assets"
# 适配修改：指向 assets/images/calendar/
TEXT_PATH = ASSETS_PATH / "images" / "calendar"


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


async def _draw_develop(
        base_img: Image.Image,
        data: CalendarData,
        id_name_map: Dict[str, str]
):
    """(辅助函数) 绘制每日材料"""
    draw = ImageDraw.Draw(base_img)
    y_offset = 120

    # --- 角色材料 ---
    base_img.paste(Image.open(TEXT_PATH / "char_icon.png"), (60, y_offset), Image.open(TEXT_PATH / "char_icon.png"))
    char_list = data.develop.char

    tasks = [get_square_avatar(i) for i in char_list]  # TODO: 应该是材料图标
    icons = await asyncio.gather(*tasks)

    x_offset = 110
    for i, (icon, char_id) in enumerate(zip(icons, char_list)):
        if i >= 4: break
        char_name = id_name_map.get(str(char_id), f"ID:{char_id}")

        icon = icon.resize((60, 60))
        bar = Image.open(TEXT_PATH / "char_bar.png")
        draw_bar = ImageDraw.Draw(bar)
        bar.paste(icon, (10, 10), icon)
        draw_bar.text(
            (80, 40), char_name, fill="white",
            font=WavesFonts.waves_font_18, anchor="lm"
        )
        base_img.paste(bar, (x_offset, y_offset), bar)
        x_offset += 210

    y_offset += 90

    # --- 武器材料 ---
    base_img.paste(Image.open(TEXT_PATH / "weapon_icon.png"), (60, y_offset), Image.open(TEXT_PATH / "weapon_icon.png"))
    weapon_list = data.develop.weapon

    tasks = [get_square_weapon(i) for i in weapon_list]  # TODO: 应该是材料图标
    icons = await asyncio.gather(*tasks)

    x_offset = 110
    for i, (icon, weapon_id) in enumerate(zip(icons, weapon_list)):
        if i >= 4: break
        weapon_name = id_name_map.get(str(weapon_id), f"ID:{weapon_id}")

        icon = icon.resize((60, 60))
        bar = Image.open(TEXT_PATH / "weapon_bar.png")
        draw_bar = ImageDraw.Draw(bar)
        bar.paste(icon, (10, 10), icon)
        draw_bar.text(
            (80, 40), weapon_name, fill="white",
            font=WavesFonts.waves_font_18, anchor="lm"
        )
        base_img.paste(bar, (x_offset, y_offset), bar)
        x_offset += 210

    y_offset += 90

    # --- 深渊 ---
    base_img.paste(Image.open(TEXT_PATH / "tower.png"), (60, y_offset), Image.open(TEXT_PATH / "tower.png"))
    tower_name = data.tower
    bar = Image.open(TEXT_PATH / "none_bar.png")
    draw_bar = ImageDraw.Draw(bar)
    draw_bar.text(
        (30, 40), f"今日轮换: {tower_name}", fill="white",
        font=WavesFonts.waves_font_18, anchor="lm"
    )
    base_img.paste(bar, (110, y_offset), bar)

    return base_img, y_offset + 90


async def _draw_pool(
        base_img: Image.Image,
        pool_data: PoolData,
        y_offset: int
):
    """(辅助函数) 绘制卡池"""
    draw = ImageDraw.Draw(base_img)
    draw.text(
        (60, y_offset + 20), "当前卡池",
        fill="white", font=WavesFonts.waves_font_28
    )
    y_offset += 80

    # 遮罩
    mask = Image.open(TEXT_PATH / "star_mask.png").convert("L").resize((180, 180))

    # --- 5星角色 ---
    star5_list = pool_data.char_5
    star5_bg = Image.open(TEXT_PATH / "star5_bg.png")
    star5_fg = Image.open(TEXT_PATH / "star5_fg.png")

    icon_tasks = [_download_icon(i.icon) for i in star5_list[:2]]  # 最多2个
    icons = await asyncio.gather(*icon_tasks)

    x_offset = 60
    for i, (item, icon) in enumerate(zip(star5_list, icons)):
        if i >= 2: break

        bar = star5_bg.copy()
        draw_bar = ImageDraw.Draw(bar)
        if icon:
            icon = crop_center_img(icon, 180, 180)
            bar.paste(icon, (20, 20), mask)
        bar.paste(star5_fg, (0, 0), star5_fg)

        draw_bar.text(
            (120, 240), item.name, fill="white",
            font=WavesFonts.waves_font_24, anchor="mm"
        )
        base_img.paste(bar, (x_offset, y_offset), bar)
        x_offset += 220

    # --- 4星角色 ---
    star4_list = pool_data.char_4
    star4_bg = Image.open(TEXT_PATH / "star4_bg.png")
    star4_fg = Image.open(TEXT_PATH / "star4_fg.png")

    icon_tasks = [_download_icon(i.icon) for i in star4_list[:3]]  # 最多3个
    icons = await asyncio.gather(*tasks)

    x_offset = 520
    for i, (item, icon) in enumerate(zip(star4_list, icons)):
        if i >= 3: break

        bar = star4_bg.copy()
        draw_bar = ImageDraw.Draw(bar)
        if icon:
            icon = crop_center_img(icon, 120, 120)
            bar.paste(icon, (15, 15), mask.resize((120, 120)))
        bar.paste(star4_fg, (0, 0), star4_fg)

        draw_bar.text(
            (75, 160), item.name, fill="white",
            font=WavesFonts.waves_font_18, anchor="mm"
        )
        base_img.paste(bar, (x_offset, y_offset + 40), bar)
        x_offset += 150

    return base_img, y_offset + 300


async def _draw_event(
        base_img: Image.Image,
        ann_data: Dict[str, Any],
        y_offset: int
):
    """(辅助函数) 绘制活动"""
    draw = ImageDraw.Draw(base_img)
    draw.text(
        (60, y_offset + 20), "当前活动",
        fill="white", font=WavesFonts.waves_font_28
    )
    y_offset += 80

    event_list = ann_data.get("EVENT", [])[:3]  # 最多3个
    if not event_list:
        return base_img, y_offset

    event_bg = Image.open(TEXT_PATH / "event_bg.png")
    time_icon = Image.open(TEXT_PATH / "time_icon.png")

    icon_tasks = [_download_icon(i.get("icon", ""), (180, 80)) for i in event_list]
    icons = await asyncio.gather(*icon_tasks)

    for item, icon in zip(event_list, icons):
        bar = event_bg.copy()
        draw_bar = ImageDraw.Draw(bar)

        if icon:
            bar.paste(icon, (20, 20), icon)

        bar.paste(time_icon, (220, 70), time_icon)

        draw_bar.text(
            (220, 30), item.get("title", "Unknown"),
            fill="white", font=WavesFonts.waves_font_24
        )
        draw_bar.text(
            (250, 72), item.get("time", ""),
            fill=(200, 200, 200), font=WavesFonts.waves_font_18
        )

        base_img.paste(bar, (60, y_offset), bar)
        y_offset += 120

    return base_img, y_offset


async def draw_calendar_card(
        calendar_data: CalendarData,
        pool_data: PoolData,
        ann_data: Dict[str, Any]
) -> Optional[Image.Image]:
    """
    绘制日历卡片
    (迁移自 wutheringwaves_calendar/draw_calendar_card.py)
    """
    try:
        # --- 1. 初始化画布 ---
        bg = Image.open(TEXT_PATH / "bg1.jpg").convert("RGBA")
        base_img = Image.new("RGBA", bg.size, (0, 0, 0, 0))

        # 确保 wiki_service 的 id->name 映射已加载
        await wiki_service._load_maps()
        id_name_map = wiki_service._id_name_map or {}

        # --- 2. 绘制各个模块 ---
        base_img, y_pos_1 = await _draw_develop(base_img, calendar_data, id_name_map)
        base_img, y_pos_2 = await _draw_pool(base_img, pool_data, y_pos_1)
        base_img, y_pos_3 = await _draw_event(base_img, ann_data, y_pos_2)

        # --- 3. 合成 ---
        final_h = y_pos_3 + 100
        base_img = base_img.crop((0, 0, 1000, final_h))

        final_bg = Image.open(TEXT_PATH / "bg1.jpg").convert("RGBA")
        final_bg = crop_center_img(final_bg, 1000, final_h)

        final_bg.paste(base_img, (0, 0), base_img)
        final_bg = add_footer(final_bg)

        return final_bg

    except Exception as e:
        logger.error(f"绘制日历卡片失败: {e}")
        logger.exception(e)
        return None