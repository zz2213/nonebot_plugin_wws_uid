# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/handlers/help.py

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message
from nonebot.matcher import Matcher
from nonebot.log import logger

# 导入我们刚创建的绘图函数
from ..core.drawing.help_card import draw_help_card
from ..core.utils.image import pil_to_img_msg

help_cmd = on_command("鸣潮帮助", aliases={"帮助", "mc help"}, priority=5, block=True)


@help_cmd.handle()
async def _(matcher: Matcher):
  """
  处理 帮助 命令
  (迁移自 wutheringwaves_help/__init__.py)
  """

  await matcher.send("正在绘制帮助菜单，请稍候...")

  try:
    # 1. 调用 Drawing 绘制图片
    image = await draw_help_card()

    if image:
      await matcher.finish(pil_to_img_msg(image, format="JPEG"))
    else:
      await matcher.finish("绘制帮助菜单失败，请检查资源文件。")

  except Exception as e:
    logger.error(f"draw_help_card failed: {e}")
    await matcher.finish(f"绘制帮助菜单时发生内部错误：{e}")