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

driver = get_driver()
global_config = driver.config
# 修复：使用 .dict() 或 .model_dump() 将全局配置对象转换为字典，
# 以解决 Pydantic v2 的兼容性问题，并正确应用 env_prefix。
plugin_config = Config.parse_obj(global_config.dict())


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