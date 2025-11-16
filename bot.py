#!/usr/bin/env python3
import nonebot
from nonebot.adapters.onebot.v11 import Adapter as OneBotV11Adapter


def init():
    """初始化机器人"""
    # 初始化 NoneBot
    nonebot.init()

    # 注册适配器
    driver = nonebot.get_driver()
    driver.register_adapter(OneBotV11Adapter)

    # 加载插件
    nonebot.load_plugin("nonebot_plugin_datastore")  # 显式加载数据存储插件
    nonebot.load_plugins("src/plugins")
    app = nonebot.get_app()

    return app

if __name__ == "__main__":
    app = init()
    nonebot.run(app=app)