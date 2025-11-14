# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/core/drawing/update_log_card.py

import json
from pathlib import Path
from typing import Dict, Any, Optional
import aiofiles
from PIL import Image, ImageDraw, ImageFont
from nonebot.log import logger

# --- 导入我们迁移的工具 ---
from ..utils.fonts import WavesFonts
from ..utils.image_helpers import add_footer, get_waves_bg, crop_center_img

# --- 导入完成 ---


# --- 资源路径定义 ---
ASSETS_PATH = Path(__file__).parent.parent.parent / "assets"
# 适配修改：指向 assets/images/update/
TEXT_PATH = ASSETS_PATH / "images" / "update"
# 适配修改：指向 core/data/log.json
DATA_PATH = Path(__file__).parent.parent.parent / "core" / "data"
LOG_JSON_PATH = DATA_PATH / "log.json"


# --- 路径定义完成 ---


async def draw_update_log_card() -> Optional[Image.Image]:
    """
    绘制更新日志卡片
    (迁移自 wutheringwaves_update/draw_update_log.py)
    """
    try:
        # 1. 异步加载 log.json
        try:
            async with aiofiles.open(LOG_JSON_PATH, 'r', encoding='utf-8') as f:
                content = await f.read()
                log_data: Dict[str, List[str]] = json.loads(content)
        except Exception as e:
            logger.error(f"Failed to load log.json: {e}")
            return None  # 缺少 log.json 无法绘制

        versions = list(log_data.keys())
        if not versions:
            return None

        # --- 2. 初始化画布 ---
        # 动态计算高度
        line_count = 0
        for logs in log_data.values():
            line_count += len(logs) + 1  # +1 是版本号标题

        card_h = line_count * 40 + 240  # 动态高度

        bg = get_waves_bg(800, card_h, "bg")  # 复用 bg.jpg
        base_img = Image.new("RGBA", bg.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(base_img)

        # 绘制标题栏
        title_bar = Image.open(TEXT_PATH / "log_title.png").convert("RGBA")
        base_img.paste(title_bar, (0, 0), title_bar)

        # --- 3. 绘制日志条目 ---
        y_offset = 140

        # 倒序显示
        for version in reversed(versions):
            logs = log_data[version]

            # 绘制版本号
            draw.text(
                (60, y_offset), f"v {version}",
                fill="white", font=WavesFonts.waves_font_24
            )
            y_offset += 40

            # 绘制更新内容
            for line in logs:
                draw.text(
                    (80, y_offset), line,
                    fill=(200, 200, 200), font=WavesFonts.waves_font_20
                )
                y_offset += 35  # 行间距

            y_offset += 20  # 组间距

        # --- 4. 合成 ---
        bg.paste(base_img, (0, 0), base_img)
        bg = add_footer(bg)

        return bg

    except Exception as e:
        logger.error(f"绘制更新日志失败: {e}")
        logger.exception(e)
        return None