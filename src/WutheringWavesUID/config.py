from pydantic import BaseModel, Extra
from typing import Optional


class Config(BaseModel, extra=Extra.ignore):
  """鸣潮原生插件配置项"""
  # API配置
  WWS_API_URL: str = "https://api.kurobbs.com/gamer/api/"
  WWS_PROXY: Optional[str] = None

  # 登录配置
  WAVES_LOGIN_URL: str = ""
  WAVES_LOGIN_URL_SELF: bool = False
  WAVES_QR_LOGIN: bool = True
  WAVES_LOGIN_FORWARD: bool = False
  WAVES_TENCENT_WORD: bool = False

  # 服务器配置
  HOST: str = "127.0.0.1"
  PORT: int = 8080