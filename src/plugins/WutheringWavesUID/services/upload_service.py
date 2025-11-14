# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/services/upload_service.py

from typing import Dict, Any, Optional
from nonebot.log import logger

# 导入服务
from ..services.game_service import GameService
from ..services.character_service import CharacterService
from ..core.api.ranking_api import ranking_api

# 导入 Framework A
from ..core.damage.damage import Damage as FrameworkA_Damage
from ..core.ascension.char import CharAscension
from ..core.ascension.weapon import WeaponAscension

# 导入 Framework B
from ..core.damage_buff.buff_engine import DamageAttribute, DamageAttributeData
from ..core.data.damage.register import WavesCharRegister
from ..core.utils.scoring import get_id_name_map


class UploadService:
    """
    面板上传服务
    (迁移自 wutheringwaves_master/__init__.py)
    """

    def __init__(self, game_service: GameService, char_service: CharacterService):
        self.game_service = game_service
        self.char_service = char_service
        self.id_name_map = get_id_name_map()

    def _get_name(self, key: str) -> str:
        return self.id_name_map.get(str(key), str(key))

    async def calculate_and_upload(self, cookie: str, uid: str) -> str:
        """
        执行计算并上传面板
        """
        logger.info(f"Starting panel upload for UID: {uid}")

        # 1. 获取所有角色的原始数据
        role_list_data = await self.game_service.get_role_info(cookie, uid)
        if not role_list_data or "roleList" not in role_list_data:
            return "获取角色列表失败，无法上传。"

        role_list = role_list_data.get("roleList", [])
        upload_payloads = []  # 最终上传的数据

        # 2. 遍历每个角色，执行 Framework A 和 Framework B
        for role in role_list:
            char_id = str(role.get("id"))
            logger.info(f"Processing character: {char_id}")

            try:
                # --- 运行 Framework A (面板属性计算) ---
                # (复用 character_service._refresh_char_detail)
                # (注意：_calc_echo_score 必须先运行)
                echos, total_score = self.char_service._calc_echo_score(char_id, role.get("echoList", []))
                role["echoList"] = echos  # 注入带分数的数据

                panel_stats: Dict[str, Any] = await self.char_service._refresh_char_detail(char_id, role)

                if "error" in panel_stats:
                    logger.warning(f"Framework A (Panel) failed for {char_id}: {panel_stats['error']}")
                    continue  # 跳过此角色

                # --- 运行 Framework B (团队 Buff & 期望伤害计算) ---

                # 2.1 查找该角色的 Framework B 计算脚本
                char_buff_calculator = WavesCharRegister.find_class(int(char_id))
                if not char_buff_calculator:
                    logger.info(f"Framework B script not found for {char_id}, skipping damage calc.")
                    expected_damage = 0.0
                else:
                    # 2.2 准备 Framework B 的输入
                    # 将 Framework A 的输出 转换为 Framework B 的输入
                    attr_input = DamageAttributeData(
                        name=role.get("name", ""),
                        uid=uid,
                        level=role.get("level", 90),
                        chain=role.get("resonanceLevel", 0),
                        char_attr=self._get_name(role.get("attributeType", "")),

                        # 从 Framework A 的结果 (panel_stats) 中获取
                        atk_base=panel_stats.get("角色基础攻击", 0.0) + panel_stats.get("武器基础攻击", 0.0),
                        atk_percent=panel_stats.get("攻击", 0.0),
                        atk_flat=panel_stats.get("攻击力", 0.0) - (
                                    panel_stats.get("角色基础攻击", 0.0) + panel_stats.get("武器基础攻击", 0.0)) * (
                                             1 + panel_stats.get("攻击", 0.0)),  # 反推固定攻击
                        crit_rate=panel_stats.get("暴击率", 0.0),
                        crit_dmg=panel_stats.get("暴击伤害", 0.0),
                        dmg_bonus=panel_stats.get(f"{self._get_name(role.get('attributeType', ''))}伤害加成", 0.0),
                        heal_bonus=panel_stats.get("治疗效果加成", 0.0),
                        energy=panel_stats.get("共鸣效率", 0.0),
                    )

                    attr = DamageAttribute(attr_input)

                    # 2.3 执行 Buff 计算
                    # (calc.json 的逻辑在原项目中由 gsuid_core 处理, 这里简化)
                    # 假设我们只计算角色自身的 buff
                    calculator_instance = char_buff_calculator(
                        char_id=int(char_id),
                        chain=role.get("resonanceLevel", 0),
                        resonLevel=role.get("weapon", {}).get("resonanceLevel", 1)
                    )
                    calculator_instance.do_action("buff", attr, isGroup=False)

                    # 2.4 计算期望伤害
                    # TODO: 伤害倍率 (rate) 应从 calc.json 加载
                    # 暂时使用一个固定的倍率 10.0 (1000%) 作为演示
                    damage_rate = 10.0
                    expected_damage_result = attr.get_damage_val(damage_rate, "期望伤害", expected=True)
                    expected_damage = expected_damage_result.get("val", 0.0)

                # 3. 构建该角色的上传数据
                upload_payloads.append({
                    "char_id": int(char_id),
                    "level": role.get("level"),
                    "chain": role.get("resonanceLevel"),
                    "weapon_id": role.get("weapon", {}).get("id"),
                    "weapon_level": role.get("weapon", {}).get("level"),
                    "weapon_reson_level": role.get("weapon", {}).get("resonanceLevel"),
                    "sonata_name": role.get("sonataList", [{}])[0].get("name", "") if role.get("sonataList") else "",
                    "phantom_score": total_score,
                    "expected_damage": expected_damage,
                    # ... 补全其他面板属性 ...
                    "attribute": role.get("attribute", [])
                })

            except Exception as e:
                logger.error(f"Failed processing character {char_id} for upload: {e}")
                logger.exception(e)

        # 4. 最终上传
        if not upload_payloads:
            return "没有可上传的角色数据。"

        final_upload_data = {
            "uid": uid,
            "role_list": upload_payloads,
            "user_id": uid,  # 兼容原 API
        }

        logger.info(f"Uploading panel data for {len(upload_payloads)} characters...")
        response = await ranking_api.upload_data(final_upload_data)

        if response.success:
            return f"面板上传成功！共上传 {len(upload_payloads)} 个角色数据。"
        else:
            return f"面板上传失败：{response.msg}"

# 创建全局服务实例
# (在 handlers 中再实例化)