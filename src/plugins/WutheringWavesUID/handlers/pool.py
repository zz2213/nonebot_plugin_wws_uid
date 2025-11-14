# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/handlers/pool.py

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message
from nonebot.matcher import Matcher
from nonebot.log import logger

# 导入我们已更新的 GameService
from ..services.game_service import GameService
# 导入我们刚创建的绘图函数
from ..core.drawing.pool_card import draw_pool_card
from ..core.utils.image import pil_to_img_msg

# --- 初始化服务 ---
game_service = GameService()
# --- 服务初始化完成 ---


pool_cmd = on_command("卡池统计", aliases={"kc"}, priority=10, block=True)


@pool_cmd.handle()
async def _(matcher: Matcher):
    """
    处理 卡池统计 命令
    (迁移自 wutheringwaves_up/__init__.py)
    """

    await matcher.send(f"正在获取全服卡池抽取统计数据，请稍候...")

    try:
        # 1. 从 Service 获取数据
        data = await game_service.get_pool_stats()

        if not data or not data.data:
            await matcher.finish(f"获取卡池统计数据失败，可能暂无数据。")
            return

        # 2. 绘制图片
        image = await draw_pool_card(data)
        if image:
            await matcher.finish(pil_to_img_msg(image, format="JPEG"))
        else:
            await matcher.finish("绘制卡池统计图片失败。")

    except Exception as e:
        logger.error(f"pool_cmd failed: {e}")
        await matcher.finish(f"查询时发生内部错误：{e}")