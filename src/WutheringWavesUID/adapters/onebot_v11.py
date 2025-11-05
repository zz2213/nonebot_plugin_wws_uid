from nonebot.adapters.onebot.v11 import MessageSegment


class OneBotV11Adapter:
  """OneBot V11适配器"""

  @staticmethod
  def image(path: str) -> MessageSegment:
    """图片消息段"""
    return MessageSegment.image(f"file:///{path}")

  @staticmethod
  def node(messages: list) -> MessageSegment:
    """转发消息节点"""
    # 简化实现，实际可能需要更复杂的处理
    return MessageSegment.node(messages)