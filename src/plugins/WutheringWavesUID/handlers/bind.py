from nonebot import on_command
from nonebot.adapters import Bot, Event
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message

from ..services.bind_service import BindService

bind_cmd = on_command("鸣潮绑定", aliases={"waves绑定"}, priority=5)

@bind_cmd.handle()
async def handle_bind(bot: Bot, event: Event, args: Message = CommandArg()):
    """处理绑定命令"""
    text = args.extract_plain_text().strip()
    user_id = str(getattr(event, 'user_id', ''))
    bot_id = event.get_type()
    group_id = str(getattr(event, 'group_id', ''))

    if not text:
        # 显示当前绑定
        bind_service = BindService()
        uid = await bind_service.get_user_uid(user_id, bot_id)
        if uid:
            await bot.send(event, f"当前绑定的UID: {uid}")
        else:
            await bot.send(event, "您还未绑定UID，请使用【鸣潮登录】或【鸣潮绑定 UID】")
        return

    # 绑定新UID
    if not text.isdigit() or len(text) != 9:
        await bot.send(event, "UID格式错误，请输入9位数字UID")
        return

    bind_service = BindService()
    success = await bind_service.bind_user(user_id, bot_id, text, group_id)

    if success:
        await bot.send(event, f"绑定成功！UID: {text}")
    else:
        await bot.send(event, "绑定失败，请稍后重试")