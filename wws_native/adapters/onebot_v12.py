# wws_native/adapters/onebot_v12.py
# 这是一个为未来支持 OneBot v12 预留的文件
import io
from typing import Union
from PIL import Image
# from nonebot.adapters.onebot.v12 import MessageSegment, MessageEvent # 未来需要时取消注释
from . import MessageAdapter

class OneBotV12Adapter(MessageAdapter):
    """OneBot v12 协议的适配器实现 (待完成)"""

    def get_user_id(self) -> str:
        # assert isinstance(self._event, MessageEvent) # 未来需要时取消注释
        # return str(self._event.user.id)
        pass

    async def reply(self, message: Union[str, Image.Image]):
        # if isinstance(message, str):
        #     await self._matcher.send(message)
        # elif isinstance(message, Image.Image):
        #     img_bytes = io.BytesIO()
        #     message.save(img_bytes, format="PNG")
        #     await self._matcher.send(MessageSegment.image(img_bytes.getvalue()))
        pass