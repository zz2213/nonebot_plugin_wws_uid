from nonebot.plugin import PluginMetadata
from nonebot import get_driver

from .config import Config
from . import handlers
from . import web_routes

__plugin_meta__ = PluginMetadata(
    name="鸣潮原生插件",
    description="完整迁移自 WutheringWavesUID 的全功能鸣潮机器人",
    usage="发送 [鸣潮帮助] 查看指令",
    type="application",
    homepage="https://github.com/zz2213/nonebot_plugin_wws_uid",
    config=Config
)

global_config = get_driver().config
plugin_config = Config(**global_config.dict())