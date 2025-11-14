# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/__init__.py

from nonebot.plugin import PluginMetadata
from nonebot import get_driver

from .config import Config

__plugin_meta__ = PluginMetadata(
    name="鸣潮插件",
    description="基于NoneBot2的鸣潮游戏数据查询插件",
    usage="发送【鸣潮登录】进行账号绑定\n发送【鸣潮信息】查看角色数据",
    type="application",
    homepage="https://github.com/your-repo/WutheringWavesUID",
    config=Config,
    supported_adapters={
        "nonebot.adapters.onebot.v11",
        "nonebot.adapters.onebot.v12",
    },
)

global_config = get_driver().config
# 适配修改：使用 parse_obj 来正确加载 Pydantic 的 env_prefix 配置
plugin_config = Config.parse_obj(global_config)

# 导入处理器
from . import handlers
from . import web_routes

__all__ = ["plugin_config"]