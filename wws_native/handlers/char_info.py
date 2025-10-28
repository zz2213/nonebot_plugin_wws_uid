# wws_native/handlers/char_info.py
from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.adapters import Bot, Event, Message

from . import get_adapter
from .. import database as db
from ..WutheringWavesUID.wutheringwaves_charinfo.draw_char_card import draw_char_card

info_matcher = on_command("鸣潮查询", aliases={"wws查询", "ww查询"}, priority=10, block=True)


@info_matcher.handle()
async def _(matcher: Matcher, bot: Bot, event: Event, args: Message = CommandArg()):
  AdapterClass = get_adapter(bot)
  if not AdapterClass:
    return
  adapter = AdapterClass(bot, event, matcher)

  uid_input = args.extract_plain_text().strip()
  target_uid = 0

  if uid_input and uid_input.isdigit():
    target_uid = int(uid_input)
  elif not uid_input:
    bound_uid = await db.get_uid_by_qq(int(adapter.get_user_id()))
    if bound_uid:
      target_uid = bound_uid
    else:
      await adapter.reply("您还未绑定UID, 请使用 [鸣潮绑定 UID] 指令, 或在指令后加上UID。")
      return
  else:
    await adapter.reply(f"UID [ {uid_input} ] 格式不正确, 应为纯数字。")
    return

  await adapter.reply(f"正在查询UID: {target_uid} 的玩家信息...")

  try:
    img = await draw_char_card(target_uid)
    await adapter.reply(img)
  except Exception as e:
    await adapter.reply(f"查询失败了QAQ，错误信息: {e}")