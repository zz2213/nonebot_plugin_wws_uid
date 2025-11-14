# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/core/damage_buff/load_scripts.py
# (原名 register.py, 迁移自 WutheringWavesUID1/utils/map/damage/register.py)

import importlib
import importlib.util
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Type

# 适配修改：
from .models import CharAbstract, WeaponAbstract, DamageAttribute
from nonebot.log import logger

# --- 适配结束 ---

# 适配修改：路径指向 core/data/damage/ (存放 damage_XXXX.py 脚本)
SCRIPT_PATH = Path(__file__).parent.parent / "data" / "damage"


class WavesRegister:
    def __init__(self) -> None:
        self.classes: Dict[
            int, Type[Union[CharAbstract, WeaponAbstract]]
        ] = {}
        self.script_loaded = False

    def register_class(
            self,
            class_id: int,
            clz: Type[Union[CharAbstract, WeaponAbstract]],
    ):
        if class_id in self.classes:
            logger.warning(
                f"[Framework B] Duplicate class id: {class_id} "
                f"old: {self.classes[class_id].__name__} "
                f"new: {clz.__name__}"
            )
        self.classes[class_id] = clz

    def find_class(
            self, class_id: int
    ) -> Optional[Type[Union[CharAbstract, WeaponAbstract]]]:
        self.load_all_script()
        return self.classes.get(class_id, None)

    def load_all_script(self):
        if self.script_loaded:
            return
        self.script_loaded = True

        logger.info(f"[Framework B] Loading damage scripts from: {SCRIPT_PATH}")

        for file in SCRIPT_PATH.glob("damage_*.py"):
            try:
                # 适配修改：使用 importlib 动态加载 .py 文件
                module_name = file.stem
                # 必须给一个唯一的 module name
                module_qualname = f"nonebot_plugin_wws_uid.dynamic_damage_scripts.{module_name}"

                spec = importlib.util.spec_from_file_location(
                    module_qualname,
                    file
                )
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    if hasattr(module, "register_char"):
                        module.register_char()
                    if hasattr(module, "register_weapon"):
                        module.register_weapon()
                    # logger.debug(f"[Framework B] Loaded damage script: {file.name}")

            except Exception as e:
                logger.error(f"[Framework B] Failed to load script {file.name}: {e}")
                logger.exception(e)

        logger.info(f"[Framework B] Loaded {len(self.classes)} damage scripts.")


WavesCharRegister = WavesRegister()
WavesWeaponRegister = WavesRegister()
WavesEchoRegister = WavesRegister()  # 暂不使用，但保留
WavesSonataRegister = WavesRegister()  # 暂不使用，但保留


def register_char(
        char_id: int,
) -> Callable[
    [Type[CharAbstract]], Type[CharAbstract]
]:
    def decorator(
            clz: Type[CharAbstract],
    ) -> Type[CharAbstract]:
        WavesCharRegister.register_class(char_id, clz)
        return clz

    return decorator


def register_weapon(
        weapon_id: int,
) -> Callable[
    [Type[WeaponAbstract]], Type[WeaponAbstract]
]:
    def decorator(
            clz: Type[WeaponAbstract],
    ) -> Type[WeaponAbstract]:
        WavesWeaponRegister.register_class(weapon_id, clz)
        return clz

    return decorator


def get_char(char_id: int) -> Optional[Type[CharAbstract]]:
    return WavesCharRegister.find_class(char_id)


def get_weapon(weapon_id: int) -> Optional[Type[WeaponAbstract]]:
    return WavesWeaponRegister.find_class(weapon_id)