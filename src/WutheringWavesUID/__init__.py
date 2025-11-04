from __future__ import annotations

import importlib
from pathlib import Path
from pkgutil import iter_modules

from .client import (
    ClientNotConnected,
    active_protocols,
    send_message,
    start_client,
    stop_client,
)
from .config import Config
from .protocols import PROTOCOLS

from nonebot import  get_plugin_config, on, on_message, on_notice
from nonebot.adapters import Bot, Event
from nonebot.matcher import Matcher
from nonebot.plugin import PluginMetadata
from nonebot.typing import T_State

__plugin_meta__ = PluginMetadata(
    name="WutheringWavesUID",
    description="支持鸣潮查询的插件",
    usage="{插件用法}",
    type="application",
    homepage="https://github.com/Genshin-bots/nonebot-plugin-genshinuid",
    config=Config,
    supported_adapters={
        "~onebot.v11",
    },
)

get_message = on_message(priority=999, state={"gsuid_type": "message"})
get_notice = on_notice(priority=999, state={"gsuid_type": "notice"})
get_tn = on("inline", state={"gsuid_type": "notice"})

config = get_plugin_config(Config)

for module_info in iter_modules([str(Path(__file__).parent / "protocols")]):
    if module_info.name.startswith("_"):
        continue
    module_name = f"GenshinUID.protocols.{module_info.name}"
    importlib.import_module(module_name)

ADAPTER_TO_PROTOCOL = {
    "OneBot V11": "onebot",
}



@get_tn.handle()
@get_notice.handle()
@get_message.handle()
async def handle_notice(
    bot: Bot, event: Event, matcher: Matcher, state: T_State
):
    protocol = active_protocols.get(
        f"{ADAPTER_TO_PROTOCOL[bot.adapter.get_name()]}--{bot.self_id}"
    )
    if protocol is None:
        await matcher.finish()
    message_receive = await getattr(protocol, f"handle_{state['gsuid_type']}")(
        event
    )
    await protocol.handle_send(message_receive)
