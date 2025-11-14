# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/handlers/ranking.py

from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, MessageEvent, Bot
from nonebot.matcher import Matcher
from nonebot.log import logger

from ..services.user_service import user_service
from ..services.game_service import GameService
# --- 移除硬编码，改用服务 ---
from ..services.wiki_service import wiki_service
# --- 导入结束 ---
from ..core.api.ranking_api import RankItem, TotalRankRequest
from ..core.drawing.ranking_card import draw_ranking_card, draw_total_ranking_card
from ..core.utils.image import pil_to_img_msg
from .. import plugin_config  # 导入配置

# --- 初始化服务 ---
game_service = GameService()
# --- 服务初始化完成 ---


char_rank_cmd = on_command("角色排行", aliases={"伤害排行"}, priority=10, block=True)
total_rank_cmd = on_command("总分排行", aliases={"声骸排行"}, priority=10, block=True)


@char_rank_cmd.handle()
async def _(bot: Bot, event: MessageEvent, matcher: Matcher, args: Message = CommandArg()):
    """
    处理 角色排行 命令
    """
    cmd_args = args.extract_plain_text().strip().split()

    role_name = ""
    if cmd_args:
        role_name = cmd_args[0]

    if not role_name:
        await matcher.finish("请输入要查询的角色名，例如：角色排行 忌炎")
        return

    # --- 替换硬编码 map ---
    char_id_str = await wiki_service._find_item_id(role_name)
    if not char_id_str:
        await matcher.finish(f"未找到角色「{role_name}」，请检查名称或更新别名。")
        return

    try:
        char_id = int(char_id_str)
        if not (1100 < char_id < 1700):
            raise ValueError("ID 不在角色范围内")
    except ValueError:
        await matcher.finish(f"找到「{role_name}」的ID「{char_id_str}」不是有效的角色ID。")
        return
    # --- 替换完成 ---

    await matcher.send(f"正在获取「{role_name}」的伤害排行榜，请稍候...")

    # 构造请求
    payload = RankItem(
        char_id=char_id,
        page=1,
        page_num=10,
        rank_type=0,  # 0=伤害排行
        version=plugin_config.WAVES_RANK_VERSION,  # 从配置读取
        waves_id=""  # 传空字符串查询所有
    )

    try:
        data = await game_service.get_character_rank(payload)

        if not data or not data.data or not data.data.details:
            await matcher.finish(f"获取「{role_name}」的排行榜数据失败，可能暂无数据。")
            return

        # 绘制图片
        image = await draw_ranking_card(data.data, char_id)
        if image:
            await matcher.finish(pil_to_img_msg(image, format="JPEG"))
        else:
            await matcher.finish("绘制排行榜图片失败。")

    except Exception as e:
        logger.error(f"char_rank_cmd failed: {e}")
        await matcher.finish(f"查询时发生内部错误：{e}")


@total_rank_cmd.handle()
async def _(bot: Bot, event: MessageEvent, matcher: Matcher, args: Message = CommandArg()):
    """
    处理 总分排行 命令
    """
    # 1. 获取账号信息
    bind_info = await user_service.get_user_bind(event.user_id)
    if not bind_info:
        await matcher.finish("查询总分排行需要您先绑定账号，请发送【鸣潮登录】进行绑定。")
        return

    await matcher.send(f"正在获取 UID {bind_info.uid} 所在页的总分排行榜，请稍候...")

    # 构造请求
    payload = TotalRankRequest(
        page=1,
        page_num=10,
        version=plugin_config.WAVES_RANK_VERSION,  # 从配置读取
        waves_id=bind_info.uid  # 传入 UID 来查询该 UID 所在的页面
    )

    try:
        data = await game_service.get_total_rank(payload)

        if not data or not data.data or not data.data.score_details:
            await matcher.finish(f"获取总分排行榜数据失败，可能暂无数据。")
            return

        # 绘制图片
        image = await draw_total_ranking_card(data.data)
        if image:
            await matcher.finish(pil_to_img_msg(image, format="JPEG"))
        else:
            await matcher.finish("绘制总分排行图片失败。")

    except Exception as e:
        logger.error(f"total_rank_cmd failed: {e}")
        await matcher.finish(f"查询时发生内部错误：{e}")