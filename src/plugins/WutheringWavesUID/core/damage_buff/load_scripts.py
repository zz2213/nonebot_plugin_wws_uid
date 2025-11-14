# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/core/damage_buff/load_scripts.py

import importlib
import pkgutil
from pathlib import Path
from nonebot.log import logger

# 导入 Framework B 的核心类
from .buff_engine import CharAbstract, DamageAttribute, WavesWeaponRegister

# 导入 Framework B 的注册器
from ..data.damage.register import WavesCharRegister

# 导入 Framework A 的相关工具 (旧脚本会 import)
from ..core.damage.abstract import DamageAbstract
from ..core.damage.damage import Damage
from ..core.damage.utils import get_damage_data
from ..core.utils.util import sync_dict


def load_all_damage_scripts():
    """
    动态加载 core/data/damage/ 目录下的所有 damage_*.py 脚本
    """

    # 路径指向 .../core/data/damage
    scripts_path = Path(__file__).parent.parent / "data" / "damage"
    # 转换为 Python 模块路径
    module_prefix = "nonebot_plugin_wws_uid.src.plugins.WutheringWavesUID.core.data.damage"

    logger.info("Start loading damage buff scripts (Framework B)...")

    loaded_count = 0
    for finder, name, ispkg in pkgutil.iter_modules([str(scripts_path)]):
        if name.startswith("damage_"):
            try:
                module_name = f"{module_prefix}.{name}"

                # --- 关键的猴子补丁 ---
                # 旧脚本 (damage_1102.py) 错误地导入了:
                # from ...utils.damage.abstract import CharAbstract
                #
                # 我们必须在它导入之前，
                # 手动将我们正确的 CharAbstract (Framework B)
                # 注入到它试图导入的模块 (Framework A) 中。

                from ...core.damage import abstract as framework_a_abstract

                # 将 Framework B 的类，注入到 Framework A 的模块中
                setattr(framework_a_abstract, "CharAbstract", CharAbstract)
                setattr(framework_a_abstract, "WavesCharRegister", WavesCharRegister)
                setattr(framework_a_abstract, "WavesWeaponRegister", WavesWeaponRegister)
                setattr(framework_a_abstract, "DamageAttribute", DamageAttribute)

                # --- 补丁结束 ---

                importlib.import_module(module_name)
                loaded_count += 1
            except ImportError as e:
                logger.error(f"Failed to import damage script {name}: {e}")
            except Exception as e:
                logger.error(f"Error loading damage script {name}: {e}")

    logger.info(f"Loaded {loaded_count} damage buff scripts.")


# 在插件加载时执行一次
load_all_damage_scripts()