import asyncio
import hashlib
import re
import uuid
from pathlib import Path
from typing import Union

from nonebot import on_command
from nonebot.adapters import Bot, Event
from nonebot.params import CommandArg
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import Message

from ..core_logic.api import waves_api
from ..core_logic.models import APIResponse
from ..utils.cache import TimedCache
from ..utils.login_helpers import (
  get_url, get_token, send_login, page_login_local,
  page_login_other, add_cookie, login_success_msg
)

# 缓存
cache = TimedCache(timeout=600, maxsize=10)

game_title = "[鸣潮]"
msg_error = "[鸣潮] 登录失败\n1.是否注册过库街区\n2.库街区能否查询当前鸣潮特征码数据\n"

# 登录命令
login_cmd = on_command("鸣潮登录", aliases={"waves登录", "鸣潮login"}, priority=5)


@login_cmd.handle()
async def handle_login(bot: Bot, event: Event):
  """处理登录命令"""
  await page_login(bot, event)


# 验证码登录命令
code_login_cmd = on_command("鸣潮验证码登录", aliases={"waves验证码登录"}, priority=5)


@code_login_cmd.handle()
async def handle_code_login(bot: Bot, event: Event, args: Message = CommandArg()):
  """处理验证码登录"""
  text = args.extract_plain_text().strip()
  if text:
    await code_login(bot, event, text)


async def page_login(bot: Bot, event: Event):
  """页面登录处理"""
  url, is_local = await get_url()

  if is_local:
    await page_login_local(bot, event, url)
  else:
    await page_login_other(bot, event, url)


async def code_login(bot: Bot, event: Event, text: str, isPage: bool = False):
  """验证码登录处理"""
  # 手机+验证码
  try:
    phone_number, code = text.split(",")
    if not is_valid_chinese_phone_number(phone_number):
      raise ValueError("Invalid phone number")
  except ValueError:
    await bot.send(
        event,
        f"{game_title} 手机号+验证码登录失败\n\n请参照以下格式:\n鸣潮登录 手机号,验证码\n"
    )
    return

  did = str(uuid.uuid4()).upper()
  result = await waves_api.login(phone_number, code, did)

  if not result.get("success", False):
    return await bot.send(event, msg_error)

  if not result.get("data") or not isinstance(result["data"], dict):
    return await bot.send(event, "登录失败: 响应数据格式错误")

  token = result["data"].get("token", "")
  waves_user = await add_cookie(event, token, did)

  if waves_user and isinstance(waves_user, WwsUser):
    return await login_success_msg(bot, event, waves_user)
  else:
    if isinstance(waves_user, str):
      return await bot.send(event, waves_user)
    else:
      return await bot.send(event, msg_error)


def is_valid_chinese_phone_number(phone_number: str) -> bool:
  """验证手机号格式"""
  pattern = re.compile(r"^1[3-9]\d{9}$")
  return pattern.match(phone_number) is not None