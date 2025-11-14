# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/handlers/role_info.py

import asyncio
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageEvent, Bot
from nonebot.matcher import Matcher
from nonebot.log import logger

from ..services.user_service import user_service
# 导入我们已更新的 GameService
from ..services.game_service import GameService
# 导入我们刚创建的绘图函数
from ..core.drawing.role_info_card import draw_role_info_card
from ..core.utils.image import pil_to_img_msg

# --- 初始化服务 ---
from ..core.api.waves_api import waves_api

game_service = GameService()
# --- 服务初始化完成 ---


role_info_cmd = on_command("鸣潮信息", aliases={"mcinfo", "信息", "面板"}, priority=10, block=True)


@role_info_cmd.handle()
async def _(bot: Bot, event: MessageEvent, matcher: Matcher):
    """
    处理 鸣潮信息 命令
    (迁移自 wutheringwaves_roleinfo/__init__.py)
    """

    # 1. 获取账号信息
    bind_info = await user_service.get_user_bind(event.user_id)
    if not bind_info:
        await matcher.finish("你尚未绑定账号，请发送【鸣潮登录】进行绑定。")
        return

    await matcher.send(f"正在获取 UID: {bind_info.uid} 的基础信息，请稍候...")

    # 2. 调用 Service 获取数据
    try:
        user_info_data = await game_service.get_user_info(
            bind_info.cookie,
            bind_info.uid
        )

        if not user_info_data:
            await matcher.finish("获取数据失败，可能是 Cookie 已失效或 API 暂不可用。")
            return

    except Exception as e:
        logger.error(f"Failed to get user_info data: {e}")
        await matcher.finish(f"获取数据时发生内部错误：{e}")
        return

    # 3. 调用 Drawing 绘制图片
    try:
        # user_id 用于绘制 QQ 头像
        image = await draw_role_info_card(user_info_data, event.user_id)

        if image:
            await matcher.finish(pil_to_img_msg(image, format="JPEG"))
        else:
            await matcher.finish("绘制基础信息卡片失败。")

    except Exception as e:
        logger.error(f"draw_role_info_card failed: {e}")
        await matcher.finish(f"绘制图片时发生内部错误：{e}")