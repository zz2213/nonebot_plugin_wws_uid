# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/core/drawing/period_card.py

from pathlib import Path
from typing import Dict, Any, Optional

from PIL import Image, ImageDraw, ImageFont
from nonebot.log import logger

# --- 导入我们迁移的工具 ---
from ..utils.fonts import WavesFonts
from ..utils.image_helpers import add_footer
from ..utils.drawing_helpers import draw_pic  # 用于绘制头像

# --- 导入完成 ---


# --- 资源路径定义 ---
ASSETS_PATH = Path(__file__).parent.parent.parent / "assets"
# 适配修改：指向 assets/images/period/
TEXT_PATH = ASSETS_PATH / "images" / "period"


# --- 路径定义完成 ---


async def draw_period_card(
        user_info: Dict[str, Any],
        period_data: Dict[str, Any],
        user_id: str
) -> Optional[Image.Image]:
    """
    绘制资源统计卡片
    (迁移自 draw_period.py)
    """
    try:
        # --- 1. 数据提取 ---
        daily_info = period_data.get("dailyInfo", {})
        month_card_info = period_data.get("monthCardInfo", {})
        gain_info = period_data.get("gainInfo", {})

        # --- 2. 初始化画布 ---
        bg = Image.open(TEXT_PATH / "top-bg.png").convert("RGBA")
        base_img = Image.new("RGBA", bg.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(base_img)

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

        # Slogan
        slogan_img = Image.open(TEXT_PATH / "slagon.png").convert("RGBA")
        base_img.paste(slogan_img, (680, 40), slogan_img)

        # --- 4. 绘制活跃度 ---
        active_bg = Image.open(TEXT_PATH / "home-main-p1.png").convert("RGBA")
        base_img.paste(active_bg, (40, 150), active_bg)

        draw.text(
            (120, 260), str(daily_info.get("todayLiveness", 0)),
            fill="white", font=WavesFonts.arial_bold_font_30, anchor="mm"
        )
        draw.text(
            (320, 260), str(daily_info.get("weekLiveness", 0)),
            fill="white", font=WavesFonts.arial_bold_font_30, anchor="mm"
        )
        draw.text(
            (120, 360), "今日活跃",
            fill="white", font=WavesFonts.waves_font_24, anchor="mm"
        )
        draw.text(
            (320, 360), "本周活跃",
            fill="white", font=WavesFonts.waves_font_24, anchor="mm"
        )

        # --- 5. 绘制月卡 ---
        month_card_bg = Image.open(TEXT_PATH / "home-main-p2.png").convert("RGBA")
        base_img.paste(month_card_bg, (520, 150), month_card_bg)

        if month_card_info.get("isMonthCard", False):
            days = month_card_info.get("remainDays", 0)
            status_text = f"剩 {days} 天"
        else:
            status_text = "未购买"

        draw.text(
            (720, 280), status_text,
            fill="white", font=WavesFonts.waves_font_30, anchor="mm"
        )

        # --- 6. 绘制资源统计 ---
        star_bg = Image.open(TEXT_PATH / "tab-star-bg.png").convert("RGBA")
        coin_bg = Image.open(TEXT_PATH / "tab-coin-bg.png").convert("RGBA")
        base_img.paste(star_bg, (40, 430), star_bg)
        base_img.paste(coin_bg, (520, 430), coin_bg)

        draw.text(
            (280, 480), f"今日已获: {gain_info.get('todayGain', 0)}",
            fill="white", font=WavesFonts.waves_font_24, anchor="mm"
        )
        draw.text(
            (280, 520), f"本月已获: {gain_info.get('monthGain', 0)}",
            fill="white", font=WavesFonts.waves_font_24, anchor="mm"
        )

        draw.text(
            (760, 480), f"今日已获: {gain_info.get('todayShell', 0)}",
            fill="white", font=WavesFonts.waves_font_24, anchor="mm"
        )
        draw.text(
            (760, 520), f"本月已获: {gain_info.get('monthShell', 0)}",
            fill="white", font=WavesFonts.waves_font_24, anchor="mm"
        )

        # --- 7. 合成 ---
        bg.paste(base_img, (0, 0), base_img)
        bg = add_footer(bg)

        return bg

    except Exception as e:
        logger.error(f"绘制资源卡片失败 (uid: {user_info.get('uid')}): {e}")
        logger.exception(e)
        return None