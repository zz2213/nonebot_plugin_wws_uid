# wws_native/handlers/bind.py
from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.adapters import Bot, Event, Message

from . import get_adapter
from ..WutheringWavesUID.wutheringwaves_user.deal import bind_user

bind_matcher = on_command("鸣潮绑定", aliases={"wws绑定", "ww绑定"}, priority=10, block=True)

@bind_matcher.handle()
async def _(matcher: Matcher, bot: Bot, event: Event, args: Message = CommandArg()):
    AdapterClass = get_adapter(bot)
    if not AdapterClass:
        return
    adapter = AdapterClass(bot, event, matcher)

    uid_to_bind = args.extract_plain_text().strip()
    if not uid_to_bind or not uid_to_bind.isdigit():
        await adapter.reply("请输入正确的UID！格式：鸣潮绑定 123456789")
        return

    # 注意：bind_user 现在需要接收 adapter 对象
    result_msg = await bind_user(adapter, int(uid_to_bind))
    await adapter.reply(result_msg)