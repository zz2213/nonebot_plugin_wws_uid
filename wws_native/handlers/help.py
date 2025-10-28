# wws_native/handlers/help.py
import io
from PIL import Image
from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import MessageSegment

# 从被改造的 WutheringWavesUID 项目中导入绘图函数
from ..WutheringWavesUID.wutheringwaves_help import get_help

# 注册 "鸣潮帮助" 指令
help_matcher = on_command("鸣潮帮助", aliases={"wws帮助", "ww帮助"}, priority=5, block=True)


@help_matcher.handle()
async def _(matcher: Matcher):
  # 调用原项目的绘图函数
  img: Image.Image = await get_help.run()

  # 将返回的Pillow图片转换为MessageSegment并发送
  img_bytes = io.BytesIO()
  img.save(img_bytes, format="PNG")
  await matcher.finish(MessageSegment.image(img_bytes.getvalue()))