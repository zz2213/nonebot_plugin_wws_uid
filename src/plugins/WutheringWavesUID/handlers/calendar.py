# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/handlers/calendar.py

import asyncio
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message
from nonebot.matcher import Matcher
from nonebot.log import logger

# 导入所有需要的服务
from ..services.calendar_service import calendar_service
from ..services.game_service import GameService
from ..services.announcement_service import announcement_service
# 导入绘图函数
from ..core.drawing.calendar_card import draw_calendar_card
from ..core.utils.image import pil_to_img_msg

# --- 初始化服务 ---
game_service = GameService()
# --- 服务初始化完成 ---


calendar_cmd = on_command("日历", aliases={"rl"}, priority=10, block=True)


@calendar_cmd.handle()
async def _(matcher: Matcher):
    """
    处理 日历 命令
    (迁移自 wutheringwaves_calendar/__init__.py)
    """

    await matcher.send("正在获取游戏日历数据，请稍候...")

    try:
        # 1. 并发获取所有数据
        calendar_task = calendar_service.get_calendar_data()
        pool_task = game_service.get_pool_list()
        ann_task = announcement_service.get_announcements()

        calendar_data, pool_resp, ann_data = await asyncio.gather(
            calendar_task,
            pool_task,
            ann_task
        )

        # 2. 校验数据
        if not calendar_data:
            await matcher.finish("获取日历数据失败 (材料/深渊)。")
            return

        if not pool_resp or not pool_resp.data:
            await matcher.finish("获取卡池数据失败。")
            return

        if not ann_data or not ann_data.get("EVENT"):
            await matcher.finish("获取活动数据失败。")
            return

        # 3. 绘制图片
        image = await draw_calendar_card(calendar_data, pool_resp.data, ann_data)
        if image:
            await matcher.finish(pil_to_img_msg(image, format="JPEG"))
        else:
            await matcher.finish("绘制日历图失败。")

    except Exception as e:
        logger.error(f"calendar_cmd failed: {e}")
        await matcher.finish(f"查询时发生内部错误：{e}")