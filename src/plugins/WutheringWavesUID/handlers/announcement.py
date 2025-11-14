# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/handlers/announcement.py

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message
from nonebot.matcher import Matcher
from nonebot.log import logger

# 导入我们刚创建的服务和绘图函数
from ..services.announcement_service import announcement_service
from ..core.drawing.ann_card import draw_ann_card
from ..core.utils.image import pil_to_img_msg

ann_cmd = on_command("公告", aliases={"游戏公告"}, priority=10, block=True)


@ann_cmd.handle()
async def _(matcher: Matcher):
    """
    处理 公告 命令
    (迁移自 wutheringwaves_ann/__init__.py)
    """

    await matcher.send("正在获取最新游戏公告...")

    try:
        # 1. 从 Service 获取数据
        data = await announcement_service.get_announcements()

        if not data:
            await matcher.finish("获取公告数据失败，请稍后再试。")
            return

        # 2. 绘制图片
        image = await draw_ann_card(data)
        if image:
            await matcher.finish(pil_to_img_msg(image, format="JPEG"))
        else:
            await matcher.finish("绘制公告图失败。")

    except Exception as e:
        logger.error(f"ann_cmd failed: {e}")
        await matcher.finish(f"查询时发生内部错误：{e}")