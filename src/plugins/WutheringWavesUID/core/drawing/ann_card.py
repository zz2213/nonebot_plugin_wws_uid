# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/core/drawing/ann_card.py

import asyncio
from io import BytesIO
from pathlib import Path
from typing import Dict, Any, Optional, List

from PIL import Image, ImageDraw, ImageFont
from nonebot.log import logger

# --- 导入我们迁移的工具 ---
from ..utils.fonts import WavesFonts
from ..utils.image_helpers import add_footer, crop_center_img
from ..api.client import api_client
# 导入服务模型
from ..services.announcement_service import AnnItem

# --- 导入完成 ---


# --- 资源路径定义 ---
ASSETS_PATH = Path(__file__).parent.parent.parent / "assets"
# 适配修改：公告模块没有本地资源，但我们保留一个路径
TEXT_PATH = ASSETS_PATH / "images" / "ann"


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


async def draw_ann_card(
        data: List[AnnItem]
) -> Optional[Image.Image]:
    """
    绘制游戏公告图
    (迁移自 wutheringwaves_ann/ann_card.py)
    """
    try:
        if not data:
            return None

        # --- 1. 下载所有公告图片 ---
        # 我们只取最新的几张
        max_items = 5
        download_tasks = []
        for item in data[:max_items]:
            download_tasks.append(_download_icon(item.pic_url))

        images = await asyncio.gather(*download_tasks)

        # 过滤掉下载失败的
        valid_images = [img for img in images if img is not None]
        if not valid_images:
            return None

        # --- 2. 计算画布尺寸 ---
        # 假设所有公告图宽度一致 (1000px)
        base_width = 1000
        total_height = 0
        resized_images = []

        for img in valid_images:
            # 缩放
            w, h = img.size
            scale = base_width / w
            new_h = int(h * scale)
            resized_img = img.resize((base_width, new_h), Image.Resampling.LANCZOS)
            resized_images.append(resized_img)
            total_height += new_h

        # --- 3. 初始化画布 ---
        bg_color = (30, 30, 30)  # 深灰色背景
        base_img = Image.new("RGBA", (base_width, total_height), bg_color)

        # --- 4. 粘贴图片 ---
        y_offset = 0
        for img in resized_images:
            base_img.paste(img, (0, y_offset), img)
            y_offset += img.height

        # --- 5. 添加页脚并返回 ---
        # (原项目没有页脚，但我们统一添加)
        # base_img = add_footer(base_img) # 公告图一般不加页脚

        return base_img

    except Exception as e:
        logger.error(f"绘制公告图失败: {e}")
        logger.exception(e)
        return None