# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/core/utils/image.py

from io import BytesIO
from PIL import Image
from nonebot.adapters.onebot.v11 import MessageSegment

def pil_to_bytes(image: Image.Image, format: str = "PNG") -> bytes:
    """
    将PIL图像对象转换为bytes
    :param image: PIL图像对象
    :param format: 图像格式 (PNG, JPEG, etc.)
    :return: 图像的bytes
    """
    buffered = BytesIO()
    # 适配修改：高质量 JPEG
    if format == "JPEG":
        image.save(buffered, format=format, quality=95)
    else:
        image.save(buffered, format=format)
    return buffered.getvalue()

def pil_to_img_msg(image: Image.Image, format: str = "PNG") -> MessageSegment:
    """
    将PIL图像对象转换为OneBot V11的MessageSegment
    :param image: PIL图像对象
    :param format: 图像格式
    :return: OneBot V11的MessageSegment
    """
    return MessageSegment.image(pil_to_bytes(image, format))