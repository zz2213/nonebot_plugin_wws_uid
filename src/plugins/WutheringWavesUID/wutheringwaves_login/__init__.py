import re

from nonebot import logger

from ..gsuid_core_compat import (
    Bot,
    Event,
    SV
)

sv_kuro_login = SV("库洛登录")


@sv_kuro_login.on_command(("登录", "登陆", "登入", "登龙", "login"))
async def get_login_msg(bot: Bot, ev: Event):
    logger.info("开始登录")
    game_title = "[鸣潮]"

    # uid_list = await WavesBind.get_uid_list_by_game(ev.user_id, ev.bot_id)
    # if uid_list is None:
    #     return await bot.send(ERROR_CODE[WAVES_CODE_103])

    text = re.sub(r'["\n\t ]+', "", ev.text.strip())
    text = text.replace("，", ",")
    if text == "":
        return await bot.send("登录超时!\n", at_sender=at_sender)

    elif "," in text:
        return await bot.send("登录超时!\n", at_sender=at_sender)

    elif text.isdigit():
        return

    at_sender = True if ev.group_id else False
    return await bot.send(
        f"{game_title} 账号登录失败\n请重新输入命令【登录】进行登录\n",
        at_sender=at_sender,
    )
