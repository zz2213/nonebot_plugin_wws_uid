"""
GenshinUID Core 兼容层 (Shim) V4

此文件仅模拟 gsuid_core 的 Bot, Event, SV 和 Handler 逻辑。
(V4: 修复了 Any cannot be instantiated 错误，并移除了 handler 的前缀检查)
"""
import re
from typing import Any, Dict, List, Optional, Tuple, Callable, Union

# -------------------------------------------------------------------
# 1. 从 NoneBot 插件内部导入
# -------------------------------------------------------------------
from nonebot import logger as nb_logger, get_driver

# -------------------------------------------------------------------
# 2. 模拟 gsuid_core 的命令注册 (sv.py)
# -------------------------------------------------------------------

_sv_list: List["SV"] = []
"""存储所有 SV 实例"""

class Command:
    """模拟 gsuid_core.sv.Command 类，存储命令元数据"""
    def __init__(
        self,
        name: Union[str, list[str]],
        func: Callable,
        priority: int,
        pm: int,
        area: str,
    ):
        self.name = [name] if isinstance(name, str) else name
        self.func = func
        self.priority = priority
        self.pm = pm
        self.area = area
        self.aliases = self.name
        self.rex = [
            re.compile(f"^{re.escape(x)}$", re.I) for x in self.name
        ]

class SV:
    """
    模拟 gsuid_core.sv.SV 类
    完整支持 on_command 及其所有参数 (priority, pm, area)
    """
    def __init__(
        self,
        name: str,
        priority: int = 10,
        pm: int = 6,
        area: str = "ALL",
    ):
        self.name = name
        self.priority = priority
        self.pm = pm
        self.area = area
        self.commands: List[Command] = []
        _sv_list.append(self)
        nb_logger.info(f"[Shim] 注册服务: {name}")

    def on_command(
        self,
        name: Union[str, list[str]],
        priority: Optional[int] = None,
        pm: Optional[int] = None,
        area: Optional[str] = None,
    ) -> Callable:
        """
        模拟 on_command 装饰器
        """
        def decorator(func: Callable) -> Callable:
            self.commands.append(
                Command(
                    name=name,
                    func=func,
                    priority=priority or self.priority,
                    pm=pm or self.pm,
                    area=area or self.area,
                )
            )
            nb_logger.debug(f"[Shim] 服务 {self.name} 注册命令: {name}")
            return func
        return decorator

# -------------------------------------------------------------------
# 3. 模拟 gsuid_core 的 Bot 和 Event (models.py, bot.py)
# -------------------------------------------------------------------
class Bot:
    """模拟 gsuid_core.bot.Bot 类"""
    def __init__(self, msg_receive: Any): # 使用 Any 避免导入 MessageReceive
        self.bot_id = msg_receive.bot_id
        self.bot_self_id = msg_receive.bot_self_id
        # 为 login.py 中错误的 bot.send 调用提供 fallback
        self._shim_event: "Event" | None = None

    async def send(
        self,
        message: Union[str, List[Any]], # 兼容 MessageSegment
        ev: Optional["Event"] = None, # 允许 ev 为 None
        at_sender: bool = False,
        message_type: str = "text",
        **kwargs
    ) -> None:
        """
        模拟 Bot.send()。
        """

        # [FIX] 在函数内部导入，避免启动时循环依赖
        from .entity.pack import Message, MessageSend
        from .client import call_bot

        _ev_instance = ev or self._shim_event
        if not _ev_instance:
             nb_logger.error("[Shim] bot.send() 调用失败：缺少 'ev' 参数。")
             return

        if _ev_instance.group_id:
            target_id = _ev_instance.group_id
            target_type = _ev_instance.user_type
        elif _ev_instance.user_id:
            target_id = _ev_instance.user_id
            target_type = _ev_instance.user_type
        else:
            nb_logger.warning("[Shim] 无法确定目标ID，跳过发送消息。")
            return

        content_list: List[Message] = []

        # 1. 处理 @sender
        if at_sender and _ev_instance.user_id and target_type != "direct":
            content_list.append(Message(type="at", data=_ev_instance.user_id))

        # 2. 添加消息内容
        msg_list = message if isinstance(message, list) else [message]

        for item in msg_list:
            # 假设 item 是 gsuid_core.segment.MessageSegment 实例 (由您复制)
            if hasattr(item, "type") and hasattr(item, "data"):
                if item.type == "node":
                    nb_logger.warning("[Shim] 节点消息 (node) 已被简化为文本发送。")
                    content_list.append(Message(type="text", data="[节点消息] " + str(item.data)))
                else:
                    content_list.append(Message(type=item.type, data=item.data))
            elif isinstance(item, str):
                 content_list.append(Message(type="text", data=item))
            else:
                content_list.append(Message(type="text", data=str(item)))

        # 3. 创建 MessageSend 并发送
        msg_send = MessageSend(
            bot_id=self.bot_id,
            bot_self_id=self.bot_self_id,
            target_type=target_type,
            target_id=target_id,
            content=content_list,
        )

        await call_bot(msg_send)

