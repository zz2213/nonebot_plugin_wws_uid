# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/__init__.py

from nonebot.plugin import PluginMetadata
from nonebot import get_driver
import asyncio # <-- 保留导入

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

driver = get_driver()
global_config = driver.config
# 适配修改：使用 parse_obj 来正确加载 Pydantic 的 env_prefix 配置
plugin_config = Config.parse_obj(global_config)


# --- 修复：将 database.init_db() 移至 on_startup ---
from . import database
from .services.config_service import config_service

# asyncio.run(database.init_db()) # <-- 移除此错误行

@driver.on_startup
async def _():
    # 异步初始化数据库
    await database.init_db()
    # 异步初始化动态配置
    await config_service.initialize_config()
# --- 修复结束 ---


# 导入处理器 (必须在 config_service 实例化之后)
from . import handlers
from . import web_routes

__all__ = ["plugin_config"]