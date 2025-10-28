# wws_native/handlers/__init__.py
from typing import Type
from nonebot.adapters import Bot

from ..adapters import MessageAdapter
from ..adapters.onebot_v11 import OneBotV11Adapter
from ..adapters.onebot_v12 import OneBotV12Adapter

# 协议名称到适配器类的映射
ADAPTER_MAP: dict[str, Type[MessageAdapter]] = {
    "OneBot V11": OneBotV11Adapter,
    "OneBot V12": OneBotV12Adapter, # 预留
}

def get_adapter(bot: Bot) -> Type[MessageAdapter] | None:
    """根据bot对象获取对应的适配器类"""
    return ADAPTER_MAP.get(bot.adapter.get_name())

# 自动加载所有指令处理器
from . import help
from . import bind
from . import char_info
from . import char_list