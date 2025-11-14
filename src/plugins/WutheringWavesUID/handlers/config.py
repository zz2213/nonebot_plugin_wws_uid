# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/handlers/config.py

from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message
from nonebot.matcher import Matcher
from nonebot.permission import SUPERUSER, GROUP_ADMIN, GROUP_OWNER
from nonebot.log import logger

# 导入我们刚创建的服务
from ..services.config_service import config_service

# 权限：仅限超级用户和群管理
ADMIN_PERMISSION = SUPERUSER | GROUP_ADMIN | GROUP_OWNER

set_config_cmd = on_command("设置配置", aliases={"wws set"}, priority=5, block=True, permission=ADMIN_PERMISSION)
show_config_cmd = on_command("查看配置", aliases={"wws config"}, priority=5, block=True, permission=ADMIN_PERMISSION)
reset_config_cmd = on_command("重置配置", aliases={"wws reset"}, priority=5, block=True, permission=ADMIN_PERMISSION)


@set_config_cmd.handle()
async def _(matcher: Matcher, args: Message = CommandArg()):
    """
    处理 设置配置 命令
    (迁移自 wutheringwaves_config/set_config.py)
    """
    arg_list = args.extract_plain_text().strip().split()

    if len(arg_list) != 2:
        await matcher.finish("❌ 参数格式错误。\n用法: 设置配置 [配置项] [值]\n"
                             "例如: 设置配置 WAVES_BLUR_RADIUS 10\n"
                             "例如: 设置配置 WAVES_OPEN_WIKI 关闭")
        return

    key, value = arg_list[0], arg_list[1]

    try:
        result_msg = await config_service.set_config(key, value)
        await matcher.finish(result_msg)

    except Exception as e:
        logger.error(f"set_config_cmd failed: {e}")
        await matcher.finish(f"设置时发生内部错误：{e}")


@reset_config_cmd.handle()
async def _(matcher: Matcher, args: Message = CommandArg()):
    """
    处理 重置配置 命令
    """
    key = args.extract_plain_text().strip()

    if not key:
        await matcher.finish("❌ 参数格式错误。\n用法: 重置配置 [配置项]\n"
                             "例如: 重置配置 WAVES_BLUR_RADIUS")
        return

    try:
        result_msg = await config_service.reset_config(key)
        await matcher.finish(result_msg)

    except Exception as e:
        logger.error(f"reset_config_cmd failed: {e}")
        await matcher.finish(f"重置时发生内部错误：{e}")


@show_config_cmd.handle()
async def _(matcher: Matcher):
    """
    处理 查看配置 命令
    (迁移自 wutheringwaves_config/show_config.py)
    """
    try:
        config_str = await config_service.get_all_configs_str()
        await matcher.finish(config_str)

    except Exception as e:
        logger.error(f"show_config_cmd failed: {e}")
        await matcher.finish(f"查询时发生内部错误：{e}")