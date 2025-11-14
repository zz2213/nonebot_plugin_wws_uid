# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/config.py

from pydantic import BaseModel, Field
from typing import Optional


class Config(BaseModel):
  """
  WutheringWavesUID 插件配置
  (迁移自 wutheringwaves_config/config_default.py)

  所有配置项都可以通过在 .env 文件中添加 "WAVES_" 前缀来覆盖
  例如: WAVES_API_URL="http://your.api.url/"
  """

  # 基础配置
  WAVES_API_URL: str = "http://127.0.0.1:8080/"  # 你的 waves-api 后端地址

  # --- 功能开关 ---
  WAVES_OPEN_CHAR_INFO: bool = True  # 角色面板
  WAVES_OPEN_STAMINA: bool = True  # 体力查询
  WAVES_OPEN_ROLE_INFO: bool = True  # 角色信息 (原项目未使用)
  WAVES_OPEN_GACHA_LOGS: bool = True  # 抽卡记录
  WAVES_OPEN_EXPLORE: bool = True  # 探索度
  WAVES_OPEN_ABYSS: bool = True  # 深渊 (深塔/全息/冥海)
  WAVES_OPEN_CALENDAR: bool = True  # 日历 (包含每日材料)
  WAVES_OPEN_WIKI: bool = True  # Wiki (角色/武器/声骸/攻略)
  WAVES_OPEN_RANK: bool = True  # 角色伤害排行
  WAVES_OPEN_TOTAL_RANK: bool = True  # 声骸总分排行
  WAVES_OPEN_QUERY: bool = True  # 数据统计 (持有率/出场率)
  WAVES_OPEN_CODE: bool = True  # 兑换码 (我们尚未迁移)

  # --- 角色面板配置 ---
  # (迁移自 wutheringwaves_charinfo/draw_char_card.py 和 show_config.py)
  WAVES_BLUR_RADIUS: int = 6  # 面板背景模糊半径
  WAVES_BLUR_BRIGHTNESS: float = 0.8  # 面板背景亮度
  WAVES_BLUR_CONTRAST: float = 1.2  # 面板背景对比度

  # --- 体力推送配置 ---
  # (迁移自 wutheringwaves_stamina)
  WAVES_STAMINA_THRESHOLD: int = 200  # 体力推送阈值 (暂未实现)

  # --- 抽卡记录配置 ---
  # (迁移自 wutheringwaves_gachalog)
  WAVES_GACHA_LIMIT: int = 5  # 抽卡记录显示的五星个数

  # --- 排行榜配置 ---
  WAVES_RANK_VERSION: str = "1.0"  # 排行榜数据版本

  class Config:
    extra = "ignore"  # 忽略 .env 中多余的配置
    env_prefix = "WAVES_"  # 自动从 .env 读取 WAVES_...