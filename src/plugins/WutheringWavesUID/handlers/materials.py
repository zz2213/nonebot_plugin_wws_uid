# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/handlers/materials.py

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageEvent
from nonebot.matcher import Matcher
from nonebot.log import logger

# 导入我们刚创建的服务和绘图函数
from ..services.calendar_service import calendar_service
from ..core.drawing.materials_card import draw_material_card
from ..core.utils.image import pil_to_img_msg

materials_cmd = on_command("每日材料", aliases={"cl", "材料"}, priority=10, block=True)


@materials_cmd.handle()
async def _(matcher: Matcher):
  """
  处理 每日材料 命令
  (迁移自 wutheringwaves_develop/__init__.py)
  """
  await matcher.send("正在获取今日可刷取材料...")

  try:
    # 1. 从 Service 获取数据
    data = await calendar_service.get_calendar_data()

    if not data:
      await matcher.finish("获取日历数据失败，请稍后再试。")
      return

    # 2. 绘制图片
    image = await draw_material_card(data)
    if image:
      await matcher.finish(pil_to_img_msg(image, format="JPEG"))
    else:
      await matcher.finish("绘制每日材料图失败。")

  except Exception as e:
    logger.error(f"materials_cmd failed: {e}")
    await matcher.finish(f"查询时发生内部错误：{e}")