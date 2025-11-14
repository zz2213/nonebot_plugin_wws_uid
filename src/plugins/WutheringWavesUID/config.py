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

    # --- 新增 (用于 Web 登录) ---
    WAVES_HOST: str = "127.0.0.1"
    WAVES_PORT: int = 8080  # 确保这个端口与你 NoneBot 的主端口不同
    # --- 结束 ---

    # --- 新增 (用于动态配置) ---
    WAVES_DYNAMIC_CONFIG_PATH: Path = Path("data/wutheringwaves_uid/wws_dynamic_config.json")
    # --- 结束 ---

    # 基础配置
    WAVES_API_URL: str = "http://127.0.0.1:8080/"  # 你的 waves-api 后端地址

    # --- 功能开关 ---
    WAVES_OPEN_CHAR_INFO: bool = True  # 角色面板
    WAVES_OPEN_STAMINA: bool = True  # 体力查询
    WAVES_OPEN_ROLE_INFO: bool = True  # 角色信息
    WAVES_OPEN_GACHA_LOGS: bool = True  # 抽卡记录
    WAVES_OPEN_EXPLORE: bool = True  # 探索度
    WAVES_OPEN_ABYSS: bool = True  # 深渊 (深塔/全息/冥海)
    WAVES_OPEN_CALENDAR: bool = True  # 日历
    WAVES_OPEN_MATERIALS: bool = True  # 每日材料
    WAVES_OPEN_WIKI: bool = True  # Wiki (角色/武器/声骸/攻略)
    WAVES_OPEN_RANK: bool = True  # 角色伤害排行
    WAVES_OPEN_TOTAL_RANK: bool = True  # 声骸总分排行
    WAVES_OPEN_QUERY: bool = True  # 数据统计 (持有率/出场率)
    WAVES_OPEN_CODE: bool = True  # 兑换码
    WAVES_OPEN_PERIOD: bool = True  # 资源统计
    WAVES_OPEN_POKER: bool = True  # 扑克牌
    WAVES_OPEN_STATUS: bool = True  # 运行状态
    WAVES_OPEN_UPDATE_LOG: bool = True  # 更新日志
    WAVES_OPEN_UPLOAD: bool = True  # 上传面板

    # --- 角色面板配置 ---
    WAVES_BLUR_RADIUS: int = 6  # 面板背景模糊半径
    WAVES_BLUR_BRIGHTNESS: float = 0.8  # 面板背景亮度
    WAVES_BLUR_CONTRAST: float = 1.2  # 面板背景对比度

    # --- 体力推送配置 ---
    WAVES_STAMINA_THRESHOLD: int = 200  # 体力推送阈值 (暂未实现)

    # --- 抽卡记录配置 ---
    WAVES_GACHA_LIMIT: int = 5  # 抽卡记录显示的五星个数

    # --- 排行榜配置 ---
    WAVES_RANK_VERSION: str = "1.0"  # 排行榜数据版本

    class Config:
        extra = "ignore"
        env_prefix = "WAVES_"