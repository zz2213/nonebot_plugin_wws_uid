# wws_native/handlers/__init__.py
from typing import Type
from nonebot.adapters import Bot, Event
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.typing import T_State

from ..adapters import MessageAdapter
from ..adapters.onebot_v11 import OneBotV11Adapter
from ..adapters.onebot_v12 import OneBotV12Adapter # 预留

# 协议名称到适配器类的映射
ADAPTER_MAP: dict[str, Type[MessageAdapter]] = {
    "OneBot V11": OneBotV11Adapter,
    # "OneBot V12": OneBotV12Adapter,
}

def create_adapter(bot: Bot, event: Event, matcher: Matcher) -> MessageAdapter | None:
    """
    [核心工厂函数]
    根据bot, event 和 matcher 创建对应的协议适配器实例。
    """
    adapter_name = bot.adapter.get_name()
    adapter_class = ADAPTER_MAP.get(adapter_name)
    if not adapter_class:
        logger.warning(f"未找到适配器 {adapter_name} 的 MessageAdapter 实现，将跳过此事件。")
        return None
    try:
        # 尝试实例化适配器
        return adapter_class(bot, event, matcher)
    except TypeError:
        # 如果 event 类型不匹配 (例如: OneBotV11Adapter 收到非 MessageEvent)
        return None

# 自动加载所有指令处理器
from . import login
from . import user