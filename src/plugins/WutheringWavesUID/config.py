from pydantic import BaseModel, Extra
from typing import Optional

class Config(BaseModel, extra=Extra.ignore):
    """鸣潮插件配置"""

    # API配置
    WAVES_API_URL: str = "https://api.kurobbs.com/gamer/api/"
    WAVES_PROXY: Optional[str] = None

    # 登录配置
    WAVES_LOGIN_URL: str = ""
    WAVES_LOGIN_URL_SELF: bool = False
    WAVES_QR_LOGIN: bool = True
    WAVES_LOGIN_FORWARD: bool = False
    WAVES_TENCENT_WORD: bool = False

    # 服务器配置
    HOST: str = "127.0.0.1"
    PORT: int = 8080

    # 功能开关
    WAVES_ENABLE_LOGIN: bool = True
    WAVES_ENABLE_CARD: bool = True

    # 图片生成配置
    WAVES_CARD_WIDTH: int = 800
    WAVES_CARD_HEIGHT: int = 600
    WAVES_FONT_PATH: str = "assets/fonts/"