# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/config.py

from pydantic import BaseModel, Field
from typing import Optional
from pathlib import Path


class Config(BaseModel):
    """
    WutheringWavesUID 插件配置
    (迁移自 wutheringwaves_config/config_default.py)

    所有配置项都可以通过在 .env 文件中添加 "WAVES_" 前缀来覆盖
    例如: WAVES_API_URL="http://your.api.url/"
    """

    # --- Web 登录配置 ---
    WAVES_HOST: str = "127.0.0.1"
    WAVES_PORT: int = 8080  # 确保这个端口与你 NoneBot 的主端口一致

    # --- 动态配置路径 ---
    WAVES_DYNAMIC_CONFIG_PATH: Path = Path("data/wutheringwaves_uid/wws_dynamic_config.json")

    # --- 基础 API 配置 ---
    WAVES_API_URL: str = "http://127.0.0.1:8080/"  # 你的 waves-api (官方数据) 后端地址

    # --- 新增：排行榜 API 配置 ---
    WAVES_RANK_API_URL: str = "https://top.camellya.xyz"  # 排行榜和统计数据的 API 地址
    # --- 新增结束 ---

    # --- 功能开关 ---
    WAVES_OPEN_CHAR_INFO: bool = True
    WAVES_OPEN_STAMINA: bool = True
    WAVES_OPEN_ROLE_INFO: bool = True
    WAVES_OPEN_GACHA_LOGS: bool = True
    WAVES_OPEN_EXPLORE: bool = True
    WAVES_OPEN_ABYSS: bool = True
    WAVES_OPEN_CALENDAR: bool = True
    WAVES_OPEN_MATERIALS: bool = True
    WAVES_OPEN_WIKI: bool = True
    WAVES_OPEN_RANK: bool = True
    WAVES_OPEN_TOTAL_RANK: bool = True
    WAVES_OPEN_QUERY: bool = True
    WAVES_OPEN_CODE: bool = True
    WAVES_OPEN_PERIOD: bool = True
    WAVES_OPEN_POKER: bool = True
    WAVES_OPEN_STATUS: bool = True
    WAVES_OPEN_UPDATE_LOG: bool = True
    WAVES_OPEN_UPLOAD: bool = True

    # --- 细致配置 ---
    WAVES_BLUR_RADIUS: int = 6
    WAVES_BLUR_BRIGHTNESS: float = 0.8
    WAVES_BLUR_CONTRAST: float = 1.2
    WAVES_STAMINA_THRESHOLD: int = 200
    WAVES_GACHA_LIMIT: int = 5
    WAVES_RANK_VERSION: str = "1.0"

    class Config:
        extra = "ignore"
        env_prefix = "WAVES_"