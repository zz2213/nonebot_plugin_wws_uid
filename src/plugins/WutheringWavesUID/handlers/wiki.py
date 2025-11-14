# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/handlers/wiki.py

from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, MessageSegment, MessageEvent
from nonebot.matcher import Matcher
from nonebot.log import logger

# 导入我们刚创建的服务和绘图函数
from ..services.wiki_service import wiki_service
from ..core.drawing.wiki_card import (
    draw_char_wiki, draw_weapon_wiki, draw_echo_wiki, draw_sonata_wiki
)
from ..core.utils.image import pil_to_img_msg

char_wiki_cmd = on_command("角色图鉴", aliases={"角色"}, priority=11, block=True)
weapon_wiki_cmd = on_command("武器图鉴", aliases={"武器"}, priority=11, block=True)
echo_wiki_cmd = on_command("声骸图鉴", aliases={"声骸"}, priority=11, block=True)
guide_cmd = on_command("攻略", aliases={"gl"}, priority=11, block=True)


async def _get_name(matcher: Matcher, args: Message = CommandArg()) -> str:
    """辅助函数：从参数中提取名称"""
    name = args.extract_plain_text().strip()
    if not name:
        await matcher.finish("请输入要查询的名称。")
    return name


@char_wiki_cmd.handle()
async def _(matcher: Matcher, args: Message = CommandArg()):
    """处理 角色图鉴 命令"""
    name = await _get_name(matcher, args)

    await matcher.send(f"正在查询角色「{name}」的图鉴资料...")

    try:
        # wiki_service 内部已集成别名查询
        data = await wiki_service.get_char_wiki_data(name)
        if not data:
            await matcher.finish(f"未查询到角色「{name}」的图鉴数据。")
            return

        image = await draw_char_wiki(data)
        if image:
            await matcher.finish(pil_to_img_msg(image, format="JPEG"))
        else:
            await matcher.finish("绘制角色图鉴失败。")

    except Exception as e:
        logger.error(f"char_wiki_cmd failed: {e}")
        await matcher.finish(f"查询时发生内部错误：{e}")


@weapon_wiki_cmd.handle()
async def _(matcher: Matcher, args: Message = CommandArg()):
    """处理 武器图鉴 命令"""
    name = await _get_name(matcher, args)

    await matcher.send(f"正在查询武器「{name}」的图鉴资料...")

    try:
        # wiki_service 内部已集成别名查询
        data = await wiki_service.get_weapon_wiki_data(name)
        if not data:
            await matcher.finish(f"未查询到武器「{name}」的图鉴数据。")
            return

        image = await draw_weapon_wiki(data)
        if image:
            await matcher.finish(pil_to_img_msg(image, format="JPEG"))
        else:
            await matcher.finish("绘制武器图鉴失败。")

    except Exception as e:
        logger.error(f"weapon_wiki_cmd failed: {e}")
        await matcher.finish(f"查询时发生内部错误：{e}")


@echo_wiki_cmd.handle()
async def _(matcher: Matcher, args: Message = CommandArg()):
    """
    处理 声骸图鉴 命令
    (自动区分套装和怪物)
    """
    name = await _get_name(matcher, args)
    await matcher.send(f"正在查询声骸「{name}」的图鉴资料...")

    try:
        # 1. 优先尝试搜索套装 (wiki_service 内部已集成别名查询)
        sonata_data = await wiki_service.get_sonata_wiki_data(name)
        if sonata_data:
            image = await draw_sonata_wiki(sonata_data)
            if image:
                await matcher.finish(pil_to_img_msg(image, format="JPEG"))
            else:
                await matcher.finish("绘制声骸套装图鉴失败。")
            return

        # 2. 尝试搜索单个声骸 (wiki_service 内部已集成别名查询)
        echo_data = await wiki_service.get_echo_wiki_data(name)
        if echo_data:
            image = await draw_echo_wiki(echo_data)
            if image:
                await matcher.finish(pil_to_img_msg(image, format="JPEG"))
            else:
                await matcher.finish("绘制声骸图鉴失败。")
            return

        # 3. 都没找到
        await matcher.finish(f"未查询到声骸或套装「{name}」的图鉴数据。")

    except Exception as e:
        logger.error(f"echo_wiki_cmd failed: {e}")
        await matcher.finish(f"查询时发生内部错误：{e}")


@guide_cmd.handle()
async def _(matcher: Matcher, args: Message = CommandArg()):
    """
    处理 攻略 命令
    """
    name = await _get_name(matcher, args)
    await matcher.send(f"正在获取「{name}」的攻略图...")

    try:
        # wiki_service.get_guide_image 内部已集成别名查询
        image_bytes = await wiki_service.get_guide_image(name)

        if image_bytes:
            await matcher.finish(MessageSegment.image(image_bytes))
        else:
            await matcher.finish(f"未能在图源中找到「{name}」的攻略图。")

    except Exception as e:
        logger.error(f"guide_cmd failed: {e}")
        await matcher.finish(f"获取攻略图时发生内部错误：{e}")