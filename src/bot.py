import nonebot
from nonebot.adapters.onebot.v11 import Adapter as OneBotAdapter
from nonebot.log import logger

# 初始化
nonebot.init()

# 注册适配器
driver = nonebot.get_driver()
driver.register_adapter(OneBotAdapter)

# 打印已加载的插件
@driver.on_startup
async def startup():
    from nonebot.plugin import get_loaded_plugins
    plugins = get_loaded_plugins()
    logger.info(f"已加载插件: {[plugin.name for plugin in plugins]}")

# 加载你的插件
#nonebot.load_plugin("plugins.WutheringWavesUID")
nonebot.load_plugin("plugins.Test")

if __name__ == "__main__":
    nonebot.run()