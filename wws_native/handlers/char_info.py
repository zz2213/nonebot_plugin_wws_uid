# wws_native/handlers/char_info.py
import io
from PIL import Image
from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import MessageEvent, Message, MessageSegment

# 导入我们的工具函数和原项目的绘图函数
from ..utils import get_target_uid
from ..WutheringWavesUID.wutheringwaves_charinfo.draw_char_card import draw_char_card

info_matcher = on_command("鸣潮查询", aliases={"wws查询", "ww查询"}, priority=10, block=True)


@info_matcher.handle()
async def _(matcher: Matcher, event: MessageEvent, args: Message = CommandArg()):
  # 使用工具函数获取目标UID
  target_uid = await get_target_uid(matcher, event, args)
  if not target_uid:
    return

  await matcher.send(f"正在查询UID: {target_uid} 的玩家信息...")

  try:
    # 调用原项目的绘图函数
    img: Image.Image = await draw_char_card(int(target_uid))

    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    await matcher.finish(MessageSegment.image(img_bytes.getvalue()))
  except Exception as e:
    await matcher.finish(f"查询失败了QAQ，错误信息: {e}")