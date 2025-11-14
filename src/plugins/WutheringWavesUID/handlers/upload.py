# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/handlers/upload.py

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageEvent, Bot
from nonebot.matcher import Matcher
from nonebot.log import logger

from ..services.user_service import user_service
# 导入我们所有需要的服务
from ..services.game_service import GameService
from ..services.character_service import CharacterService
from ..services.upload_service import UploadService

# --- 初始化服务 ---
from ..core.api.waves_api import waves_api

game_service = GameService()
character_service = CharacterService(game_service)
# UploadService 依赖 GameService 和 CharacterService
upload_service = UploadService(game_service, character_service)
# --- 服务初始化完成 ---


upload_cmd = on_command("上传面板", aliases={"scp", "上传"}, priority=10, block=True)


@upload_cmd.handle()
async def _(bot: Bot, event: MessageEvent, matcher: Matcher):
    """
    处理 上传面板 命令
    (迁移自 wutheringwaves_master/__init__.py)
    """

    # 1. 获取账号信息
    bind_info = await user_service.get_user_bind(event.user_id)
    if not bind_info:
        await matcher.finish("你尚未绑定账号，请发送【鸣潮登录】进行绑定。")
        return

    await matcher.send(f"正在获取 UID: {bind_info.uid} 的角色数据并计算期望伤害，请稍候...")
    await matcher.send("此过程将计算你所有角色的面板和伤害，可能需要 1-2 分钟...")

    # 2. 调用 Service 执行复杂的上传逻辑
    try:
        result_msg = await upload_service.calculate_and_upload(
            bind_info.cookie,
            bind_info.uid
        )

        await matcher.finish(result_msg)

    except Exception as e:
        logger.error(f"calculate_and_upload failed: {e}")
        logger.exception(e)
        await matcher.finish(f"上传时发生内部错误：{e}")