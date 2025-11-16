from __future__ import annotations

import importlib
from pathlib import Path
from pkgutil import iter_modules

from .client import (
    active_protocols,
    send_message,
)
from .config import Config
from .adapters import PROTOCOLS
from . import gsuid_core_compat
from . import wutheringwaves_login

from nonebot import get_driver, get_plugin_config, on, on_message, on_notice, logger
from nonebot.adapters import Bot, Event
from nonebot.matcher import Matcher
from nonebot.plugin import PluginMetadata
from nonebot.typing import T_State


__plugin_meta__ = PluginMetadata(
    name="WutheringWavesUID",
    description="支持大部分适配器的全功能NoneBot2原神插件",
    usage="{插件用法}",
    type="application",
    homepage="https://github.com/Zyone2/nonebot_plugin_wutheringwavesuid",
    config=Config,
    supported_adapters={
        "~onebot.v11",
    },
)

get_message = on_message(priority=999, state={"gsuid_type": "message"})
get_notice = on_notice(priority=999, state={"gsuid_type": "notice"})
get_tn = on("inline", state={"gsuid_type": "notice"})

driver = get_driver()
config = get_plugin_config(Config)

for module_info in iter_modules([str(Path(__file__).parent / "adapters")]):
    if module_info.name.startswith("_"):
        continue
    module_name = f".adapters.{module_info.name}"
    importlib.import_module(module_name, package=__name__)

ADAPTER_TO_PROTOCOL = {
    "OneBot V11": "onebot",
}



@driver.on_bot_connect
async def _(bot: Bot):
    protocol_name = ADAPTER_TO_PROTOCOL[bot.adapter.get_name()]
    protocol = PROTOCOLS[protocol_name](bot)
    active_protocols[f"{protocol_name}--{bot.self_id}"] = protocol


@driver.on_bot_disconnect
async def _(bot: Bot):
    active_protocols.pop(
        f"{ADAPTER_TO_PROTOCOL[bot.adapter.get_name()]}--{bot.self_id}", None
    )


@get_tn.handle()
@get_notice.handle()
@get_message.handle()
async def handle_notice(
        bot: Bot, event: Event, matcher: Matcher, state: T_State
):
    logger.info("处理nonebot接收到的原始消息")
    protocol = active_protocols.get(
        f"{ADAPTER_TO_PROTOCOL[bot.adapter.get_name()]}--{bot.self_id}"
    )
    if protocol is None:
        await matcher.finish()
    message_receive = await getattr(protocol, f"handle_{state['gsuid_type']}")(
        event
    )
    if message_receive is None:
        await matcher.finish()

    # MODIFIED: 传入原始 bot 实例
    try:
        await send_message(message_receive, bot)
        # except ClientNotConnected: # REMOVED
    except Exception as e:
        logger.exception(f"处理 GSUID 消息时出错: {e}")

    await matcher.finish()