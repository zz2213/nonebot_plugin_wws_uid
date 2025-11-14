# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/core/drawing/poker_card.py

from io import BytesIO
from pathlib import Path
from typing import Dict, Any, Optional

from PIL import Image, ImageDraw, ImageFont
from nonebot.log import logger

# --- 导入我们迁移的工具 ---
from ..utils.fonts import WavesFonts
from ..utils.image_helpers import add_footer, get_role_pile_old, WAVES_SHUXING_MAP, get_attribute
from ..api.client import api_client
# 导入 API 模型
from ..api.ranking_api import RankDetail

# --- 导入完成 ---


# --- 资源路径定义 ---
ASSETS_PATH = Path(__file__).parent.parent.parent / "assets"
# 适配修改：指向 assets/images/more/
TEXT_PATH = ASSETS_PATH / "images" / "more"


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


async def draw_poker_card(
        rank_detail: RankDetail,
        user_info: Dict[str, Any]
) -> Optional[Image.Image]:
    """
    绘制扑克牌
    (迁移自 wutheringwaves_more/draw_poker.py)
    :param rank_detail: 来自 game_service.get_one_rank 的单条排行数据
    :param user_info: 来自 game_service.get_user_info 的玩家数据
    """
    try:
        # --- 1. 数据提取 ---
        char_id = rank_detail.char_id

        # --- 2. 初始化画布 ---
        base_img = Image.open(TEXT_PATH / "card_bg.png").convert("RGBA")
        draw = ImageDraw.Draw(base_img)

        # --- 3. 绘制立绘 ---
        try:
            role_pic = await get_role_pile_old(char_id, custom=True)
            # 调整立绘大小和位置
            w, h = role_pic.size
            ratio = 1000 / h  # 按高度 1000 缩放
            role_pic = role_pic.resize((int(w * ratio), int(h * ratio)), Image.Resampling.LANCZOS)
            base_img.paste(role_pic, (-150, -50), role_pic)
        except Exception as e:
            logger.warning(f"Failed to load role pile for {char_id}: {e}")

        # 粘贴前景
        fg_img = Image.open(TEXT_PATH / "base_info_bg.png").convert("RGBA")
        base_img.paste(fg_img, (0, 0), fg_img)

        # --- 4. 绘制文本信息 ---
        # 昵称 & UID
        draw.text(
            (60, 60), user_info.get("nickname", "Unknown"),
            fill="white", font=WavesFonts.waves_font_28
        )
        draw.text(
            (60, 100), f"UID: {user_info.get('uid', '...-...')}",
            fill="white", font=WavesFonts.waves_font_22
        )

        # 角色名
        draw.text(
            (570, 770), rank_detail.kuro_name,
            fill="white", font=WavesFonts.waves_font_36, anchor="rm"
        )

        # 属性
        attr_name = user_info.get("attributeType", "default")  # 假设 user_info 里有
        attr_color = WAVES_SHUXING_MAP.get(attr_name, (255, 255, 255))
        attr_icon = await get_attribute(attr_name)
        if attr_icon:
            attr_icon = attr_icon.resize((40, 40))
            base_img.paste(attr_icon, (400, 720), attr_icon)
        draw.text(
            (450, 730), attr_name, fill=attr_color,
            font=WavesFonts.waves_font_24
        )

        # 伤害
        draw.text(
            (570, 820), "期望伤害",
            fill="white", font=WavesFonts.waves_font_24, anchor="rm"
        )
        draw.text(
            (570, 880), f"{rank_detail.expected_damage:.0f}",
            fill="white", font=WavesFonts.waves_font_36, anchor="rm"
        )

        # 排名
        draw.text(
            (570, 930), f"Rank. {rank_detail.rank}",
            fill=(244, 191, 11), font=WavesFonts.waves_font_28, anchor="rm"
        )

        # --- 5. 合成 ---
        base_img = add_footer(base_img)

        return base_img

    except Exception as e:
        logger.error(f"绘制扑克牌失败 (uid: {user_info.get('uid')}): {e}")
        logger.exception(e)
        return None