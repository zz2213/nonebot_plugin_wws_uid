# wws_native/adapters/onebot_v11.py
import io
from typing import Union
from PIL import Image
from nonebot.adapters.onebot.v11 import MessageSegment, MessageEvent
from . import MessageAdapter


class OneBotV11Adapter(MessageAdapter):
  """OneBot v11 协议的适配器实现"""

  def get_user_id(self) -> str:
    # 确保 event 是 MessageEvent 类型
    assert isinstance(self._event, MessageEvent)
    return str(self._event.user_id)

  async def reply(self, message: Union[str, Image.Image]):
    if isinstance(message, str):
      await self._matcher.send(message)
    elif isinstance(message, Image.Image):
      img_bytes = io.BytesIO()
      message.save(img_bytes, format="PNG")
      await self._matcher.send(MessageSegment.image(img_bytes.getvalue()))