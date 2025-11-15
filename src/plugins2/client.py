from __future__ import annotations

import re  # <-- 新增导入
from .protocols import AbstractProtocol
from .sayu_protocol import Message, MessageReceive, MessageSend
# from .sayu_protocol import GsClient # REMOVED
from .gsuid_core_compat import Bot as ShimBot, Event as ShimEvent, COMMAND_HANDLERS  # <-- 新增：导入 shim
from .utils import command_start  # <-- 新增：导入命令前缀

from nonebot import logger
from nonebot.adapters import Bot as NB_Bot  # 区分 NoneBot 的 Bot

# _client: GsClient | None = None # REMOVED
active_protocols: dict[str, AbstractProtocol] = {}
CAST_MAP = {"qqguild": "qq", "qqgroup": "qq"}


# class ClientNotConnected(Exception): # REMOVED
#     pass

# async def start_client(...): # REMOVED
# async def stop_client(): # REMOVED


async def call_bot(msg: MessageSend):
    """
    (保持不变)
    这个函数现在由 gsuid_core_compat.py 中的 ShimBot.send() 间接调用
    """
    # assert _client is not None # REMOVED
    bot_id = CAST_MAP.get(msg.bot_id, msg.bot_id)
    bot_protocol_id = f"{bot_id}--{msg.bot_self_id}"
    protocol = active_protocols.get(bot_protocol_id)
    if protocol is None:
        # if bot_id == _client.bot_id: # MODIFIED
        if bot_id == "NoneBot2":  # 假设 bot_id 曾为 "NoneBot2"
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
    """
    修改后的消息入口：
    不再通过 WebSocket 发送，而是路由到本地核心处理函数。
    """
    # if _client is None: # REMOVED
    #     logger.warning("[GSUID] 客户端已关闭")
    #     raise ClientNotConnected
    # await _client.send(msg) # REMOVED

    # 新增：调用本地命令路由
    await _process_core_message(msg, original_bot)


async def _process_core_message(msg: MessageReceive, original_bot: "NB_Bot"):
    """
    本地核心处理逻辑：命令分发。
    """
    protocol_id = f"{msg.bot_id}--{msg.bot_self_id}"
    protocol = active_protocols.get(protocol_id)
    if protocol is None:
        logger.warning(f"[GSUID-CORE] 未找到协议实例 {protocol_id} 来执行命令。")
        return

    raw_text = ""
    # 提取消息的文本内容
    for segment in msg.content:
        if segment.type == "text":
            raw_text = segment.data
            break

    if not raw_text:
        logger.debug("[GSUID-CORE] 消息不含文本内容，跳过命令分发。")
        return

    # 1. 命令匹配 (使用 nonebot 的 command_start)
    matched_command = None
    final_command_text = raw_text.lstrip()  # 原始命令文本（含参数）

    for start in command_start:
        if final_command_text.startswith(start):
            command_with_args = final_command_text[len(start):].strip()

            # 提取命令词 (e.g., "登录")
            parts = command_with_args.split(maxsplit=1)
            command_name = parts[0] if parts else ""

            if command_name in COMMAND_HANDLERS:
                matched_command = command_name
                final_command_text = command_with_args  # 传递 "登录 123,456"
                break

    if matched_command:
        # 2. 执行命令
        command_func = COMMAND_HANDLERS[matched_command]

        # 实例化 Shim Bot 和 Event
        shim_bot = ShimBot(msg)
        shim_event = ShimEvent(msg, raw_command_text=final_command_text)

        # 为 Bot.send 缺少 ev 参数时提供备用
        setattr(shim_bot, '_shim_event', shim_event)

        logger.info(f"[GSUID-CORE] 匹配到命令: {matched_command} | 执行: {command_func.__name__}")

        try:
            # 执行核心逻辑函数，使用 Shim Bot 和 Event
            await command_func(shim_bot, shim_event)
        except Exception as e:
            logger.exception(f"[GSUID-CORE] 执行命令 {matched_command} 时出错: {e}")
            await shim_bot.send(f"执行命令时发生内部错误: {e}", shim_event)
        return

    logger.debug(f"[GSUID-CORE] 未匹配到 GSUID 命令: {raw_text}")