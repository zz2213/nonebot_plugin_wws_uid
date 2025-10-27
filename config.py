# nonebot_plugin_wws_uid/config.py

from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
  """
  nonebot-plugin-wws-uid 的配置项
  """
  # 鸣潮玩家信息查询API
  WWS_API_URL: str = "https://api.kurobbs.com/gamer/api/wutheringWaves/getInfo"

  # 代理设置，方便访问API
  WWS_PROXY: str | None = None