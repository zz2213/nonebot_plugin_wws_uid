# WutheringWavesUID1/wutheringwaves_start/start.py (修改后)
import nonebot
from nonebot.log import logger # 替换 gsuid_core.logger

from ..wutheringwaves_resource import startup

# 使用 NoneBot 的 @nonebot.on_startup 装饰器替换 @on_core_start
@nonebot.on_startup
async def all_start():
    logger.info("[鸣潮] 启动中...")
    try:
        from ..utils.damage.register_char import register_char
        from ..utils.damage.register_echo import register_echo
        from ..utils.damage.register_weapon import register_weapon
        from ..utils.limit_user_card import load_limit_user_card
        from ..utils.map.damage.register import register_damage, register_rank
        from ..utils.queues import init_queues

        # 注册
        register_weapon()
        register_echo()
        register_damage()
        register_rank()
        register_char()

        # 初始化任务队列
        init_queues()

        # 加载角色极限面板
        card_list = await load_limit_user_card()
        logger.info(f"[鸣潮][加载角色极限面板] 数量: {len(card_list)}")

        await startup()
    except Exception as e:
        logger.exception(e)

    logger.success("[鸣潮] 启动完成✅")