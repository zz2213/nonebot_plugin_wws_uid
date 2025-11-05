import io
import re
import asyncio
from abc import ABC, abstractmethod
from typing import Union
from PIL import Image
from nonebot.matcher import Matcher
from nonebot.adapters import Bot, Event
from nonebot.exception import PausedException, FinishedException


class MessageAdapter(ABC):
  """
  消息适配器抽象基类
  用于隔离不同协议的实现细节，实现依赖倒置。
  """

  def __init__(self, bot: Bot, event: Event, matcher: Matcher):
    self._bot = bot
    self._event = event
    self._matcher = matcher

  @abstractmethod
  def get_user_id(self) -> str:
    """获取用户ID"""
    raise NotImplementedError

  @abstractmethod
  def get_group_id(self) -> str | None:
    """获取群组ID，如果是私聊则返回None"""
    raise NotImplementedError

  def get_raw_text(self) -> str:
    """获取原始纯文本消息"""
    return self._event.get_plaintext().strip()

  @abstractmethod
  async def reply(self, message: Union[str, Image.Image, "MessageSegment"]):
    """回复消息，支持文本、Pillow图片和平台原生的MessageSegment"""
    raise NotImplementedError

  async def wait_for_message(self, timeout: int = 120, regex: str = r"^\d{6}$") -> str | None:
    """
    [原生实现] 模拟 gsuid_core 的 sv.wait_for()
    等待用户在指定时间内回复一条符合正则表达式的消息。
    """
    try:
      # 关键：使用 matcher.receive() 来等待下一次事件
      event = await self._matcher.receive(timeout=timeout)
      text = event.get_plaintext().strip()

      if re.match(regex, text):
        return text
      else:
        await self.reply("输入格式不正确，请重新操作。")
        await FinishedException()  # 结束当前交互
        return None
    except asyncio.TimeoutError:
      await self.reply("输入超时，请重新操作。")
      await FinishedException()  # 结束当前交互
      return None
    except PausedException:
      # 这不应该发生，但作为保险
      await self.reply("会话暂停，请重新操作。")
      await FinishedException()  # 结束当前交互
      return None