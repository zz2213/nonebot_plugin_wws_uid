# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/handlers/poker.py

import asyncio
from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, MessageEvent, Bot
from nonebot.matcher import Matcher
from nonebot.log import logger

from ..services.user_service import user_service
from ..services.game_service import GameService
from ..services.wiki_service import wiki_service
from ..core.api.ranking_api import OneRankRequest
from ..core.drawing.poker_card import draw_poker_card
from ..core.utils.image import pil_to_img_msg

# --- 初始化服务 ---
game_service = GameService()
# --- 服务初始化完成 ---


poker_cmd = on_command("poker", aliases={"扑克牌"}, priority=10, block=True)


@poker_cmd.handle()
async def _(bot: Bot, event: MessageEvent, matcher: Matcher, args: Message = CommandArg()):
    """
    处理 poker 命令
    (迁移自 wutheringwaves_more/__init__.py)
    """

    # 1. 获取账号信息
    bind_info = await user_service.get_user_bind(event.user_id)
    if not bind_info:
        await matcher.finish("你尚未绑定账号，请发送【鸣潮登录】进行绑定。")
        return

    # 2. 解析参数 (角色名)
    role_name = args.extract_plain_text().strip()
    if not role_name:
        await matcher.finish("请输入要查询的角色名，例如：poker 忌炎")
        return

    # 3. 转换 ID
    char_id_str = await wiki_service._find_item_id(role_name)
    if not char_id_str:
        await matcher.finish(f"未找到角色「{role_name}」，请检查名称或更新别名。")
        return

    try:
        char_id = int(char_id_str)
    except ValueError:
        await matcher.finish(f"找到「{role_name}」的ID「{char_id_str}」不是有效的角色ID。")
        return

    await matcher.send(f"正在获取「{role_name}」的排行数据以生成扑克牌...")

    # 4. 调用 Service 获取数据
    try:
        # 扑克牌需要两个数据：玩家信息(user_info)和角色排行(rank_detail)
        user_info_task = game_service.get_user_info(bind_info.cookie, bind_info.uid)

        rank_payload = OneRankRequest(char_id=char_id, waves_id=bind_info.uid)
        rank_data_task = game_service.get_one_rank(rank_payload)

        user_info_data, rank_data = await asyncio.gather(user_info_task, rank_data_task)

        if not user_info_data:
            await matcher.finish("获取玩家信息失败，无法生成扑克牌。")
            return

        if not rank_data or not rank_data.data:
            await matcher.finish(f"获取「{role_name}」的排行数据失败，请先【上传面板】再试。")
            return

        rank_detail = rank_data.data[0]  # 获取玩家自己的排行

    except Exception as e:
        logger.error(f"Failed to get poker data: {e}")
        await matcher.finish(f"获取数据时发生内部错误：{e}")
        return

    # 5. 调用 Drawing 绘制图片
    try:
        image = await draw_poker_card(rank_detail, user_info_data)

        if image:
            await matcher.finish(pil_to_img_msg(image, format="JPEG"))
        else:
            await matcher.finish("绘制扑克牌失败。")

    except Exception as e:
        logger.error(f"draw_poker_card failed: {e}")
        await matcher.finish(f"绘制图片时发生内部错误：{e}")