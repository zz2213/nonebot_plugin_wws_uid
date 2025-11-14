# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/handlers/status.py

import psutil
import time
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageEvent
from nonebot.matcher import Matcher
from nonebot.log import logger
from nonebot.permission import SUPERUSER

# 导入我们迁移的 框架B (团队buff) 注册器
from ..core.damage_team_buff.register import WavesCharRegister, WavesWeaponRegister
# 导入 wiki_service (用于检查 id2name.json)
from ..services.wiki_service import wiki_service
# 导入 动态配置服务
from ..services.config_service import config_service

# 记录插件启动时间
START_TIME = time.time()

status_cmd = on_command(
    "鸣潮状态",
    aliases={"wwo status", "wws status"},
    priority=10,
    block=True,
    permission=SUPERUSER  # 仅限超管
)


@status_cmd.handle()
async def _(event: MessageEvent, matcher: Matcher):
    """
    处理 状态 命令
    (迁移自 wutheringwaves_status/__init__.py)
    """

    # --- 1. 获取系统和进程信息 ---
    try:
        proc = psutil.Process()
        mem_info = proc.memory_info()
        mem_rss = mem_info.rss / 1024 / 1024  # RSS memory in MB

        run_time_seconds = int(time.time() - START_TIME)
        run_time_hours = run_time_seconds // 3600
        run_time_minutes = (run_time_seconds % 3600) // 60

    except Exception as e:
        logger.error(f"Failed to get psutil info: {e}")
        await matcher.finish("获取系统状态失败，请检查是否已安装 `psutil`。")
        return

    # --- 2. 检查内部服务状态 ---

    # 检查 框架B (团队buff) 脚本加载
    framework_b_loaded = WavesCharRegister.script_loaded and WavesWeaponRegister.script_loaded
    framework_b_count = len(WavesCharRegister.classes) + len(WavesWeaponRegister.classes)

    # 检查 动态配置
    config_initialized = config_service._initialized

    # 检查 Wiki 数据
    await wiki_service._load_maps()
    id_name_loaded = bool(wiki_service._id_name_map)
    id_name_count = len(wiki_service._id_name_map or {})

    # --- 3. 构造消息 ---
    msg_lines = [
        "⭐ 鸣潮插件运行状态 ⭐",
        f"· 插件已运行: {run_time_hours} 小时 {run_time_minutes} 分钟",
        f"· 进程内存占用: {mem_rss:.2f} MB",
        "--- 内部服务 ---",
        f"· 动态配置服务: {'✅ 已初始化' if config_initialized else '❌ 未初始化'}",
        f"· ID->Name 映射: {'✅ 已加载' if id_name_loaded else '❌ 加载失败'} ({id_name_count} 个条目)",
        f"· 团队Buff框架 (B): {'✅ 已加载' if framework_b_loaded else '❌ 未加载'} ({framework_b_count} 个脚本)",
    ]

    await matcher.finish("\n".join(msg_lines))