from __future__ import annotations

import importlib
from pathlib import Path
from pkgutil import iter_modules

from .client import (
    active_protocols,
    send_message,
)
from  config import Config
from .protocols import PROTOCOLS
from . import gsuid_core_compat  # <-- 新增：导入兼容层
from . import wutheringwaves_login  # <-- 新增：导入插件，触发命令注册

from nonebot import get_driver, get_plugin_config, on, on_message, on_notice, get_app, logger
from nonebot.adapters import Bot, Event
from nonebot.matcher import Matcher
from nonebot.plugin import PluginMetadata
from nonebot.typing import T_State

# ----------------------------------------------------------------
# 导入并注册 Web 路由
# ----------------------------------------------------------------
try:
    from .wutheringwaves_login.login import (
        waves_login_index,
        waves_login,
        LoginModel
    )

    app = get_app()
    app.get("/waves/i/{auth}")(waves_login_index)
    app.post("/waves/login")(waves_login)
except ImportError as e:
    print(f"无法导入 Web 路由: {e}")
except Exception as e:
    print(f"注册 Web 路由失败: {e}")
# ----------------------------------------------------------------


__plugin_meta__ = PluginMetadata(
    name="GenshinUID",
    description="支持大部分适配器的全功能NoneBot2原神插件",
    usage="{插件用法}",
    type="application",
    homepage="[https://github.com/Genshin-bots/nonebot-plugin-genshinuid](https://github.com/Genshin-bots/nonebot-plugin-genshinuid)",
    config=Config,
    supported_adapters={
        "~onebot.v11",
        "~dodo",
        "~kaiheila",
        "~villa",
        "~telegram",
        "~discord",
        "~qq",
        "~feishu",
        "~red",
        "~ntchat",
        "~onebot.v12",
    },
)

get_message = on_message(priority=999, state={"gsuid_type": "message"})
get_notice = on_notice(priority=999, state={"gsuid_type": "notice"})
get_tn = on("inline", state={"gsuid_type": "notice"})

driver = get_driver()
config = get_plugin_config(Config)

for module_info in iter_modules([str(Path(__file__).parent / "protocols")]):
    if module_info.name.startswith("_"):
        continue
    module_name = f"GenshinUID.protocols.{module_info.name}"
    importlib.import_module(module_name)

ADAPTER_TO_PROTOCOL = {
    "OneBot V11": "onebot",
    "OneBot V12": "onebot_v12",
    "DoDo": "dodo",
    "Kaiheila": "kaiheila",
    "Villa": "villa",
    "Telegram": "telegram",
    "Discord": "discord",
    "Feishu": "feishu",
    "RedProtocol": "onebot:red",
    "ntchat": "ntchat",
    "QQ": "qq",
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