# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/handlers/update_log.py

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message
from nonebot.matcher import Matcher
from nonebot.log import logger

# 导入我们刚创建的绘图函数
from ..core.drawing.update_log_card import draw_update_log_card
from ..core.utils.image import pil_to_img_msg

update_log_cmd = on_command("鸣潮更新记录", aliases={"wws update"}, priority=10, block=True)


@update_log_cmd.handle()
async def _(matcher: Matcher):
    """
    处理 更新记录 命令
    (迁移自 wutheringwaves_update/__init__.py)
    """

    await matcher.send("正在获取插件更新记录...")

    try:
        # 1. 调用 Drawing 绘制图片
        image = await draw_update_log_card()

        if image:
            await matcher.finish(pil_to_img_msg(image, format="JPEG"))
        else:
            await matcher.finish("绘制更新日志失败，可能是 `log.json` 文件缺失。")

    except Exception as e:
        logger.error(f"draw_update_log_card failed: {e}")
        await matcher.finish(f"绘制时发生内部错误：{e}")