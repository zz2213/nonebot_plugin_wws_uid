# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/core/drawing/role_info_card.py

import asyncio
from io import BytesIO
from pathlib import Path
from typing import Dict, Any, Optional

from PIL import Image, ImageDraw, ImageFont
from nonebot.log import logger

# --- 导入我们迁移的工具 ---
from ..utils.fonts import WavesFonts
from ..utils.image_helpers import add_footer, get_waves_bg, get_square_avatar
from ..utils.drawing_helpers import draw_pic  # 用于绘制头像

# --- 导入完成 ---


# --- 资源路径定义 ---
ASSETS_PATH = Path(__file__).parent.parent.parent / "assets"
# 适配修改：指向 assets/images/roleinfo/
TEXT_PATH = ASSETS_PATH / "images" / "roleinfo"


# --- 路径定义完成 ---


async def draw_role_info_card(
        user_info: Dict[str, Any],
        user_id: str
) -> Optional[Image.Image]:
    """
    绘制基础信息卡片
    (迁移自 wutheringwaves_roleinfo/draw_role_info.py)
    """
    try:
        # --- 1. 数据提取 ---
        # 活跃度
        active_days = user_info.get("activeDays", 0)
        level = user_info.get("level", 0)

        # 统计
        stats_info = user_info.get("stats", {})
        char_count = stats_info.get("roleCount", 0)
        weapon_count = stats_info.get("weaponCount", 0)
        echo_count = stats_info.get("phantomCount", 0)

        # TODO: 原图还有 "角色图鉴" "声骸图鉴" "武器图鉴"，
        # 但 get_user_info 接口似乎没返回？暂时写死
        char_book = stats_info.get("roleBook", char_count)
        echo_book = stats_info.get("phantomBook", echo_count)
        weapon_book = stats_info.get("weaponBook", weapon_count)

        # --- 2. 初始化画布 ---
        bg = get_waves_bg(1000, 700, "bg")  # 复用 bg.jpg
        base_img = Image.new("RGBA", bg.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(base_img)

        top_bg = Image.open(TEXT_PATH / "title_bar.png").convert("RGBA")
        base_img.paste(top_bg, (0, 0), top_bg)

        main_bg = Image.open(TEXT_PATH / "base_info_bg.png").convert("RGBA")
        base_img.paste(main_bg, (0, 140), main_bg)

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
        draw.text(
            (400, 84), f"Lv.{level}",
            fill="white", font=WavesFonts.waves_font_22
        )
        draw.text(
            (500, 84), f"活跃天数: {active_days}",
            fill="white", font=WavesFonts.waves_font_22
        )

        # --- 4. 绘制统计信息 ---

        # 角色
        char_bg = Image.open(TEXT_PATH / "char_bg.png").convert("RGBA")
        base_img.paste(char_bg, (50, 200), char_bg)
        draw.text(
            (100, 360), f"拥有角色: {char_count}",
            fill="white", font=WavesFonts.waves_font_24
        )

        # 武器
        weapon_bg = Image.open(TEXT_PATH / "weapon_bg.png").convert("RGBA")
        base_img.paste(weapon_bg, (370, 200), weapon_bg)
        draw.text(
            (420, 360), f"拥有武器: {weapon_count}",
            fill="white", font=WavesFonts.waves_font_24
        )

        # 声骸
        echo_bg = Image.open(TEXT_PATH / "bs.png").convert("RGBA")
        base_img.paste(echo_bg, (690, 200), echo_bg)
        draw.text(
            (740, 360), f"拥有声骸: {echo_count}",
            fill="white", font=WavesFonts.waves_font_24
        )

        # --- 5. 绘制图鉴信息 ---
        y_offset = 460
        draw.text(
            (120, y_offset), f"角色图鉴: {char_book}",
            fill="white", font=WavesFonts.waves_font_28, anchor="lm"
        )
        draw.text(
            (120, y_offset + 80), f"武器图鉴: {weapon_book}",
            fill="white", font=WavesFonts.waves_font_28, anchor="lm"
        )
        draw.text(
            (120, y_offset + 160), f"声骸图鉴: {echo_book}",
            fill="white", font=WavesFonts.waves_font_28, anchor="lm"
        )

        # --- 6. 合成 ---
        bg.paste(base_img, (0, 0), base_img)
        bg = add_footer(bg)

        return bg

    except Exception as e:
        logger.error(f"绘制基础信息卡片失败 (uid: {user_info.get('uid')}): {e}")
        logger.exception(e)
        return None