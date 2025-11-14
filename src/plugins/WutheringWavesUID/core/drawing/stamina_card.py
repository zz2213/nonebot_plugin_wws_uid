# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/core/drawing/stamina_card.py

import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from PIL import Image, ImageDraw, ImageFont
from nonebot.log import logger

# --- 导入我们迁移的工具 ---
from ..utils.fonts import WavesFonts
from ..utils.image_helpers import add_footer, get_waves_bg
from ..utils.drawing_helpers import draw_pic
# --- 新增导入 ---
from ...services.config_service import config_service

# --- 导入结束 ---


# --- 资源路径定义 ---
ASSETS_PATH = Path(__file__).parent.parent.parent / "assets"
TEXT_PATH = ASSETS_PATH / "images" / "stamina"


# --- 路径定义完成 ---


def _format_time(seconds: int) -> str:
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
    """
    try:
        # --- 1. 数据提取 ---
        stamina_info = stats_data.get("staminaInfo", {})
        cur_stamina = stamina_info.get("stamina", 0)
        max_stamina = stamina_info.get("maxStamina", 240)

        recover_time_str = stamina_info.get("staminaRecoverTime", "0")
        recover_time_int = int(recover_time_str)

        full_time_str = "已回满"
        if cur_stamina < max_stamina and recover_time_int > 0:
            now = int(time.time())
            remaining_seconds = recover_time_int - now
            if remaining_seconds > 0:
                full_time_str = f"{_format_time(remaining_seconds)} 后回满"
            else:
                full_time_str = "已回满"
                cur_stamina = max_stamina

        # --- 动态配置替换 ---
        threshold_config = await config_service.get_config("WAVES_STAMINA_THRESHOLD")
        threshold = threshold_config if isinstance(threshold_config, int) else 200
        is_full_tip = cur_stamina >= threshold
        # --- 替换完成 ---

        # --- 2. 初始化画布 ---
        bg = get_waves_bg(1000, 300, "bg")
        base_img = Image.new("RGBA", bg.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(base_img)

        title_bar = Image.open(TEXT_PATH / "title_bar.png").convert("RGBA")
        base_img.paste(title_bar, (0, 0), title_bar)

        # --- 3. 绘制头部信息 ---
        try:
            avatar_img = await draw_pic(user_id)  # draw_pic 接收 qid
            if avatar_img:
                avatar_img = avatar_img.resize((100, 100))
                base_img.paste(avatar_img, (20, 20), avatar_img)
        except FileNotFoundError:
            logger.warning(f"draw_stamina_card: 缺少头像资源")

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

        bar_width = int(880 * (cur_stamina / max_stamina))
        if bar_width > 0:
            main_bar = main_bar.crop((0, 0, bar_width, main_bar.height))
            base_img.paste(main_bar, (60, 160), main_bar)

        draw.text(
            (500, 185), f"{cur_stamina} / {max_stamina}",
            fill="white", font=WavesFonts.waves_font_30, anchor="mm"
        )

        draw.text(
            (500, 230), full_time_str,
            fill="white", font=WavesFonts.waves_font_24, anchor="mm"
        )

        # --- 5. 绘制推送状态 (动态配置替换) ---
        draw.text(
            (820, 84), "体力推送:",
            fill="white", font=WavesFonts.waves_font_22
        )
        if is_full_tip:
            status_img = Image.open(TEXT_PATH / "yes.png").convert("RGBA")
        else:
            status_img = Image.open(TEXT_PATH / "no.png").convert("RGBA")
        base_img.paste(status_img, (910, 80), status_img)
        # --- 替换完成 ---

        # --- 6. 合成 ---
        bg.paste(base_img, (0, 0), base_img)
        bg = add_footer(bg)

        return bg

    except Exception as e:
        logger.error(f"绘制体力卡片失败 (uid: {user_info.get('uid')}): {e}")
        logger.exception(e)
        return None