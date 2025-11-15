#!/usr/bin/env python3
import nonebot
from nonebot.adapters.onebot.v11 import Adapter as OneBotV11Adapter


async def init_database():
    """确保数据库初始化"""
    try:
        from nonebot_plugin_datastore import get_session
        from my_wuthering_bot.src.plugins.WutheringWavesUID import Base

        # 测试数据库连接
        async with get_session() as session:
            # 执行简单的查询来测试连接
            await session.execute("SELECT 1")
            print("✅ 数据库连接正常")

    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        raise

def init():
    """初始化机器人"""
    # 初始化 NoneBot
    nonebot.init()

    # 注册适配器
    driver = nonebot.get_driver()
    driver.register_adapter(OneBotV11Adapter)

    # 加载插件
    nonebot.load_plugin("nonebot_plugin_datastore")  # 显式加载数据存储插件
    nonebot.load_plugin("plugins.WutheringWavesUID")

    # 可选：加载调试插件
    try:
        nonebot.load_plugin("plugins.debug_tools")
    except Exception as e:
        print(f"调试工具加载失败: {e}，但不影响主要功能")

    app = nonebot.get_app()

    # 添加启动事件
    @app.on_event("startup")
    async def startup_event():
        print("=" * 50)
        print("鸣潮测试机器人启动成功!")
        print(f"访问地址: http://localhost:8080")

        # 初始化数据库
        await init_database()

        # 检查鸣潮插件状态
        try:
            from my_wuthering_bot.src.plugins.WutheringWavesUID import get_uid_by_user
            print("✅ 鸣潮插件数据库模块加载正常")
        except Exception as e:
            print(f"❌ 鸣潮插件数据库模块加载失败: {e}")

        print("=" * 50)

    return app

if __name__ == "__main__":
    app = init()
    nonebot.run(app=app)