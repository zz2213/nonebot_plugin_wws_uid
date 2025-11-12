import re
from nonebot import on_command
from nonebot.adapters import Bot, Event
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message

from ..core.utils.login import LoginManager

login_cmd = on_command("鸣潮登录", aliases={"waves登录", "鸣潮login"}, priority=5)
code_login_cmd = on_command("鸣潮验证码登录", aliases={"waves验证码登录"}, priority=5)

@login_cmd.handle()
async def handle_login(bot: Bot, event: Event):
    """处理登录命令"""
    login_manager = LoginManager(bot, event)
    await login_manager.start_login()

@code_login_cmd.handle()
async def handle_code_login(bot: Bot, event: Event, args: Message = CommandArg()):
    """处理验证码登录"""
    text = args.extract_plain_text().strip()
    if not text:
        await bot.send(event, "请提供手机号和验证码，格式：手机号,验证码")
        return

    login_manager = LoginManager(bot, event)
    await login_manager.code_login(text)