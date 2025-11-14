# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/core/drawing/character_card.py
import asyncio
from io import BytesIO
from pathlib import Path
from typing import Dict, Any, List, Optional

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance  # 新增 ImageEnhance
from nonebot.log import logger

# --- 导入我们迁移的工具 ---
from ..utils.fonts import WavesFonts
from ..utils.image_helpers import (
    crop_center_img, get_waves_bg, get_square_avatar, get_square_weapon,
    get_attribute, get_attribute_prop, change_color, WAVES_SHUXING_MAP,
    draw_text_with_shadow, WAVES_ECHO_MAP
)
from ..utils.drawing_helpers import draw_pic
from ..utils.scoring import get_score_level
from ..api.client import api_client
# --- 新增导入 ---
from ..services.config_service import config_service

# --- 导入结束 ---


# --- 资源路径定义 ---
ASSETS_PATH = Path(__file__).parent.parent.parent / "assets"
TEXT_PATH = ASSETS_PATH / "images" / "charinfo"


# --- 路径定义完成 ---


# --- 异步下载工具函数 ---
async def _download_icon(url: str, size: Optional[tuple[int, int]] = None) -> Optional[Image.Image]:
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


# --- 绘图辅助函数 (迁移自 draw_char_card.py) ---

async def _draw_echo(
        data: List[Dict[str, Any]],
        recommend_attrs: List[str]
) -> Image.Image:
    img = Image.new("RGBA", (1482, 332), (0, 0, 0, 0))
    sh_bg = Image.open(TEXT_PATH / "sh_bg.png")

    sh_score_bg = {
        "SSS": Image.open(TEXT_PATH / "sh_score_bg_sss.png"),
        "SS": Image.open(TEXT_PATH / "sh_score_bg_ss.png"),
        "S": Image.open(TEXT_PATH / "sh_score_bg_s.png"),
        "A": Image.open(TEXT_PATH / "sh_score_bg_a.png"),
        "B": Image.open(TEXT_PATH / "sh_score_bg_b.png"),
        "C": Image.open(TEXT_PATH / "sh_score_bg_c.png"),
    }
    sh_score_level = {
        "SSS": Image.open(TEXT_PATH / "sh_score_sss.png"),
        "SS": Image.open(TEXT_PATH / "sh_score_ss.png"),
        "S": Image.open(TEXT_PATH / "sh_score_s.png"),
        "A": Image.open(TEXT_PATH / "sh_score_a.png"),
        "B": Image.open(TEXT_PATH / "sh_score_b.png"),
        "C": Image.open(TEXT_PATH / "sh_score_c.png"),
    }

    x_list = [0, 308, 616, 924, 1232]

    download_tasks = []
    for i, echo in enumerate(data):
        if i >= 5:
            break
        download_tasks.append(_download_icon(echo.get("icon", "")))

    icon_images = await asyncio.gather(*download_tasks)

    for i, echo in enumerate(data):
        if i >= 5:
            break

        base_img = sh_bg.copy()
        draw = ImageDraw.Draw(base_img)

        cost = echo.get("cost", 0)
        cost_color = WAVES_ECHO_MAP.get(echo.get("sonataName", ""), (255, 255, 255))
        draw.text(
            (28, 28), f"COST {cost}", fill=cost_color,
            font=WavesFonts.arial_bold_font_18
        )

        icon = icon_images[i]
        if icon:
            icon = icon.resize((100, 100), Image.Resampling.LANCZOS)
            base_img.paste(icon, (12, 54), icon)

        draw.text(
            (118, 54), echo.get("name", "Unknown"), fill="white",
            font=WavesFonts.waves_font_24
        )
        draw.text(
            (118, 88), f"Lv.{echo.get('level', 0)}", fill=(160, 160, 160),
            font=WavesFonts.waves_font_20
        )

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

        sub_entries = echo.get("subEntry", [])
        for j, sub in enumerate(sub_entries):
            sub_name = sub.get("key", "Unknown")
            sub_value = sub.get("value", 0.0)

            fill = (244, 191, 11) if sub_name in recommend_attrs else "white"
            val_str = f"{sub_value:.1f}%" if "%" in sub.get("unit", "") else str(int(sub_value))

            draw.text(
                (30, 222 + j * 24), f"· {sub_name} +{val_str}",
                fill=fill, font=WavesFonts.waves_font_18
            )

        score = echo.get("score", 0.0)
        level = get_score_level(score)

        score_bg = sh_score_bg[level].copy()
        score_level_img = sh_score_level[level].copy()

        base_img.paste(score_bg, (158, 80), score_bg)
        base_img.paste(score_level_img, (168, 88), score_level_img)
        draw_score = ImageDraw.Draw(base_img)
        draw_score.text(
            (204, 91), str(score), fill="white",
            font=WavesFonts.arial_bold_font_18, anchor="lt"
        )

        img.paste(base_img, (x_list[i], 0), base_img)

    return img


