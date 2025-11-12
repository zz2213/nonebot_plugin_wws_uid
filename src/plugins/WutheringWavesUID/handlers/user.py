from nonebot import on_command
from nonebot.adapters import Bot, Event

from ..services.bind_service import BindService
from ..services.game_service import GameService
from ..services.user_service import UserService

user_info_cmd = on_command("鸣潮信息", aliases={"waves信息"}, priority=5)

@user_info_cmd.handle()
async def handle_user_info(bot: Bot, event: Event):
    """处理用户信息查询"""
    user_id = str(getattr(event, 'user_id', ''))
    bot_id = event.get_type()

    # 获取绑定的UID
    bind_service = BindService()
    uid = await bind_service.get_user_uid(user_id, bot_id)

    if not uid:
        await bot.send(event, "您还未绑定鸣潮UID，请先使用【鸣潮登录】命令")
        return

    # 获取用户Cookie
    user_service = UserService()
    user = await user_service.get_user(user_id, bot_id)

    if not user or not user.cookie:
        await bot.send(event, "登录信息已过期，请重新登录")
        return

    # 获取游戏数据
    game_service = GameService()
    user_info = await game_service.get_user_info(user.cookie, uid)
    role_info = await game_service.get_role_info(user.cookie, uid)

    if not user_info:
        await bot.send(event, "获取用户信息失败，请检查登录状态")
        return

    # 构建回复消息
    nickname = user_info.get("nickname", "未知")
    level = user_info.get("level", 0)

    message = [
        "【鸣潮用户信息】",
        f"UID: {uid}",
        f"昵称: {nickname}",
        f"等级: {level}",
    ]

    # 添加角色信息
    if role_info:
        # 根据实际API响应结构调整
        pass

    await bot.send(event, "\n".join(message))