class Event:
    """模拟 gsuid_core.models.Event 类"""
    def __init__(self, msg_receive: Any, raw_command_text: str): # 使用 Any 避免导入 MessageReceive
        self._msg = msg_receive

        # 暴露核心逻辑需要的属性
        self.user_id: Optional[str] = msg_receive.user_id
        self.bot_id: str = msg_receive.bot_id
        self.group_id: Optional[str] = msg_receive.group_id
        self.text: str = raw_command_text # 包含命令和参数的文本
        self.user_type: str = msg_receive.user_type
        self.sender: dict = msg_receive.sender # 暴露 sender
        self.user_pm: int = msg_receive.user_pm # 暴露 user_pm

    @property
    def is_group(self) -> bool:
        return self.user_type == "group"

# -------------------------------------------------------------------
# 4. 模拟 gsuid_core 的命令处理器 (handler.py)
# -------------------------------------------------------------------

async def shim_command_handler(bot: Bot, ev: Event):
    """
    模拟 gsuid_core.handler.handle_message 逻辑。
    (V4: 已移除前缀检查，假定 ev.text 是干净的命令)
    """

    # 假设 ev.text 已经是剥离前缀后的文本 (例如: "登录 123,456")
    msg_text = ev.text.lstrip()

    # 提取命令词
    cmd_name = msg_text.split(" ", 1)[0]
    if not cmd_name:
        return

    # ---------------------------------------------------------------
    # 模拟 gsuid_core 的 优先级、权限、区域 检查
    # ---------------------------------------------------------------

    # 1. 筛选所有匹配的命令，并按优先级排序
    matched_commands: List[Command] = []
    for sv in _sv_list:
        for cmd in sv.commands:
            for rex in cmd.rex:
                if rex.match(cmd_name):
                    matched_commands.append(cmd)
                    break # 匹配到此命令即停止

    if not matched_commands:
        nb_logger.debug(f"[Shim Handler] 未匹配到命令: {cmd_name}")
        return

    # 按优先级排序 (priority 越小越优先)
    matched_commands.sort(key=lambda x: x.priority)

    # 2. 依次执行检查
    for cmd in matched_commands:
        # 检查权限 (pm)
        if ev.user_pm > cmd.pm:
            nb_logger.debug(f"[Shim Handler] 命令 {cmd.name[0]} 权限不足 (Ev:{ev.user_pm} > Cmd:{cmd.pm})")
            continue # 权限不足，尝试下一个

        # 检查区域 (area)
        if cmd.area == "GROUP" and ev.user_type != "group":
            nb_logger.debug(f"[Shim Handler] 命令 {cmd.name[0]} 仅限群组")
            continue
        if cmd.area == "DIRECT" and ev.user_type != "direct":
            nb_logger.debug(f"[Shim Handler] 命令 {cmd.name[0]} 仅限私聊")
            continue

        # -----------------------------------------------------------
        # 检查通过，执行命令
        # -----------------------------------------------------------
        nb_logger.info(
            f"[Shim Handler] 执行命令: {cmd.name[0]} (Prio: {cmd.priority}, PM: {cmd.pm}, Area: {cmd.area})"
        )
        try:
            # 传递原始的、去除了前缀的文本 (ev.text)
            ev.text = msg_text # 更新 ev.text 为去除前缀的完整命令
            await cmd.func(bot, ev)
            return # 成功执行后终止
        except Exception as e:
            nb_logger.exception(f"[Shim Handler] 执行命令 {cmd.name[0]} 出错: {e}")
            await bot.send(f"执行命令 {cmd.name[0]} 时发生内部错误: {e}", ev)
            return # 出错后终止