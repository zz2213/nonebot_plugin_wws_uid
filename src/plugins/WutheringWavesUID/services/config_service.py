# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/services/config_service.py

import json
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
import aiofiles
from nonebot.log import logger

# 导入静态配置 (来自 .env)
from ..config import plugin_config

# --- 路径定义 ---
DATA_PATH = Path(__file__).parent.parent / "core" / "data"
DYNAMIC_CONFIG_PATH = DATA_PATH / "dynamic_config.json"

# --- 默认配置 (迁移自 config_default.py) ---
# 这些是最低优先级的默认值
# 优先级: 动态JSON -> 静态.env -> 此处默认值
_DEFAULTS: Dict[str, Any] = {
    "WAVES_OPEN_CHAR_INFO": True,
    "WAVES_OPEN_STAMINA": True,
    "WAVES_OPEN_ROLE_INFO": True,
    "WAVES_OPEN_GACHA_LOGS": True,
    "WAVES_OPEN_EXPLORE": True,
    "WAVES_OPEN_ABYSS": True,
    "WAVES_OPEN_CALENDAR": True,
    "WAVES_OPEN_WIKI": True,
    "WAVES_OPEN_RANK": True,
    "WAVES_OPEN_TOTAL_RANK": True,
    "WAVES_OPEN_QUERY": True,
    "WAVES_OPEN_CODE": True,
    "WAVES_BLUR_RADIUS": 6,
    "WAVES_BLUR_BRIGHTNESS": 0.8,
    "WAVES_BLUR_CONTRAST": 1.2,
    "WAVES_STAMINA_THRESHOLD": 200,
    "WAVES_GACHA_LIMIT": 5,
    "WAVES_RANK_VERSION": "1.0",
}


class ConfigService:
    """
    动态配置服务
    (迁移自 wutheringwaves_config)
    """

    def __init__(self):
        self._dynamic_config: Optional[Dict[str, Any]] = None
        self._lock = asyncio.Lock()
        DATA_PATH.mkdir(parents=True, exist_ok=True)
        if not DYNAMIC_CONFIG_PATH.exists():
            self._initialize_json()

    def _initialize_json(self):
        """同步创建空的 JSON 文件"""
        try:
            with open(DYNAMIC_CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump({}, f)
        except IOError:
            pass

    async def _read_dynamic_config(self) -> Dict[str, Any]:
        """(私有) 异步读取动态配置文件"""
        if self._dynamic_config is not None:
            return self._dynamic_config

        async with self._lock:
            # 双重检查
            if self._dynamic_config is not None:
                return self._dynamic_config

            try:
                async with aiofiles.open(DYNAMIC_CONFIG_PATH, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    self._dynamic_config = json.loads(content)
                    return self._dynamic_config
            except (json.JSONDecodeError, FileNotFoundError):
                self._dynamic_config = {}
                return {}
            except Exception as e:
                logger.error(f"Failed to read dynamic config: {e}")
                return {}  # 出错时返回空, 触发回退

    async def _write_dynamic_config(self, config: Dict[str, Any]) -> bool:
        """(私有) 异步写入动态配置文件"""
        async with self._lock:
            try:
                async with aiofiles.open(DYNAMIC_CONFIG_PATH, 'w', encoding='utf-8') as f:
                    await f.write(json.dumps(config, ensure_ascii=False, indent=4))
                self._dynamic_config = config  # 更新内存缓存
                return True
            except IOError as e:
                logger.error(f"Failed to write dynamic config: {e}")
                return False

    async def get_config(self, key: str) -> Any:
        """
        获取一个配置项 (优先级: 动态JSON -> 静态.env -> 默认值)
        """
        # 1. 检查动态配置 (JSON)
        dynamic_config = await self._read_dynamic_config()
        if key in dynamic_config:
            return dynamic_config[key]

        # 2. 检查静态配置 (.env)
        if hasattr(plugin_config, key):
            return getattr(plugin_config, key)

        # 3. 回退到硬编码的默认值
        return _DEFAULTS.get(key)

    async def set_config(self, key: str, value_str: str) -> str:
        """设置一个配置项 (写入 JSON)"""
        # 1. 检查 key 是否合法
        if key not in _DEFAULTS:
            return f"❌ 无效的配置项: {key}"

        # 2. 转换类型
        default_value = _DEFAULTS[key]
        value: Any
        try:
            if isinstance(default_value, bool):
                if value_str.lower() in ["true", "on", "1", "开启"]:
                    value = True
                elif value_str.lower() in ["false", "off", "0", "关闭"]:
                    value = False
                else:
                    raise ValueError("布尔值必须是 开启/关闭 或 true/false")
            elif isinstance(default_value, int):
                value = int(value_str)
            elif isinstance(default_value, float):
                value = float(value_str)
            else:
                value = value_str  # 字符串
        except ValueError as e:
            return f"❌ 值「{value_str}」的类型不正确: {e}"

        # 3. 写入
        config = await self._read_dynamic_config()
        config[key] = value
        if await self._write_dynamic_config(config):
            return f"✅ 配置「{key}」已设置为「{value}」"
        else:
            return "❌ 写入动态配置文件失败"

    async def reset_config(self, key: str) -> str:
        """重置一个配置项 (从 JSON 中删除)"""
        if key not in _DEFAULTS:
            return f"❌ 无效的配置项: {key}"

        config = await self._read_dynamic_config()
        if key not in config:
            return "ℹ️ 该配置项未被动态修改，无需重置。"

        del config[key]

        if await self._write_dynamic_config(config):
            return f"✅ 配置「{key}」已重置为默认值。"
        else:
            return "❌ 写入动态配置文件失败"

    async def get_all_configs_str(self) -> str:
        """获取所有配置项的当前状态 (用于显示)"""
        msg = "--- 鸣潮插件当前配置 ---\n"
        dynamic_config = await self._read_dynamic_config()

        for key in _DEFAULTS.keys():
            current_value = await self.get_config(key)

            source = " (默认)"
            if key in dynamic_config:
                source = " (动态)"
            elif hasattr(plugin_config, key) and getattr(plugin_config, key) != _DEFAULTS.get(key):
                source = " (.env)"

            msg += f"· {key}: {current_value}{source}\n"

        return msg.strip()


# 创建全局服务实例
config_service = ConfigService()