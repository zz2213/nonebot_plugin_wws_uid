from nonebot.adapters.onebot.v12 import MessageSegment


class OneBotV12Adapter:
  """OneBot V12适配器"""

  @staticmethod
  def image(path: str) -> MessageSegment:
    """图片消息段"""
    return MessageSegment.image(path)

  @staticmethod
  def node(messages: list) -> MessageSegment:
    """转发消息节点"""
    # 简化实现
    return messages[0] if messages else MessageSegment.text("")