# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/handlers/code.py

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message
from nonebot.matcher import Matcher
from nonebot.log import logger

# 导入我们刚创建的服务
from ..services.code_service import code_service

code_cmd = on_command("鸣潮兑换码", aliases={"兑换码", "dhm"}, priority=10, block=True)


@code_cmd.handle()
async def _(matcher: Matcher):
    """
    处理 鸣潮兑换码 命令
    (迁移自 wutheringwaves_code/__init__.py)
    """

    await matcher.send("正在获取最新可用兑换码...")

    try:
        # 1. 从 Service 获取数据
        code_list = await code_service.get_redemption_codes()

        if not code_list:
            await matcher.finish("获取兑换码数据失败，请稍后再试。")
            return

        # 2. 格式化为文本
        msg_lines = []
        for item in code_list:
            msg_lines.append(f"兑换码: {item.code}\n详情: {item.text}")

        separator = "\n" + "-" * 20 + "\n"
        final_msg = "⭐ 最新兑换码:\n" + separator.join(msg_lines)

        await matcher.finish(final_msg)

    except Exception as e:
        logger.error(f"code_cmd failed: {e}")
        await matcher.finish(f"查询时发生内部错误：{e}")