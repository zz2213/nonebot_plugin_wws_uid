# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/handlers/character_list.py

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageEvent, Bot
from nonebot.matcher import Matcher

from ..services.user_service import user_service
from ..services.game_service import GameService
from ..services.character_service import CharacterService
from ..core.drawing.character_list_card import draw_character_list_card
from ..core.utils.image import pil_to_img_msg

# --- 初始化服务 ---
from ..core.api.waves_api import waves_api

game_service = GameService()
character_service = CharacterService(game_service)
# --- 服务初始化完成 ---


character_list_cmd = on_command("角色列表", aliases={"cklb", "练度"}, priority=10, block=True)


@character_list_cmd.handle()
async def _(bot: Bot, event: MessageEvent, matcher: Matcher):
  """
  处理 角色列表 命令
  (迁移自 wutheringwaves_charlist/__init__.py)
  """

  # 1. 获取账号信息
  bind_info = await user_service.get_user_bind(event.user_id)
  if not bind_info:
    await matcher.finish("你尚未绑定账号，请发送【鸣潮登录】进行绑定。")
    return

  await matcher.send(f"正在获取 UID: {bind_info.uid} 的角色列表数据，请稍候...")

  # 2. 调用 Service 获取数据
  try:
    list_data = await character_service.get_character_list_data(
        bind_info.cookie,
        bind_info.uid
    )

    if not list_data:
      await matcher.finish("获取角色列表数据失败，可能是 Cookie 已失效或 API 暂不可用。")
      return

    # 将 UID 注入数据
    list_data["uid"] = bind_info.uid

  except Exception as e:
    logger.error(f"get_character_list_data failed: {e}")
    await matcher.finish(f"获取数据时发生内部错误：{e}")
    return

  # 3. 调用 Drawing 绘制图片
  try:
    image = await draw_character_list_card(list_data, event.user_id)

    if image:
      await matcher.finish(pil_to_img_msg(image, format="JPEG"))
    else:
      await matcher.finish("绘制角色列表图失败。")

  except Exception as e:
    logger.error(f"draw_character_list_card failed: {e}")
    await matcher.finish(f"绘制图片时发生内部错误：{e}")
    return