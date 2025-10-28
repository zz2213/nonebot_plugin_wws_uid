# wws_native/handlers/char_list.py
# ... (与 char_info.py 结构类似，只是调用的绘图函数不同)
from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.adapters import Bot, Event, Message

from . import get_adapter
from .. import database as db
from ..WutheringWavesUID.wutheringwaves_charlist.draw_char_list import draw_char_list

list_matcher = on_command("鸣潮角色", aliases={"wws角色", "ww角色"}, priority=10, block=True)

@list_matcher.handle()
async def _(matcher: Matcher, bot: Bot, event: Event, args: Message = CommandArg()):
    AdapterClass = get_adapter(bot)
    if not AdapterClass: return
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

    await adapter.reply(f"正在查询UID: {target_uid} 的角色展柜...")
    try:
        img = await draw_char_list(target_uid)
        await adapter.reply(img)
    except Exception as e:
        await adapter.reply(f"查询失败了QAQ，错误信息: {e}")