# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/handlers/echo_list.py

from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, MessageEvent, Bot
from nonebot.matcher import Matcher
from nonebot.log import logger

from ..services.user_service import user_service
from ..services.game_service import GameService
from ..services.character_service import CharacterService
# --- 移除硬编码，改用服务 ---
from ..services.wiki_service import wiki_service
# --- 导入结束 ---
from ..core.drawing.echo_list_card import draw_echo_list_card
from ..core.utils.image import pil_to_img_msg

# --- 初始化服务 ---
from ..core.api.waves_api import waves_api

game_service = GameService()
character_service = CharacterService(game_service)
# --- 服务初始化完成 ---


echo_list_cmd = on_command("声骸列表", aliases={"shlb"}, priority=10, block=True)


@echo_list_cmd.handle()
async def _(bot: Bot, event: MessageEvent, matcher: Matcher, args: Message = CommandArg()):
    """
    处理 声骸列表 命令
    """
    cmd_args = args.extract_plain_text().strip().split()

    # 1. 获取账号信息
    bind_info = await user_service.get_user_bind(event.user_id)
    if not bind_info:
        await matcher.finish("你尚未绑定账号，请发送【鸣潮登录】进行绑定。")
        return

    # 2. 解析参数
    role_name = ""
    if cmd_args:
        role_name = cmd_args[0]

    if not role_name:
        await matcher.finish("请输入要查询的角色名，例如：声骸列表 忌炎")
        return

    # --- 替换硬编码 map ---
    role_id_str = await wiki_service._find_item_id(role_name)
    if not role_id_str:
        await matcher.finish(f"未找到角色「{role_name}」，请检查名称或更新别名。")
        return

    try:
        role_id = int(role_id_str)
        if not (1100 < role_id < 1700):
            raise ValueError("ID 不在角色范围内")
    except ValueError:
        await matcher.finish(f"找到「{role_name}」的ID「{role_id_str}」不是有效的角色ID。")
        return
    # --- 替换完成 ---

    await matcher.send(f"正在获取「{role_name}」的声骸列表数据，请稍候...")

    # 3. 调用 Service 获取数据
    try:
        panel_data = await character_service.get_character_panel_data(
            bind_info.cookie,
            bind_info.uid,
            role_id
        )

        if not panel_data:
            await matcher.finish("获取角色数据失败，可能是 Cookie 已失效或 API 暂不可用。")
            return

        panel_data["uid"] = bind_info.uid  # 注入UID，绘图时需要

    except Exception as e:
        logger.error(f"get_character_panel_data failed: {e}")
        await matcher.finish(f"获取数据时发生内部错误：{e}")
        return

    # 4. 调用 Drawing 绘制图片
    try:
        image = await draw_echo_list_card(panel_data, event.user_id)

        if image:
            await matcher.finish(pil_to_img_msg(image, format="JPEG"))
        else:
            await matcher.finish("绘制声骸列表图失败。")

    except Exception as e:
        logger.error(f"draw_echo_list_card failed: {e}")
        await matcher.finish(f"绘制图片时发生内部错误：{e}")
        return