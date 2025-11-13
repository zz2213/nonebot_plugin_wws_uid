# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/handlers/alias.py

from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message
from nonebot.permission import SUPERUSER, GROUP_ADMIN, GROUP_OWNER
from nonebot.typing import T_State
from nonebot.matcher import Matcher

# 导入我们刚创建的服务实例
from ..services.alias_service import alias_service

# 权限设置：
# 只有超级用户、群主、群管理员可以操作
ADMIN_PERMISSION = SUPERUSER | GROUP_ADMIN | GROUP_OWNER

# --- 辅助函数 ---

async def parse_add_alias_args(matcher: Matcher, state: T_State, args: Message = CommandArg()):
    """解析添加别名的参数 (标准名 别名)"""
    arg_list = args.extract_plain_text().strip().split()
    if len(arg_list) != 2:
        await matcher.finish("参数格式错误，请发送：[标准名] [别名]")
        return
    state["standard_name"] = arg_list[0]
    state["alias"] = arg_list[1]


async def parse_del_alias_args(matcher: Matcher, state: T_State, args: Message = CommandArg()):
    """解析删除别名的参数 (别名)"""
    alias = args.extract_plain_text().strip()
    if not alias:
        await matcher.finish("参数格式错误，请发送：[别名]")
        return
    state["alias"] = alias

async def parse_find_alias_args(matcher: Matcher, state: T_State, args: Message = CommandArg()):
    """解析查找别名的参数 (名称)"""
    name = args.extract_plain_text().strip()
    if not name:
        await matcher.finish("参数格式错误，请发送：[名称]")
        return
    state["name"] = name


# --- 角色别名 ---

add_char_als = on_command("添加角色别名", permission=ADMIN_PERMISSION, priority=10, block=True, depends=[parse_add_alias_args])
del_char_als = on_command("删除角色别名", permission=ADMIN_PERMISSION, priority=10, block=True, depends=[parse_del_alias_args])
get_char_als = on_command("角色别名列表", priority=10, block=True)
find_char_als = on_command("查找角色别名", priority=10, block=True, depends=[parse_find_alias_args])

@add_char_als.handle()
async def _(matcher: Matcher, state: T_State):
    msg = await alias_service.add_char_alias(state["standard_name"], state["alias"])
    await matcher.finish(msg)

@del_char_als.handle()
async def _(matcher: Matcher, state: T_State):
    msg = await alias_service.del_char_alias(state["alias"])
    await matcher.finish(msg)

@get_char_als.handle()
async def _(matcher: Matcher):
    msg = await alias_service.get_char_alias_list()
    await matcher.finish(msg)

@find_char_als.handle()
async def _(matcher: Matcher, state: T_State):
    msg = await alias_service.find_char_alias(state["name"])
    await matcher.finish(msg)


# --- 武器别名 ---

add_weapon_als = on_command("添加武器别名", permission=ADMIN_PERMISSION, priority=10, block=True, depends=[parse_add_alias_args])
del_weapon_als = on_command("删除武器别名", permission=ADMIN_PERMISSION, priority=10, block=True, depends=[parse_del_alias_args])
get_weapon_als = on_command("武器别名列表", priority=10, block=True)
find_weapon_als = on_command("查找武器别名", priority=10, block=True, depends=[parse_find_alias_args])

@add_weapon_als.handle()
async def _(matcher: Matcher, state: T_State):
    msg = await alias_service.add_weapon_alias(state["standard_name"], state["alias"])
    await matcher.finish(msg)

@del_weapon_als.handle()
async def _(matcher: Matcher, state: T_State):
    msg = await alias_service.del_weapon_alias(state["alias"])
    await matcher.finish(msg)

@get_weapon_als.handle()
async def _(matcher: Matcher):
    msg = await alias_service.get_weapon_alias_list()
    await matcher.finish(msg)

@find_weapon_als.handle()
async def _(matcher: Matcher, state: T_State):
    msg = await alias_service.find_weapon_alias(state["name"])
    await matcher.finish(msg)


# --- 声骸别名 ---

add_echo_als = on_command("添加声骸别名", permission=ADMIN_PERMISSION, priority=10, block=True, depends=[parse_add_alias_args])
del_echo_als = on_command("删除声骸别名", permission=ADMIN_PERMISSION, priority=10, block=True, depends=[parse_del_alias_args])
get_echo_als = on_command("声骸别名列表", priority=10, block=True)
find_echo_als = on_command("查找声骸别名", priority=10, block=True, depends=[parse_find_alias_args])

@add_echo_als.handle()
async def _(matcher: Matcher, state: T_State):
    msg = await alias_service.add_echo_alias(state["standard_name"], state["alias"])
    await matcher.finish(msg)

@del_echo_als.handle()
async def _(matcher: Matcher, state: T_State):
    msg = await alias_service.del_echo_alias(state["alias"])
    await matcher.finish(msg)

@get_echo_als.handle()
async def _(matcher: Matcher):
    msg = await alias_service.get_echo_alias_list()
    await matcher.finish(msg)

@find_echo_als.handle()
async def _(matcher: Matcher, state: T_State):
    msg = await alias_service.find_echo_alias(state["name"])
    await matcher.finish(msg)


# --- 声骸套装别名 ---

add_sonata_als = on_command("添加套装别名", permission=ADMIN_PERMISSION, priority=10, block=True, depends=[parse_add_alias_args])
del_sonata_als = on_command("删除套装别名", permission=ADMIN_PERMISSION, priority=10, block=True, depends=[parse_del_alias_args])
get_sonata_als = on_command("套装别名列表", priority=10, block=True)
find_sonata_als = on_command("查找套装别名", priority=10, block=True, depends=[parse_find_alias_args])

@add_sonata_als.handle()
async def _(matcher: Matcher, state: T_State):
    msg = await alias_service.add_sonata_alias(state["standard_name"], state["alias"])
    await matcher.finish(msg)

@del_sonata_als.handle()
async def _(matcher: Matcher, state: T_State):
    msg = await alias_service.del_sonata_alias(state["alias"])
    await matcher.finish(msg)

@get_sonata_als.handle()
async def _(matcher: Matcher):
    msg = await alias_service.get_sonata_alias_list()
    await matcher.finish(msg)

@find_sonata_als.handle()
async def _(matcher: Matcher, state: T_State):
    msg = await alias_service.find_sonata_alias(state["name"])
    await matcher.finish(msg)