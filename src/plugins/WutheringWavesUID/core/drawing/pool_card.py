# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/core/drawing/pool_card.py

import asyncio
from io import BytesIO
from pathlib import Path
from typing import Dict, Any, Optional, List

from PIL import Image, ImageDraw, ImageFont
from nonebot.log import logger

# --- 导入我们迁移的工具 ---
from ..utils.fonts import WavesFonts
from ..utils.image_helpers import add_footer, get_waves_bg, get_square_avatar
from ..api.client import api_client
# 导入 API 模型
from ..api.ranking_api import PoolData, PoolDetail, PoolItem

# --- 导入完成 ---


# --- 资源路径定义 ---
ASSETS_PATH = Path(__file__).parent.parent.parent / "assets"
# 适配修改：指向 assets/images/up/
TEXT_PATH = ASSETS_PATH / "images" / "up"


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


async def _draw_pool_item(
        pool: PoolDetail
) -> Image.Image:
    """(辅助函数) 绘制单个卡池统计"""

    # 异步下载图标
    avatar_task = get_square_avatar(pool.char_id)
    pool_img_task = _download_icon(pool.pool_img, (920, 200))
    avatar_img, pool_img = await asyncio.gather(avatar_task, pool_img_task)

    base_img = Image.new("RGBA", (920, 480), (0, 0, 0, 0))
    draw = ImageDraw.Draw(base_img)

    # 绘制卡池图
    if pool_img:
        mask = Image.open(TEXT_PATH / "char_mask.png").convert("L")
        mask = mask.resize((920, 200))
        base_img.paste(pool_img, (0, 0), mask)

    # 绘制头像
    if avatar_img:
        avatar_img = avatar_img.resize((100, 100))
        avatar_mask = Image.open(TEXT_PATH / "avatar_mask.png").convert("L")
        avatar_mask = avatar_mask.resize((100, 100))
        base_img.paste(avatar_img, (40, 60), avatar_mask)

    # 绘制标题和总数
    draw.text(
        (160, 60), pool.char_name,
        fill="white", font=WavesFonts.waves_font_30
    )
    draw.text(
        (160, 110), f"卡池: {pool.name}",
        fill=(200, 200, 200), font=WavesFonts.waves_font_22
    )
    draw.text(
        (880, 160), f"总抽数: {pool.total}",
        fill="white", font=WavesFonts.waves_font_24, anchor="ra"
    )

    # 绘制进度条
    bar_bg = Image.open(TEXT_PATH / "bar.png").convert("RGBA")
    bar_img = bar_bg.resize((840, 30))
    base_img.paste(bar_img, (40, 220), bar_img)

    x_offset = 40
    total_percent = 0.0

    for i, item in enumerate(pool.data):
        percent = item.num / pool.total
        bar_w = int(840 * percent)
        if bar_w <= 0:
            continue

        color = (255, 215, 0) if "1抽" in item.name else (180, 120, 255)
        bar_fill = Image.new("RGBA", (bar_w, 30), color)
        base_img.paste(bar_fill, (x_offset, 220), bar_fill)

        # 绘制百分比
        total_percent += percent
        percent_str = f"{total_percent * 100:.1f}%"
        draw.text(
            (x_offset + bar_w - 5, 225), percent_str,
            fill="black", font=WavesFonts.waves_font_18, anchor="ra"
        )
        x_offset += bar_w

    # 绘制图例
    y_offset = 280
    for item in pool.data:
        color = (255, 215, 0) if "1抽" in item.name else (180, 120, 255)
        draw.rectangle([(40, y_offset), (60, y_offset + 20)], fill=color)

        rate = item.num / pool.total * 100
        text = f"{item.name}: {item.num}人 ({rate:.1f}%)"
        draw.text(
            (80, y_offset + 10), text,
            fill="white", font=WavesFonts.waves_font_20, anchor="lm"
        )
        y_offset += 30

    return base_img


async def draw_pool_card(data: PoolData) -> Optional[Image.Image]:
    """
    绘制卡池统计图
    (迁移自 wutheringwaves_up/pool.py)
    """
    try:
        pool_list = data.data
        if not pool_list:
            return None

        # --- 1. 初始化画布 ---
        card_h = 500 * len(pool_list) + 240
        bg = get_waves_bg(1000, card_h)
        base_img = Image.new("RGBA", bg.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(base_img)

        # 绘制标题
        draw.text(
            (500, 60), "卡池统计",
            fill="white", font=WavesFonts.waves_font_36, anchor="mm"
        )
        draw.text(
            (500, 110), f"数据总数: {data.total} | 更新时间: {data.time}",
            fill="white", font=WavesFonts.waves_font_24, anchor="mm"
        )

        # --- 2. 绘制条目 ---
        draw_tasks = [_draw_pool_item(pool) for pool in pool_list]
        bar_images = await asyncio.gather(*draw_tasks)

        # --- 3. 粘贴条目 ---
        y_offset = 160
        for bar_img in bar_images:
            base_img.paste(bar_img, (40, y_offset), bar_img)
            y_offset += 500  # 每个条目高度

        # --- 4. 合成 ---
        bg.paste(base_img, (0, 0), base_img)
        bg = add_footer(bg)

        return bg

    except Exception as e:
        logger.error(f"绘制卡池统计失败: {e}")
        logger.exception(e)
        return None