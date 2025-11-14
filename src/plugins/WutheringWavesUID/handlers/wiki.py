# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/handlers/wiki.py

import asyncio
from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, MessageEvent, Bot, MessageSegment
from nonebot.matcher import Matcher
from nonebot.log import logger

# 导入我们刚创建的服务实例
from ..services.wiki_service import wiki_service
# 导入我们刚创建的绘图函数
from ..core.drawing.wiki_card import (
  draw_char_wiki_card, draw_weapon_wiki_card, draw_echo_wiki_card
)
from ..core.utils.image import pil_to_img_msg
from ..api.client import api_client  # 用于下载攻略图

# --- 角色ID 临时 hardcode ---
# TODO: 后续应替换为调用 AliasService
role_name_map = {
  "忌炎": "忌炎", "吟霖": "吟霖", "卡卡罗": "卡卡罗", "维里奈": "维里奈", "安可": "安可",
  "鉴心": "鉴心", "凌阳": "凌阳", "散华": "散华", "丹瑾": "丹瑾", "莫特斐": "莫特斐",
  "秧秧": "秧秧", "白芷": "白芷", "炽霞": "炽霞", "渊武": "渊武", "桃祈": "桃祈",
  "漂泊者": "漂泊者·衍射", "光主": "漂泊者·衍射", "暗主": "漂泊者·湮灭", "长离": "长离",
}
# ---

char_wiki_cmd = on_command("角色图鉴", aliases={"jstd"}, priority=10, block=True)
weapon_wiki_cmd = on_command("武器图鉴", aliases={"wqtd"}, priority=10, block=True)
echo_wiki_cmd = on_command("声骸图鉴", aliases={"shtd"}, priority=10, block=True)
guide_cmd = on_command("攻略", aliases={"gl"}, priority=10, block=True)


@char_wiki_cmd.handle()
async def _(matcher: Matcher, args: Message = CommandArg()):
  """
  处理 角色图鉴 命令
  (迁移自 wutheringwaves_wiki/__init__.py)
  """
  name = args.extract_plain_text().strip()
  if not name:
    await matcher.finish("请输入要查询的角色名，例如：角色图鉴 忌炎")
    return

  # TODO: 替换为 AliasService
  std_name = role_name_map.get(name, name)

  await matcher.send(f"正在查询角色「{std_name}」的图鉴资料...")

  try:
    data = await wiki_service.get_char_wiki_data(std_name)
    if not data:
      await matcher.finish(f"未查询到角色「{std_name}」的图鉴资料。")
      return

    image = await draw_char_wiki_card(data)
    if image:
      await matcher.finish(pil_to_img_msg(image, format="JPEG"))
    else:
      await matcher.finish("绘制角色图鉴失败。")

  except Exception as e:
    logger.error(f"char_wiki_cmd failed: {e}")
    await matcher.finish(f"查询时发生内部错误：{e}")


@weapon_wiki_cmd.handle()
async def _(matcher: Matcher, args: Message = CommandArg()):
  """
  处理 武器图鉴 命令
  (迁移自 wutheringwaves_wiki/__init__.py)
  """
  name = args.extract_plain_text().strip()
  if not name:
    await matcher.finish("请输入要查询的武器名，例如：武器图鉴 停驻之烟")
    return

  await matcher.send(f"正在查询武器「{name}」的图鉴资料...")

  try:
    # TODO: 武器名需要 AliasService
    data = await wiki_service.get_weapon_wiki_data(name)
    if not data:
      await matcher.finish(f"未查询到武器「{name}」的图鉴资料，请确保输入了标准全称。")
      return

    image = await draw_weapon_wiki_card(data)
    if image:
      await matcher.finish(pil_to_img_msg(image, format="JPEG"))
    else:
      await matcher.finish("绘制武器图鉴失败。")

  except Exception as e:
    logger.error(f"weapon_wiki_cmd failed: {e}")
    await matcher.finish(f"查询时发生内部错误：{e}")


@echo_wiki_cmd.handle()
async def _(matcher: Matcher, args: Message = CommandArg()):
  """
  处理 声骸图鉴 命令
  (迁移自 wutheringwaves_wiki/__init__.py)
  """
  name = args.extract_plain_text().strip()
  if not name:
    await matcher.finish("请输入要查询的声骸或套装名，例如：声骸图鉴 不绝余音")
    return

  await matcher.send(f"正在查询「{name}」的图鉴资料...")

  try:
    # TODO: 声骸/套装名需要 AliasService
    data = await wiki_service.get_echo_wiki_data(name)
    if not data:
      await matcher.finish(f"未查询到「{name}」的图鉴资料，请确保输入了标准全称。")
      return

    image = await draw_echo_wiki_card(data)
    if image:
      await matcher.finish(pil_to_img_msg(image, format="JPEG"))
    else:
      await matcher.finish("绘制声骸图鉴失败。")

  except Exception as e:
    logger.error(f"echo_wiki_cmd failed: {e}")
    await matcher.finish(f"查询时发生内部错误：{e}")


@guide_cmd.handle()
async def _(matcher: Matcher, args: Message = CommandArg()):
  """
  处理 攻略 命令
  (迁移自 wutheringwaves_wiki/guide.py)
  """
  name = args.extract_plain_text().strip()
  if not name:
    await matcher.finish("请输入要查询攻略的角色名，例如：攻略 忌炎")
    return

  # TODO: 替换为 AliasService
  std_name = role_name_map.get(name, name)

  await matcher.send(f"正在查找「{std_name}」的攻略图，请稍候...")

  try:
    image_urls = await wiki_service.get_guide_images(std_name)
    if not image_urls:
      await matcher.finish(f"未找到「{std_name}」的攻略图。")
      return

    # 仅发送第一张攻略图
    img_url = image_urls[0]
    resp = await api_client.get(img_url)
    resp.raise_for_status()

    await matcher.finish(MessageSegment.image(resp.content))

  except Exception as e:
    logger.error(f"guide_cmd failed: {e}")
    await matcher.finish(f"获取攻略图时发生内部错误：{e}")