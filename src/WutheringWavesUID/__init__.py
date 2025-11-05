# wws_native/__init__.py
from nonebot.plugin import PluginMetadata
from . import handlers # 导入handlers模块以注册所有指令

__plugin_meta__ = PluginMetadata(
    name="鸣潮原生插件",
    description="完整迁移自 WutheringWavesUID 的全功能鸣潮机器人",
    usage="发送 [鸣潮帮助] 查看指令",
    type="application",
    homepage="https://github.com/zz2213/nonebot_plugin_wws_uid"
)