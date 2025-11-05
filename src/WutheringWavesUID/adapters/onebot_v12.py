# (这是一个为未来支持 OneBot v12 预留的框架)
import io
from typing import Union
from PIL import Image
from nonebot.adapters import Bot, Event
from nonebot.matcher import Matcher
# from nonebot.adapters.onebot.v12 import MessageSegment, MessageEvent, Message
from . import MessageAdapter


class OneBotV12Adapter(MessageAdapter):
  """OneBot v12 协议的适配器实现 (待完成)"""

  def __init__(self, bot: Bot, event: Event, matcher: Matcher):
    # if not isinstance(event, MessageEvent):
    #     raise TypeError("OneBotV12Adapter 必须接收 MessageEvent")
    super().__init__(bot, event, matcher)
    # self._event: MessageEvent = event

  def get_user_id(self) -> str:
    # return str(self._event.user_id)
    raise NotImplementedError("OneBot v12 适配器尚未实现")

  def get_group_id(self) -> str | None:
    # return str(self._event.group_id) if hasattr(self._event, "group_id") else None
    raise NotImplementedError("OneBot v12 适配器尚未实现")

  async def reply(self, message: Union[str, Image.Image, "MessageSegment"]):
    # ... (v12 的实现)
    raise NotImplementedError("OneBot v12 适配器尚未实现")