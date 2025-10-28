# wws_native/handlers/char_list.py
import io
from PIL import Image
from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import MessageEvent, Message, MessageSegment

from ..utils import get_target_uid
from ..WutheringWavesUID.wutheringwaves_charlist.draw_char_list import draw_char_list

list_matcher = on_command("鸣潮角色", aliases={"wws角色", "ww角色"}, priority=10, block=True)


@list_matcher.handle()
async def _(matcher: Matcher, event: MessageEvent, args: Message = CommandArg()):
  target_uid = await get_target_uid(matcher, event, args)
  if not target_uid:
    return

  await matcher.send(f"正在查询UID: {target_uid} 的角色展柜...")

  try:
    img: Image.Image = await draw_char_list(int(target_uid))

    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    await matcher.finish(MessageSegment.image(img_bytes.getvalue()))
  except Exception as e:
    await matcher.finish(f"查询失败了QAQ，错误信息: {e}")