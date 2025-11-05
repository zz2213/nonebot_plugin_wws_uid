from nonebot import on_command
from nonebot.adapters import Bot, Event

from ..database import get_uid_by_user

# 用户信息查询命令
user_info_cmd = on_command("鸣潮信息", aliases={"waves信息"}, priority=5)


@user_info_cmd.handle()
async def handle_user_info(bot: Bot, event: Event):
  """处理用户信息查询"""
  user_id = str(getattr(event, 'user_id', ''))
  bot_id = event.get_type()

  uid = await get_uid_by_user(user_id, bot_id)
  if uid:
    await bot.send(event, f"您的鸣潮UID是: {uid}")
  else:
    await bot.send(event, "您还未绑定鸣潮UID，请先使用【鸣潮登录】命令")