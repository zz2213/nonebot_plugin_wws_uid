from typing import Dict, Optional

from pydantic import BaseModel

from ..utils.api.model import RoleDetailData
from .calc import WuWaCalc
from .calculate import calc_phantom_score, get_calc_map, get_total_score_bg
from .char_info_utils import get_all_role_detail_info
from .damage.abstract import DamageRankRegister
from .damage.utils import comma_separated_number


class WavesCharRank(BaseModel):
    roleId: int  # 角色id
    roleName: str  # 角色名字
    starLevel: int  # 角色星级
    level: int  # 角色等级
    chain: int  # 命座
    chainName: str  # 命座
    score: float  # 角色评分
    score_bg: str  # 评分背景
    expected_damage: Optional[float]  # 期望伤害

    weaponId: int  # 武器id
    weaponLevel: int  # 武器等级
    weaponResonLevel: int  # 武器共鸣等级
    sonataName: str  # 合鸣效果
    expected_name: str  # 期望伤害名字

    def to_rank_dict(self):
        return {
            "char_id": self.roleId,
            "level": self.level,
            "chain": self.chain,
            "weapon_id": self.weaponId,
            "weapon_level": self.weaponLevel,
            "weapon_reson_level": self.weaponResonLevel,
            "sonata_name": self.sonataName,
            "phantom_score": self.score,
            "phantom_score_bg": self.score_bg,
            "expected_damage": self.expected_damage if self.expected_damage else 0,
            "expected_name": self.expected_name if self.expected_name else "",
        }


async def get_waves_char_rank(uid, all_role_detail, need_expected_damage=False):
    if not all_role_detail:
        all_role_detail = await get_all_role_detail_info(uid)
    if isinstance(all_role_detail, Dict):
        temp = all_role_detail.values()
    else:
        temp = all_role_detail if all_role_detail else []
    waves_char_rank = []
    for role_detail in temp:
        if not isinstance(role_detail, RoleDetailData):
            role_detail = RoleDetailData(**role_detail)

        phantom_score = 0
        calc: WuWaCalc = WuWaCalc(role_detail)
        # calc_temp = None
        expected_damage = None

        sonataName = ""
        expected_name = ""
        if role_detail.phantomData and role_detail.phantomData.equipPhantomList:
            equipPhantomList = role_detail.phantomData.equipPhantomList

            calc.phantom_pre = calc.prepare_phantom()
            calc.phantom_card = calc.enhance_summation_phantom_value(calc.phantom_pre)
            calc.calc_temp = get_calc_map(
                calc.phantom_card,
                role_detail.role.roleName,
                role_detail.role.roleId,
            )
            for i, _phantom in enumerate(equipPhantomList):
                if _phantom and _phantom.phantomProp:
                    props = _phantom.get_props()
                    _score, _bg = calc_phantom_score(
                        role_detail.role.roleId, props, _phantom.cost, calc.calc_temp
                    )
                    phantom_score += _score

            if need_expected_damage:
                rankDetail = DamageRankRegister.find_class(str(role_detail.role.roleId))
                if rankDetail:
                    calc.role_card = calc.enhance_summation_card_value(
                        calc.phantom_card
                    )
                    calc.damageAttribute = calc.card_sort_map_to_attribute(
                        calc.role_card
                    )
                    _, expected_damage = rankDetail["func"](
                        calc.damageAttribute, role_detail
                    )
                    expected_damage = comma_separated_number(expected_damage)
                    expected_name = rankDetail["title"]

            for ph_detail in calc.phantom_pre.get("ph_detail", []):
                if ph_detail.get("ph_name") and ph_detail.get("ph_num") == 5:
                    sonataName = ph_detail["ph_name"]
                    break

                if ph_detail.get("ph_name") and ph_detail.get("isFull"):
                    sonataName = ph_detail["ph_name"]
                    break

        phantom_score = round(phantom_score, 2)
        wcr = WavesCharRank(
            **{
                "roleId": role_detail.role.roleId,
                "roleName": role_detail.role.roleName,
                "starLevel": role_detail.role.starLevel,
                "level": role_detail.level,
                "chain": role_detail.get_chain_num(),
                "chainName": role_detail.get_chain_name(),
                "score": phantom_score,
                "score_bg": get_total_score_bg(
                    role_detail.role.roleName, phantom_score, calc.calc_temp
                ),
                "expected_damage": expected_damage,
                "weaponId": role_detail.weaponData.weapon.weaponId,
                "weaponLevel": role_detail.weaponData.level,
                "weaponResonLevel": role_detail.weaponData.resonLevel,
                "sonataName": sonataName,
                "expected_name": expected_name,
            }
        )
        waves_char_rank.append(wcr)

    return waves_char_rank
