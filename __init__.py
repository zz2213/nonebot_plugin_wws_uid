# nonebot_plugin_wws_uid/__init__.py

from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, MessageEvent
from nonebot.matcher import Matcher
from nonebot.log import logger

from . import database as db
from .data_source import WutheringWavesAPI, generate_info_card

# 1. 查询指令
wws_query = on_command("鸣潮查询", aliases={"wws查询", "查鸣潮"}, priority=5, block=True)


@wws_query.handle()
async def handle_query(matcher: Matcher, event: MessageEvent, args: Message = CommandArg()):
  uid_input = args.extract_plain_text().strip()
  user_id = str(event.user_id)

  target_uid = ""
  if uid_input:
    if not uid_input.isdigit():
      await wws_query.finish("UID必须是纯数字哦！")
    target_uid = uid_input
  else:
    # 如果用户没有输入UID，则尝试从数据库中获取绑定的UID
    bound_uid = await db.get_uid(user_id)
    if not bound_uid:
      await wws_query.finish("你还未绑定UID，请使用【鸣潮绑定 UID】指令进行绑定，或使用【鸣潮查询 UID】查询指定玩家。")
    target_uid = bound_uid

  await matcher.send(f"正在查询UID: {target_uid}，请稍候...")

  try:
    api = WutheringWavesAPI(uid=target_uid)
    player_data = await api.get_player_data()

    # 生成并发送结果图片
    result_image_segment = await generate_info_card(player_data)
    await matcher.finish(result_image_segment)  # 直接发送图片消息段

  except Exception as e:
    logger.exception("查询处理失败")
    await matcher.finish(f"查询失败了QAQ，错误信息：{e}")


# 2. 绑定指令
wws_bind = on_command("鸣潮绑定", aliases={"wws绑定"}, priority=5, block=True)


@wws_bind.handle()
async def handle_bind(event: MessageEvent, args: Message = CommandArg()):
  uid_to_bind = args.extract_plain_text().strip()

  if not uid_to_bind or not uid_to_bind.isdigit():
    await wws_bind.finish("请输入要绑定的正确UID！")

  try:
    user_id = str(event.user_id)
    # 在绑定前，可以先验证一下UID是否有效
    await matcher.send(f"正在验证UID: {uid_to_bind}...")
    api = WutheringWavesAPI(uid=uid_to_bind)
    await api.get_player_data()  # 如果UID无效，这里会抛出异常

    # 验证通过，执行绑定
    await db.bind_uid(user_id, uid_to_bind)
    await wws_bind.finish(f"UID: {uid_to_bind} 绑定成功！")
  except Exception as e:
    logger.exception("绑定UID失败")
    await wws_bind.finish(f"绑定失败，UID可能无效或API出错。错误：{e}")