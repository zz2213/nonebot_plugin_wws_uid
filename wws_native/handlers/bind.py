# wws_native/handlers/bind.py
from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import MessageEvent, Message

# 从被改造的 WutheringWavesUID 项目中导入绑定逻辑函数
from ..WutheringWavesUID.wutheringwaves_user.deal import bind_user

bind_matcher = on_command("鸣潮绑定", aliases={"wws绑定", "ww绑定"}, priority=10, block=True)


@bind_matcher.handle()
async def _(matcher: Matcher, event: MessageEvent, args: Message = CommandArg()):
  uid_to_bind = args.extract_plain_text().strip()

  if not uid_to_bind or not uid_to_bind.isdigit():
    await matcher.finish("请输入正确的UID！格式：鸣潮绑定 123456789")

  # 调用原项目的绑定逻辑，它内部会调用我们重写的数据库函数
  # 并返回一个字符串作为结果
  result_msg = await bind_user(user_id=event.user_id, uid=int(uid_to_bind))
  await matcher.finish(result_msg)