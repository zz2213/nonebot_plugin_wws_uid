# wws_native/handlers/user.py
from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.adapters import Bot, Event, Message
from . import create_adapter

# 导入我们自己的原生数据库
from .. import database as db
from ..adapters import MessageAdapter


# [重构] 这是一个独立的业务函数，不再是指令处理器
async def bind_user(adapter: MessageAdapter, uid: int) -> str:
  user_id = int(adapter.get_user_id())

  try:
    # 调用我们自己的原生数据库函数
    flag = await db.bind_uid_by_qq(user_id, uid)
    return "绑定成功！" if flag else "绑定失败！"
  except Exception as e:
    return f"绑定时发生错误: {e}"


# [原生] 这是新的指令处理器
on_command(
    "鸣潮绑定", aliases={"wws绑定", "ww绑定"}, priority=10, block=True
).handle()


async def _(matcher: Matcher, bot: Bot, event: Event, args: Message = CommandArg()):
  adapter = create_adapter(bot, event, matcher)
  if not adapter: return

  uid_to_bind_str = args.extract_plain_text().strip()
  if not uid_to_bind_str or not uid_to_bind_str.isdigit():
    await adapter.reply("请输入正确的UID！格式：鸣潮绑定 123456789")
    return

  # 调用重构后的业务函数
  result_msg = await bind_user(adapter, int(uid_to_bind_str))
  await adapter.reply(result_msg)