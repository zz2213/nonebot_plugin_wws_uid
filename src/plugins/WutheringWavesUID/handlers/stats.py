# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/handlers/stats.py

from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, MessageEvent, Bot
from nonebot.matcher import Matcher
from nonebot.log import logger

# 导入我们已更新的 GameService
from ..services.game_service import GameService
# 导入 API 需要的 Pydantic 模型
from ..core.api.ranking_api import (
  RoleHoldRateRequest, AbyssRecordRequest, SlashAppearRateRequest
)
# 导入我们刚创建的绘图函数
from ..core.drawing.stats_card import (
  draw_char_hold_rate_card, draw_tower_appear_rate_card, draw_slash_appear_rate_card
)
from ..core.utils.image import pil_to_img_msg

# --- 初始化服务 ---
game_service = GameService()
# --- 服务初始化完成 ---


hold_rate_cmd = on_command("角色持有率", aliases={"持有率"}, priority=10, block=True)
tower_rate_cmd = on_command("深塔出场率", aliases={"深塔使用率"}, priority=10, block=True)
slash_rate_cmd = on_command("冥海出场率", aliases={"冥海使用率"}, priority=10, block=True)


@hold_rate_cmd.handle()
async def _(matcher: Matcher):
  """
  处理 角色持有率 命令
  (迁移自 wutheringwaves_query/__init__.py)
  """
  await matcher.send(f"正在获取角色持有率数据，请稍候...")

  # 构造请求
  payload = RoleHoldRateRequest(char_id=None)  # None 为查询所有

  try:
    data = await game_service.get_character_hold_rate(payload)

    if not data or not data.data:
      await matcher.finish(f"获取角色持有率数据失败，可能暂无数据。")
      return

    # 绘制图片
    image = await draw_char_hold_rate_card(data.data)
    if image:
      await matcher.finish(pil_to_img_msg(image, format="JPEG"))
    else:
      await matcher.finish("绘制角色持有率图片失败。")

  except Exception as e:
    logger.error(f"hold_rate_cmd failed: {e}")
    await matcher.finish(f"查询时发生内部错误：{e}")


@tower_rate_cmd.handle()
async def _(matcher: Matcher):
  """
  处理 深塔出场率 命令
  (迁移自 wutheringwaves_query/__init__.py)
  """
  await matcher.send(f"正在获取深塔出场率数据，请稍候...")

  # 构造请求 (查询所有区域)
  payload = AbyssRecordRequest(abyss_type="a")

  try:
    data = await game_service.get_abyss_usage_rate(payload)

    if not data or not data.data:
      await matcher.finish(f"获取深塔出场率数据失败，可能暂无数据。")
      return

    # 绘制图片
    image = await draw_tower_appear_rate_card(data.data)
    if image:
      await matcher.finish(pil_to_img_msg(image, format="JPEG"))
    else:
      await matcher.finish("绘制深塔出场率图片失败。")

  except Exception as e:
    logger.error(f"tower_rate_cmd failed: {e}")
    await matcher.finish(f"查询时发生内部错误：{e}")


@slash_rate_cmd.handle()
async def _(matcher: Matcher):
  """
  处理 冥海出场率 命令
  (迁移自 wutheringwaves_query/__init__.py)
  """
  await matcher.send(f"正在获取冥海出场率数据，请稍候...")

  # 构造请求
  payload = SlashAppearRateRequest()

  try:
    data = await game_service.get_slash_appear_rate(payload)

    if not data or not data.data:
      await matcher.finish(f"获取冥海出场率数据失败，可能暂无数据。")
      return

    # 绘制图片
    image = await draw_slash_appear_rate_card(data.data)
    if image:
      await matcher.finish(pil_to_img_msg(image, format="JPEG"))
    else:
      await matcher.finish("绘制冥海出场率图片失败。")

  except Exception as e:
    logger.error(f"slash_rate_cmd failed: {e}")
    await matcher.finish(f"查询时发生内部错误：{e}")