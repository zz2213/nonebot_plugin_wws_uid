from __future__ import annotations

import re
from .adapters import AbstractProtocol
from .entity import Message, MessageReceive, MessageSend
from .gsuid_core_compat import (
    Bot as ShimBot,
    Event as ShimEvent,
    shim_command_handler  # <-- 导入新的 Handler
)
from .utils import command_start  # 导入 nonebot 的命令前缀

from nonebot import logger
from nonebot.adapters import Bot as NB_Bot  # 区分 NoneBot 的 Bot

active_protocols: dict[str, AbstractProtocol] = {}
CAST_MAP = {"qqguild": "qq", "qqgroup": "qq"}


async def call_bot(msg: MessageSend):
    """
    (保持不变)
    这个函数现在由 gsuid_core_compat.py 中的 ShimBot.send() 间接调用
    """
    bot_id = CAST_MAP.get(msg.bot_id, msg.bot_id)
    bot_protocol_id = f"{bot_id}--{msg.bot_self_id}"
    protocol = active_protocols.get(bot_protocol_id)
    if protocol is None:
        if bot_id == "NoneBot2":
            if msg.content:
                _data = msg.content[0]
                if _data.type and _data.type.startswith("log"):
                    _type = _data.type.split("_")[-1].lower()
                    getattr(logger, _type)(_data.data)
        else:
            logger.warning(f"[GSUID] 机器人 {bot_protocol_id} 未找到")
        return
    if msg.content is None or msg.target_id is None or msg.target_type is None:
        return
    await protocol.send_message(msg.content, msg.target_id, msg.target_type)


async def send_message(msg: MessageReceive, original_bot: "NB_Bot"):
    logger.info("转发到适配器处理消息")

    await _process_core_message(msg, original_bot)


async def _process_core_message(msg: MessageReceive, original_bot: "NB_Bot"):
    """
    本地核心处理逻辑：
    将 MessageReceive 包装为 ShimBot 和 ShimEvent，
    并交给 gsuid_core_compat.shim_command_handler 处理。
    """

    # 修正：我们需要传递 *包含* 前缀的原始文本
    # onebot_v11.py 协议适配层已经剥离了 command_start
    # 我们必须在 shim_command_handler 中处理剥离逻辑
    # 因此，我们需要获取 *原始* 文本

    # MessageReceive 包含 content: List[Message]
    # 我们需要将 List[Message] 转换为 gsuid_core 期望的 ev.text (str)

    raw_text = ""
    for segment in msg.content:
        if segment.type == "text":
            raw_text += str(segment.data)

    # 1. 实例化 Shim Bot 和 Event
    # ev.text 将被 handler 内部覆盖，这里传入原始文本
    shim_bot = ShimBot(msg)
    shim_event = ShimEvent(msg, raw_command_text=raw_text)

    # 2. 为 Bot.send 缺少 ev 参数时提供备用
    setattr(shim_bot, '_shim_event', shim_event)

    # 3. 调用 GSUID Core 模拟处理器
    try:
        await shim_command_handler(shim_bot, shim_event)
    except Exception as e:
        logger.exception(f"[GSUID-CORE] 命令处理器顶层出错: {e}")
        try:
            await shim_bot.send(f"命令处理器发生严重错误: {e}", shim_event)
        except Exception:
            pass