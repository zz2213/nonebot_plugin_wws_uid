import io
from typing import Union
from PIL import Image
from nonebot.adapters.onebot.v11 import MessageSegment, MessageEvent, Message
from . import MessageAdapter


class OneBotV11Adapter(MessageAdapter):
  """OneBot v11 协议的适配器实现"""

  def __init__(self, bot, event, matcher):
    if not isinstance(event, MessageEvent):
      raise TypeError("OneBotV11Adapter 必须接收 MessageEvent")
    super().__init__(bot, event, matcher)
    self._event: MessageEvent = event

  def get_user_id(self) -> str:
    return str(self._event.user_id)

  def get_group_id(self) -> str | None:
    return str(self._event.group_id) if hasattr(self._event, "group_id") else None

  async def reply(self, message: Union[str, Image.Image, MessageSegment]):
    if isinstance(message, str):
      await self._matcher.send(message)
    elif isinstance(message, Image.Image):
      img_bytes = io.BytesIO()
      message.save(img_bytes, format="PNG")
      await self._matcher.send(MessageSegment.image(img_bytes.getvalue()))
    elif isinstance(message, MessageSegment):
      await self._matcher.send(Message(message))