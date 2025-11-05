import asyncio
import hashlib
import uuid
from pathlib import Path
from typing import Union, Tuple
from async_timeout import timeout

from nonebot import get_driver
from nonebot.adapters import Bot, Event
from nonebot.adapters.onebot.v11 import MessageSegment

from ..config import plugin_config
from ..models import WwsUser
from ..database import create_or_update_user, bind_uid
from ..core_logic.resource import get_template

game_title = "[鸣潮]"


def get_token(user_id: str) -> str:
  """生成用户token"""
  return hashlib.sha256(user_id.encode()).hexdigest()[:8]


async def get_url() -> Tuple[str, bool]:
  """获取登录URL"""
  if plugin_config.WAVES_LOGIN_URL:
    url = plugin_config.WAVES_LOGIN_URL
    if not url.startswith("http"):
      url = f"https://{url}"
    return url, plugin_config.WAVES_LOGIN_URL_SELF
  else:
    host = plugin_config.HOST
    port = plugin_config.PORT

    if host in ["localhost", "127.0.0.1"]:
      _host = "localhost"
    else:
      _host = host  # 简化处理

    return f"http://{_host}:{port}", True


async def send_login(bot: Bot, event: Event, url: str):
  """发送登录消息"""
  user_id = str(getattr(event, 'user_id', ''))
  group_id = str(getattr(event, 'group_id', ''))
  at_sender = bool(group_id)

  if plugin_config.WAVES_QR_LOGIN:
    # 二维码登录逻辑
    path = Path(__file__).parent.parent / f"{user_id}.gif"

    # 简化实现，实际需要生成二维码
    im = [
      f"{game_title} 您的id为【{user_id}】\n",
      "请扫描下方二维码获取登录地址，并复制地址到浏览器打开\n",
      MessageSegment.text("二维码功能待实现")
    ]

    if plugin_config.WAVES_LOGIN_FORWARD:
      await bot.send(event, MessageSegment.node(im))
    else:
      await bot.send(event, "".join(im), at_sender=at_sender)
  else:
    # 链接登录
    if plugin_config.WAVES_TENCENT_WORD:
      url = f"https://docs.qq.com/scenario/link.html?url={url}"

    im = [
      f"{game_title} 您的id为【{user_id}】",
      "请复制地址到浏览器打开",
      f" {url}",
      "登录地址10分钟内有效",
    ]

    if plugin_config.WAVES_LOGIN_FORWARD:
      await bot.send(event, MessageSegment.node(im))
    else:
      await bot.send(event, "\n".join(im), at_sender=at_sender)


async def page_login_local(bot: Bot, event: Event, url: str):
  """本地页面登录"""
  user_id = str(getattr(event, 'user_id', ''))
  group_id = str(getattr(event, 'group_id', ''))
  at_sender = bool(group_id)

  user_token = get_token(user_id)
  await send_login(bot, event, f"{url}/waves/i/{user_token}")

  # 缓存处理逻辑
  data = {"mobile": -1, "code": -1, "user_id": user_id}
  from .cache import cache
  cache.set(user_token, data)

  try:
    async with timeout(600):
      while True:
        result = cache.get(user_token)
        if result is None:
          return await bot.send(event, "登录超时!", at_sender=at_sender)
        if result.get("mobile") != -1 and result.get("code") != -1:
          text = f"{result['mobile']},{result['code']}"
          cache.delete(user_token)
          break
        await asyncio.sleep(1)
  except asyncio.TimeoutError:
    return await bot.send(event, "登录超时!", at_sender=at_sender)

  # 调用验证码登录
  from ..handlers.login import code_login
  return await code_login(bot, event, text, True)


async def page_login_other(bot: Bot, event: Event, url: str):
  """外部页面登录"""
  # 简化实现
  await bot.send(event, "外部登录页面功能待实现")


async def add_cookie(event: Event, token: str, did: str) -> Union[WwsUser, str, None]:
  """添加cookie并绑定用户"""
  user_id = str(getattr(event, 'user_id', ''))
  bot_id = event.get_type()
  group_id = str(getattr(event, 'group_id', ''))

  try:
    # 创建用户
    user = await create_or_update_user(
        user_id=user_id,
        bot_id=bot_id,
        uid="123456789",  # 这里应该从API获取实际UID
        cookie=token,
        did=did
    )

    # 绑定UID
    await bind_uid(
        user_id=user_id,
        bot_id=bot_id,
        uid=user.uid,
        group_id=group_id
    )

    return user
  except Exception as e:
    return f"登录失败: {str(e)}"


async def login_success_msg(bot: Bot, event: Event, user: WwsUser):
  """登录成功消息"""
  await bot.send(event, f"{game_title} 登录成功！UID: {user.uid}")