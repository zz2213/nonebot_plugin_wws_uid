# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/handlers/ranking.py

from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, MessageEvent, Bot
from nonebot.matcher import Matcher

from ..services.user_service import user_service
# 导入我们已更新的 GameService
from ..services.game_service import GameService
# 导入排行 API 需要的 Pydantic 模型
from ..core.api.ranking_api import RankItem, TotalRankRequest
# 导入我们刚创建的绘图函数
from ..core.drawing.ranking_card import draw_ranking_card, draw_total_ranking_card
from ..core.utils.image import pil_to_img_msg

# --- 初始化服务 ---
game_service = GameService()
# --- 服务初始化完成 ---


# --- 角色ID 临时 hardcode ---
# TODO: 后续应替换为调用 AliasService
role_id_map = {
  "忌炎": 1404, "吟霖": 1302, "卡卡罗": 1301, "维里奈": 1503, "安可": 1203,
  "鉴心": 1405, "凌阳": 1104, "散华": 1102, "丹瑾": 1602, "莫特斐": 1204,
  "秧秧": 1402, "白芷": 1103, "炽霞": 1202, "渊武": 1303, "桃祈": 1601,
  "漂泊者": 1501, "光主": 1501, "暗主": 1604, "长离": 1205,
  # ...
}
# ---


char_rank_cmd = on_command("角色排行", aliases={"伤害排行"}, priority=10, block=True)
total_rank_cmd = on_command("总分排行", aliases={"声骸排行"}, priority=10, block=True)


@char_rank_cmd.handle()
async def _(bot: Bot, event: MessageEvent, matcher: Matcher, args: Message = CommandArg()):
  """
  处理 角色排行 命令
  (迁移自 wutheringwaves_rank/__init__.py)
  """
  cmd_args = args.extract_plain_text().strip().split()

  role_name = ""
  if cmd_args:
    role_name = cmd_args[0]

  if not role_name:
    await matcher.finish("请输入要查询的角色名，例如：角色排行 忌炎")
    return

  char_id = role_id_map.get(role_name)
  if not char_id:
    await matcher.finish(f"未找到角色「{role_name}」的ID，请检查名称或更新角色列表。")
    return

  await matcher.send(f"正在获取「{role_name}」的伤害排行榜，请稍候...")

  # 构造请求
  payload = RankItem(
      char_id=char_id,
      page=1,
      page_num=10,
      rank_type=0,  # 0=伤害排行
      version="1.0",  # TODO: 版本号应从配置中读取
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
  (迁移自 wutheringwaves_rank/__init__.py)
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
      version="1.0",  # TODO: 版本号应从配置中读取
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