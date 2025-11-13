# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/handlers/abyss.py

import asyncio
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageEvent, Bot
from nonebot.matcher import Matcher
from nonebot.log import logger

from ..services.user_service import user_service
from ..services.game_service import GameService
from ..core.drawing.abyss_card import draw_tower_card, draw_challenge_card, draw_slash_card
from ..core.utils.image import pil_to_img_msg

# --- 初始化服务 ---
from ..core.api.waves_api import waves_api

game_service = GameService()
# --- 服务初始化完成 ---


tower_cmd = on_command("深塔", aliases={"深境之塔", "st"}, priority=10, block=True)
challenge_cmd = on_command("全息", aliases={"全息战略"}, priority=10, block=True)
slash_cmd = on_command("冥海", aliases={"冥歌海墟"}, priority=10, block=True)


@tower_cmd.handle()
async def _(bot: Bot, event: MessageEvent, matcher: Matcher):
  """
  处理 深塔 命令
  (迁移自 wutheringwaves_abyss/__init__.py)
  """
  bind_info = await user_service.get_user_bind(event.user_id)
  if not bind_info:
    await matcher.finish("你尚未绑定账号，请发送【鸣潮登录】进行绑定。")
    return

  await matcher.send(f"正在获取 UID: {bind_info.uid} 的深境之塔数据，请稍候...")

  try:
    # 并发获取用户信息和塔信息
    user_info_task = game_service.get_user_info(bind_info.cookie, bind_info.uid)
    tower_data_task = game_service.get_tower_info(bind_info.cookie, bind_info.uid)

    user_info_data, tower_data = await asyncio.gather(
        user_info_task,
        tower_data_task
    )

    if not user_info_data or not tower_data:
      await matcher.finish("获取数据失败，可能是 Cookie 已失效或 API 暂不可用。")
      return

    if not tower_data.get("towerList"):
      await matcher.finish("获取深塔数据为空，请稍后再试。")
      return

  except Exception as e:
    logger.error(f"Failed to get tower data: {e}")
    await matcher.finish(f"获取数据时发生内部错误：{e}")
    return

  # 绘制图片
  try:
    image = await draw_tower_card(user_info_data, tower_data, event.user_id)

    if image:
      await matcher.finish(pil_to_img_msg(image, format="JPEG"))
    else:
      await matcher.finish("绘制深塔卡片失败。")

  except Exception as e:
    logger.error(f"draw_tower_card failed: {e}")
    await matcher.finish(f"绘制图片时发生内部错误：{e}")


@challenge_cmd.handle()
async def _(bot: Bot, event: MessageEvent, matcher: Matcher):
  """
  处理 全息 命令
  (迁移自 wutheringwaves_abyss/__init__.py)
  """
  bind_info = await user_service.get_user_bind(event.user_id)
  if not bind_info:
    await matcher.finish("你尚未绑定账号，请发送【鸣潮登录】进行绑定。")
    return

  await matcher.send(f"正在获取 UID: {bind_info.uid} 的全息战略数据，请稍候...")

  try:
    user_info_task = game_service.get_user_info(bind_info.cookie, bind_info.uid)
    challenge_data_task = game_service.get_challenge_info(bind_info.cookie, bind_info.uid)

    user_info_data, challenge_data = await asyncio.gather(
        user_info_task,
        challenge_data_task
    )

    if not user_info_data or not challenge_data:
      await matcher.finish("获取数据失败，可能是 Cookie 已失效或 API 暂不可用。")
      return

    if not challenge_data.get("challengeList"):
      await matcher.finish("获取全息战略数据为空，请稍后再试。")
      return

  except Exception as e:
    logger.error(f"Failed to get challenge data: {e}")
    await matcher.finish(f"获取数据时发生内部错误：{e}")
    return

  # 绘制图片
  try:
    image = await draw_challenge_card(user_info_data, challenge_data, event.user_id)

    if image:
      await matcher.finish(pil_to_img_msg(image, format="JPEG"))
    else:
      await matcher.finish("绘制全息战略卡片失败。")

  except Exception as e:
    logger.error(f"draw_challenge_card failed: {e}")
    await matcher.finish(f"绘制图片时发生内部错误：{e}")


@slash_cmd.handle()
async def _(bot: Bot, event: MessageEvent, matcher: Matcher):
  """
  处理 冥海 命令
  (迁移自 wutheringwaves_abyss/__init__.py)
  """
  bind_info = await user_service.get_user_bind(event.user_id)
  if not bind_info:
    await matcher.finish("你尚未绑定账号，请发送【鸣潮登录】进行绑定。")
    return

  await matcher.send(f"正在获取 UID: {bind_info.uid} 的冥歌海墟数据，请稍候...")

  try:
    user_info_task = game_service.get_user_info(bind_info.cookie, bind_info.uid)
    slash_data_task = game_service.get_slash_info(bind_info.cookie, bind_info.uid)

    user_info_data, slash_data = await asyncio.gather(
        user_info_task,
        slash_data_task
    )

    if not user_info_data or not slash_data:
      await matcher.finish("获取数据失败，可能是 Cookie 已失效或 API 暂不可用。")
      return

    if not slash_data.get("slashList"):
      await matcher.finish("获取冥歌海墟数据为空，请稍后再试。")
      return

  except Exception as e:
    logger.error(f"Failed to get slash data: {e}")
    await matcher.finish(f"获取数据时发生内部错误：{e}")
    return

  # 绘制图片
  try:
    image = await draw_slash_card(user_info_data, slash_data, event.user_id)

    if image:
      await matcher.finish(pil_to_img_msg(image, format="JPEG"))
    else:
      await matcher.finish("绘制冥歌海墟卡片失败。")

  except Exception as e:
    logger.error(f"draw_slash_card failed: {e}")
    await matcher.finish(f"绘制图片时发生内部错误：{e}")