async def _draw_skill(data: List[Dict[str, Any]]) -> Image.Image:
    img = Image.new("RGBA", (722, 100), (0, 0, 0, 0))
    skill_bg = Image.open(TEXT_PATH / "skill_bg.png")
    skill_bar = Image.open(TEXT_PATH / "skill_bar.png")

    x_list = [0, 122, 244, 366, 488, 610]  # 6个技能位

    download_tasks = []
    for i, skill in enumerate(data):
        if i >= 6:
            break
        download_tasks.append(_download_icon(skill.get("icon", "")))

    icon_images = await asyncio.gather(*download_tasks)

    for i, skill in enumerate(data):
        if i >= 6:
            break

        base_img = skill_bg.copy()
        draw = ImageDraw.Draw(base_img)

        icon = icon_images[i]
        if icon:
            icon = icon.resize((66, 66), Image.Resampling.LANCZOS)
            base_img.paste(icon, (17, 10), icon)

        base_img.paste(skill_bar, (14, 76), skill_bar)

        level = skill.get("level", 1)
        draw.text(
            (49, 81), f"Lv.{level}", fill="white",
            font=WavesFonts.waves_font_16, anchor="mm"
        )

        img.paste(base_img, (x_list[i], 0), base_img)

    return img


async def _draw_weapon(data: Dict[str, Any]) -> Image.Image:
    img = Image.new("RGBA", (144, 532), (0, 0, 0, 0))

    rarity = data.get("rarity", 3)
    weapon_bg = Image.open(TEXT_PATH / f"weapon_icon_bg_{rarity}.png")
    img.paste(weapon_bg, (0, 0), weapon_bg)

    # BUG 1: 资源缺失
    try:
        weapon_icon = await get_square_weapon(data.get("id", 0))
        if weapon_icon:
            weapon_icon = weapon_icon.resize((140, 140), Image.Resampling.LANCZOS)
            img.paste(weapon_icon, (2, 2), weapon_icon)
    except FileNotFoundError:
        logger.warning(f"draw_weapon: 缺少武器图标 {data.get('id', 0)}")

    draw = ImageDraw.Draw(img)
    level_bg = Image.open(TEXT_PATH / "skill_bar.png").resize((70, 24))
    img.paste(level_bg, (37, 114), level_bg)
    draw.text(
        (72, 126), f"Lv.{data.get('level', 1)}", fill="white",
        font=WavesFonts.waves_font_16, anchor="mm"
    )

    reson_level = data.get("resonanceLevel", 1)
    reson_bg = Image.open(TEXT_PATH / "ph_0.png").resize((24, 24))
    for i in range(reson_level):
        img.paste(reson_bg, (5, 44 + i * 28), reson_bg)

    return img


async def _draw_chain(level: int, data: List[Dict[str, Any]]) -> Image.Image:
    img = Image.new("RGBA", (144, 532), (0, 0, 0, 0))
    mz_bg = Image.open(TEXT_PATH / "mz_bg.png")

    download_tasks = []
    for i, chain in enumerate(data):
        if i >= 6:
            break
        is_active = i < level
        icon_url = chain.get("icon", "") if is_active else chain.get("lockIcon", "")
        download_tasks.append(_download_icon(icon_url, (50, 50)))

    icon_images = await asyncio.gather(*download_tasks)

    y_list = [10, 95, 180, 265, 350, 435]
    for i, icon in enumerate(icon_images):
        if i >= 6:
            break

        base_img = mz_bg.copy()
        if icon:
            base_img.paste(icon, (47, 18), icon)

        img.paste(base_img, (0, y_list[i]), base_img)

    return img


async def _draw_prop(data: Dict[str, float]) -> Image.Image:
    img = Image.new("RGBA", (722, 280), (0, 0, 0, 0))
    prop_bg = Image.open(TEXT_PATH / "prop_bg.png")
    prop_bar = Image.open(TEXT_PATH / "prop_bar.png")

    draw = ImageDraw.Draw(img)

    prop_list = [
        "生命值", "攻击力", "防御力", "暴击率", "暴击伤害", "共鸣效率",
        "冷凝伤害加成", "热熔伤害加成", "导电伤害加成", "气动伤害加成", "衍射伤害加成", "湮灭伤害加成"
    ]

    icon_tasks = []
    for prop_name in prop_list:
        icon_name = prop_name.replace("率", "").replace("值", "").replace("力", "")
        icon_tasks.append(get_attribute_prop(icon_name))

    icon_images = await asyncio.gather(*icon_tasks)

    x_offset, y_offset = 0, 0
    for i, (prop_name, icon) in enumerate(zip(prop_list, icon_images)):
        if i == 6:
            x_offset = 366  # 换列
            y_offset = 0

        base_img = prop_bg.copy()
        draw_item = ImageDraw.Draw(base_img)

        # BUG 1: 资源缺失
        try:
            if icon:
                icon = icon.resize((38, 38))
                base_img.paste(icon, (14, 18), icon)
        except FileNotFoundError:
            logger.warning(f"draw_prop: 缺少属性图标 {prop_name}")

        base_img.paste(prop_bar, (150, 24), prop_bar)

        draw_item.text(
            (62, 28), prop_name, fill="white",
            font=WavesFonts.waves_font_22
        )

        val = data.get(prop_name, 0.0)
        unit = "%" if prop_name not in ["生命值", "攻击力", "防御力"] else ""
        val_str = f"{val:.1f}{unit}" if unit == "%" else str(int(val))

        draw_item.text(
            (320, 31), val_str, fill="white",
            font=WavesFonts.waves_font_22, anchor="rm"
        )

        img.paste(base_img, (x_offset, y_offset), base_img)
        y_offset += 46

    return img


