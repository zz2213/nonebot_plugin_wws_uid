# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/handlers/explore.py

import asyncio
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageEvent, Bot
from nonebot.matcher import Matcher
from nonebot.log import logger

from ..services.user_service import user_service
# 导入我们已更新的 GameService
from ..services.game_service import GameService
# 导入我们刚创建的绘图函数
from ..core.drawing.explore_card import draw_explore_card
from ..core.utils.image import pil_to_img_msg

# --- 初始化服务 ---
from ..core.api.waves_api import waves_api

game_service = GameService()
# --- 服务初始化完成 ---


explore_cmd = on_command("探索度", aliases={"tsd"}, priority=10, block=True)


@explore_cmd.handle()
async def _(bot: Bot, event: MessageEvent, matcher: Matcher):
  """
  处理 探索度 命令
  (迁移自 wutheringwaves_explore/__init__.py)
  """

  # 1. 获取账号信息
  bind_info = await user_service.get_user_bind(event.user_id)
  if not bind_info:
    await matcher.finish("你尚未绑定账号，请发送【鸣潮登录】进行绑定。")
    return

  await matcher.send(f"正在获取 UID: {bind_info.uid} 的探索度数据，请稍候...")

  # 2. 调用 Service 获取数据 (并发)
  try:
    # 探索度信息在 get_explore_info, 昵称/UID 在 get_user_info
    user_info_task = game_service.get_user_info(bind_info.cookie, bind_info.uid)
    explore_data_task = game_service.get_explore_info(bind_info.cookie, bind_info.uid)

    user_info_data, explore_data = await asyncio.gather(
        user_info_task,
        explore_data_task
    )

    if not user_info_data or not explore_data:
      await matcher.finish("获取数据失败，可能是 Cookie 已失效或 API 暂不可用。")
      return

    if not explore_data.get("exploreList"):
      await matcher.finish("获取探索度数据为空，请稍后再试。")
      return

  except Exception as e:
    logger.error(f"Failed to get explore data: {e}")
    await matcher.finish(f"获取数据时发生内部错误：{e}")
    return

  # 3. 调用 Drawing 绘制图片
  try:
    # user_id 用于绘制 QQ 头像
    image = await draw_explore_card(user_info_data, explore_data, event.user_id)

    if image:
      await matcher.finish(pil_to_img_msg(image, format="JPEG"))
    else:
      await matcher.finish("绘制探索度卡片失败。")

  except Exception as e:
    logger.error(f"draw_explore_card failed: {e}")
    await matcher.finish(f"绘制图片时发生内部错误：{e}")
    return