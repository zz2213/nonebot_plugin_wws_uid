# wws_native/adapters/__init__.py
import io
from abc import ABC, abstractmethod
from typing import Union
from PIL import Image
from nonebot.matcher import Matcher
from nonebot.adapters import Bot, Event

class MessageAdapter(ABC):
    """
    消息适配器抽象基类，用于隔离不同协议的实现细节。
    """
    def __init__(self, bot: Bot, event: Event, matcher: Matcher):
        self._bot = bot
        self._event = event
        self._matcher = matcher

    @abstractmethod
    def get_user_id(self) -> str:
        """获取用户ID"""
        raise NotImplementedError

    def get_message_text(self) -> str:
        """获取纯文本消息"""
        return self._event.get_plaintext().strip()

    @abstractmethod
    async def reply(self, message: Union[str, Image.Image]):
        """回复消息，支持文本和Pillow图片对象"""
        raise NotImplementedError