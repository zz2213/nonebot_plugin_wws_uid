# 光主
from .damage import echo_damage, weapon_damage, phase_damage
from ...api.model import RoleDetailData
from ...ascension.char import WavesCharResult, get_char_detail2
from ...damage.damage import DamageAttribute
from ...damage.utils import (
    skill_damage_calc,
    SkillType,
    SkillTreeMap,
    cast_skill,
    cast_liberation,
    cast_hit,
    liberation_damage,
    skill_damage,
    cast_attack,
)


def calc_damage_1(
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False
) -> (str, str):
    # 设置角色伤害类型
    attr.set_char_damage(liberation_damage)
    # 设置角色模板  "temp_atk", "temp_life", "temp_def"
    attr.set_char_template("temp_atk")

    role_name = role.role.roleName
    # 获取角色详情
    char_result: WavesCharResult = get_char_detail2(role)

    skill_type: SkillType = "共鸣解放"
    # 获取角色技能等级
    skillLevel = role.get_skill_level(skill_type)
    # 技能技能倍率
    skill_multi = skill_damage_calc(
        char_result.skillTrees, SkillTreeMap[skill_type], "1", skillLevel
    )
    title = f"回响奏鸣"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_skill, cast_hit, cast_liberation]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色固有技能
    role_breach = role.role.breach
    if role_breach and role_breach >= 3:
        title = f"{role_name}-固有技能-重击·鸣奏"
        msg = f"施放重击鸣奏后，漂泊者的攻击提升15%"
        attr.add_atk_percent(0.15, title, msg)

    # 设置角色技能施放是不是也有加成 eg：守岸人

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置共鸣链
    chain_num = role.get_chain_num()
    if chain_num >= 1:
        title = f"{role_name}-一链"
        msg = f"施放共鸣技能时，漂泊者的暴击提升15%"
        attr.add_crit_rate(0.15, title, msg)

    if chain_num >= 2:
        title = f"{role_name}-二链"
        msg = f"漂泊者的衍射伤害加成提升20%。"
        attr.add_dmg_bonus(0.2, title, msg)

    if chain_num >= 5:
        title = f"{role_name}-五链"
        msg = f"共鸣解放伤害加成提升40%。"
        attr.add_dmg_bonus(0.4, title, msg)

    if chain_num >= 6:
        title = f"{role_name}-六链"
        msg = f"共鸣技能命中目标时，目标衍射伤害抗性降低10%"
        attr.add_enemy_resistance(-0.1, title, msg)

    # 声骸
    echo_damage(attr, isGroup)

    # 武器
    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    # 暴击伤害
    crit_damage = f"{attr.calculate_crit_damage():,.0f}"
    # 期望伤害
    expected_damage = f"{attr.calculate_expected_damage():,.0f}"
    return crit_damage, expected_damage


def calc_damage_2(
    attr: DamageAttribute, role: RoleDetailData, isGroup: bool = False
) -> (str, str):
    # 设置角色伤害类型
    attr.set_char_damage(skill_damage)
    # 设置角色模板  "temp_atk", "temp_life", "temp_def"
    attr.set_char_template("temp_atk")

    role_name = role.role.roleName
    # 获取角色详情
    char_result: WavesCharResult = get_char_detail2(role)

    skill_type: SkillType = "共鸣回路"
    # 获取角色技能等级
    skillLevel = role.get_skill_level(skill_type)
    # 技能技能倍率
    skill_multi = skill_damage_calc(
        char_result.skillTrees, SkillTreeMap[skill_type], "1", skillLevel
    )
    title = f"浮声千斩·旋音伤害"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    skill_multi = skill_damage_calc(
        char_result.skillTrees, SkillTreeMap[skill_type], "2", skillLevel
    )
    title = f"浮声千斩·旋音飞轮伤害"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    skill_multi = skill_damage_calc(
        char_result.skillTrees, SkillTreeMap[skill_type], "3", skillLevel
    )
    title = f"浮声千斩·回声一段伤害"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    skill_multi = skill_damage_calc(
        char_result.skillTrees, SkillTreeMap[skill_type], "4", skillLevel
    )
    title = f"浮声千斩·回声二段伤害"
    msg = f"技能倍率{skill_multi}"
    attr.add_skill_multi(skill_multi, title, msg)

    # 设置角色施放技能
    damage_func = [cast_skill, cast_attack, cast_hit]
    phase_damage(attr, role, damage_func, isGroup)

    # 设置角色等级
    attr.set_character_level(role.role.level)

    # 设置角色固有技能
    role_breach = role.role.breach
    if role_breach and role_breach >= 3:
        title = f"{role_name}-固有技能-重击·鸣奏"
        msg = f"施放重击鸣奏后，漂泊者的攻击提升15%"
        attr.add_atk_percent(0.15, title, msg)

        title = f"{role_name}-固有技能-重击·鸣鸣"
        msg = f"共鸣技能浮声千斩·回声的伤害提升60%"
        attr.add_dmg_bonus(0.6, title, msg)

    # 设置角色技能施放是不是也有加成 eg：守岸人

    # 设置声骸属性
    attr.set_phantom_dmg_bonus()

    # 设置共鸣链
    chain_num = role.get_chain_num()
    if chain_num >= 1:
        title = f"{role_name}-一链"
        msg = f"施放共鸣技能时，漂泊者的暴击提升15%"
        attr.add_crit_rate(0.15, title, msg)

    if chain_num >= 2:
        title = f"{role_name}-二链"
        msg = f"漂泊者的衍射伤害加成提升20%。"
        attr.add_dmg_bonus(0.2, title, msg)

    if chain_num >= 6:
        title = f"{role_name}-六链"
        msg = f"共鸣技能命中目标时，目标衍射伤害抗性降低10%"
        attr.add_enemy_resistance(-0.1, title, msg)

    # 声骸
    echo_damage(attr, isGroup)

    # 武器
    weapon_damage(attr, role.weaponData, damage_func, isGroup)

    # 暴击伤害
    crit_damage = f"{attr.calculate_crit_damage():,.0f}"
    # 期望伤害
    expected_damage = f"{attr.calculate_expected_damage():,.0f}"
    return crit_damage, expected_damage


damage_detail = [
    {
        "title": "回响奏鸣",
        "func": lambda attr, role: calc_damage_1(attr, role),
    },
    {
        "title": "强化e-浮声千斩总伤",
        "func": lambda attr, role: calc_damage_2(attr, role),
    },
]

rank = damage_detail[1]