async def draw_character_card(data: Dict[str, Any]) -> Optional[Image.Image]:
    """
    绘制角色面板图 (重构自 draw_char_card.py)
    :param data: 由 CharacterService.get_character_panel_data() 返回的数据
    """

    try:
        # --- 1. 初始化画布 ---
        bg = get_waves_bg(1506, 1000)

        role_id = data.get("id", 0)
        role_pic_url = data.get("card", "")
        if role_pic_url:
            role_pic = await _download_icon(role_pic_url)
            if role_pic:
                role_pic = crop_center_img(role_pic, 1506, 1000)

                # --- 动态配置替换 ---
                radius = await config_service.get_config("WAVES_BLUR_RADIUS") or 6
                brightness = await config_service.get_config("WAVES_BLUR_BRIGHTNESS") or 0.8
                contrast = await config_service.get_config("WAVES_BLUR_CONTRAST") or 1.2

                role_pic = role_pic.filter(ImageFilter.GaussianBlur(radius=radius))
                role_pic = ImageEnhance.Brightness(role_pic).enhance(brightness)
                role_pic = ImageEnhance.Contrast(role_pic).enhance(contrast)
                # --- 替换完成 ---

                bg.paste(role_pic, (0, 0), role_pic)

        base_img = Image.new("RGBA", (1506, 1000))
        draw = ImageDraw.Draw(base_img)

        banner = Image.open(TEXT_PATH / "banner1.png")
        base_img.paste(banner, (0, 0), banner)

        # BUG 1: 资源缺失
        try:
            avatar_img = await draw_pic(role_id)
            if avatar_img:
                base_img.paste(avatar_img, (16, 18), avatar_img)
        except FileNotFoundError:
            logger.warning(f"draw_character_card: 缺少头像 {role_id}")

        draw.text(
            (210, 60), data.get("name", "Unknown"), fill="white",
            font=WavesFonts.waves_font_36
        )
        draw.text(
            (210, 110), f"UID {data.get('uid', '...-...')}", fill="white",
            font=WavesFonts.waves_font_24
        )
        draw.text(
            (440, 110), f"Lv.{data.get('level', 1)}", fill="white",
            font=WavesFonts.waves_font_24
        )

        # BUG 1: 资源缺失
        try:
            attr_name = data.get("attributeType", "default")
            attr_icon = await get_attribute(attr_name)
            if attr_icon:
                attr_icon = attr_icon.resize((50, 50))
                base_img.paste(attr_icon, (130, 120), attr_icon)
        except FileNotFoundError:
            logger.warning(f"draw_character_card: 缺少属性图标 {attr_name}")

        # --- 2. 绘制各个模块 ---

        tasks = {
            "prop": _draw_prop(data.get("formattedAttribute", {})),
            "weapon": _draw_weapon(data.get("weapon", {})),
            "chain": _draw_chain(data.get("resonanceLevel", 0), data.get("resonance", [])),
            "skill": _draw_skill(data.get("skillList", [])),
            "echo": _draw_echo(data.get("echoList", []), data.get("recommendAttrs", []))
        }

        results = await asyncio.gather(*tasks.values())
        draw_results = dict(zip(tasks.keys(), results))

        # --- 3. 粘贴各个模块 ---

        if draw_results["prop"]:
            base_img.paste(draw_results["prop"], (190, 206), draw_results["prop"])

        if draw_results["weapon"]:
            base_img.paste(draw_results["weapon"], (938, 206), draw_results["weapon"])

        if draw_results["chain"]:
            base_img.paste(draw_results["chain"], (1094, 206), draw_results["chain"])

        if draw_results["skill"]:
            base_img.paste(draw_results["skill"], (190, 504), draw_results["skill"])

        if draw_results["echo"]:
            base_img.paste(draw_results["echo"], (14, 638), draw_results["echo"])

        # --- 4. 合成最终图像 ---
        bg.paste(base_img, (0, 0), base_img)

        return bg

    except Exception as e:
        logger.error(f"绘制角色面板失败 (role_id: {data.get('id')}): {e}")
        logger.exception(e)  # 打印详细堆栈
        return None