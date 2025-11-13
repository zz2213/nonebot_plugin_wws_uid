# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/core/utils/drawing_helpers.py

from pathlib import Path
from PIL import Image

# --- 依赖替换 ---
from nonebot.adapters.onebot.v11 import MessageEvent as Event  # 替换: from gsuid_core.models import Event
from .image_helpers import crop_center_img  # 替换: from gsuid_core.utils.image.image_tools
from .image_helpers import get_event_avatar, get_square_avatar # 替换: from ..utils.image
# --- 依赖替换完成 ---


# 路径重新定义
TEXT_PATH = Path(__file__).parent.parent.parent / "assets" / "images" / "utils"


async def draw_pic_with_ring(ev: Event):
    pic = await get_event_avatar(ev)

    mask_pic = Image.open(TEXT_PATH / "avatar_mask.png")
    avatar = Image.new("RGBA", (180, 180))
    mask = mask_pic.resize((160, 160))
    resize_pic = crop_center_img(pic, 160, 160)
    avatar.paste(resize_pic, (20, 20), mask)

    avatar_ring = Image.open(TEXT_PATH / "avatar_ring.png")
    avatar_ring = avatar_ring.resize((180, 180))
    return avatar, avatar_ring


async def draw_pic(roleId):
    pic = await get_square_avatar(roleId)
    mask_pic = Image.open(TEXT_PATH / "avatar_mask.png")
    img = Image.new("RGBA", (180, 180))
    mask = mask_pic.resize((140, 140))
    resize_pic = crop_center_img(pic, 140, 140)
    img.paste(resize_pic, (22, 18), mask)

    return img