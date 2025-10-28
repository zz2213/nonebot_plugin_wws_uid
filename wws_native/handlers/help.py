# wws_native/handlers/help.py
from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.adapters import Bot, Event

from . import get_adapter
from ..WutheringWavesUID.wutheringwaves_help import get_help

help_matcher = on_command("鸣潮帮助", aliases={"wws帮助", "ww帮助"}, priority=5, block=True)


@help_matcher.handle()
async def _(matcher: Matcher, bot: Bot, event: Event):
  AdapterClass = get_adapter(bot)
  if not AdapterClass:
    return
  adapter = AdapterClass(bot, event, matcher)

  img = await get_help.run()
  await adapter.reply(img)