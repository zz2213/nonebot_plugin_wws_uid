# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/handlers/gacha.py

import asyncio
from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, MessageEvent, Bot
from nonebot.matcher import Matcher
from nonebot.log import logger

from ..services.user_service import user_service
from ..services.gacha_service import gacha_service
from ..core.drawing.gacha_card import draw_gacha_card
from ..core.utils.image import pil_to_img_msg

import re

# --- 初始化服务 ---
# (gacha_service 已全局实例化)
# ---


gacha_import_cmd = on_command("导入抽卡链接", aliases={"导入抽卡", "ckdx"}, priority=10, block=True)
gacha_log_cmd = on_command("抽卡记录", aliases={"ckjl"}, priority=10, block=True)

# 用于从消息中提取 URL
URL_REGEX = re.compile(r"https?://[^\s]+")


@gacha_import_cmd.handle()
async def _(bot: Bot, event: MessageEvent, matcher: Matcher, args: Message = CommandArg()):
  """
  处理 导入抽卡链接 命令
  (迁移自 wutheringwaves_gachalog/__init__.py)
  """

  # 1. 获取账号信息
  bind_info = await user_service.get_user_bind(event.user_id)
  if not bind_info:
    await matcher.finish("你尚未绑定账号，请发送【鸣潮登录】进行绑定。")
    return

  # 2. 提取 URL
  gacha_url = ""
  text_content = event.get_plaintext()
  match = URL_REGEX.search(text_content)
  if match:
    gacha_url = match.group(0)

  if not gacha_url:
    await matcher.finish("未在您的消息中找到抽卡链接。")
    return

  await matcher.send("检测到抽卡链接，正在开始导入... \n这可能需要 1-2 分钟，请耐心等待，期间请勿重复触发。")

  # 3. 调用 Service 更新
  try:
    result_msg = await gacha_service.update_gacha_logs(
        str(event.user_id),
        gacha_url
    )
    await matcher.finish(result_msg)

  except Exception as e:
    logger.error(f"update_gacha_logs failed: {e}")
    await matcher.finish(f"导入时发生内部错误：{e}")


@gacha_log_cmd.handle()
async def _(bot: Bot, event: MessageEvent, matcher: Matcher):
  """
  处理 抽卡记录 命令
  (迁移自 wutheringwaves_gachalog/__init__.py)
  """

  # 1. 获取账号信息
  bind_info = await user_service.get_user_bind(event.user_id)
  if not bind_info:
    await matcher.finish("你尚未绑定账号，请发送【鸣潮登录】进行绑定。")
    return

  await matcher.send(f"正在查询 UID: {bind_info.uid} 的抽卡记录，请稍候...")

  # 2. 调用 Service 获取统计数据
  try:
    summary_data = await gacha_service.get_gacha_summary(
        str(event.user_id),
        bind_info.uid
    )

    if not summary_data or summary_data.get("total", 0) == 0:
      await matcher.finish("未查询到您的抽卡记录，请先发送【导入抽卡链接】+ [您的抽卡URL] 进行导入。")
      return

  except Exception as e:
    logger.error(f"get_gacha_summary failed: {e}")
    await matcher.finish(f"获取数据时发生内部错误：{e}")
    return

  # 3. 调用 Drawing 绘制图片
  try:
    image = await draw_gacha_card(summary_data, event.user_id)

    if image:
      await matcher.finish(pil_to_img_msg(image, format="JPEG"))
    else:
      await matcher.finish("绘制抽卡记录图失败。")

  except Exception as e:
    logger.error(f"draw_gacha_card failed: {e}")
    await matcher.finish(f"绘制图片时发生内部错误：{e}")