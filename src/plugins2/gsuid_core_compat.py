"""
GenshinUID Core 兼容层 (Shim)

此文件模拟 gsuid_core 的内部 API，以最小的改动迁移核心插件。
它将 gsuid_core 的调用（如 bot.send）转换为 nonebot-plugin-genshinuid 的内部调用（call_bot）。
"""
import asyncio
import base64
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Callable, Union

# -------------------------------------------------------------------
# 1. 从 NoneBot 插件内部导入
# -------------------------------------------------------------------
from nonebot import logger as nb_logger, get_app, get_driver
from pydantic import BaseModel
from starlette.responses import HTMLResponse

# 导入 sayu_protocol 和 client 的 call_bot
# 注意：这里我们使用 try...except 来防止循环导入
try:
    from .sayu_protocol.pack import Message, MessageReceive, MessageSend
    from .client import call_bot
except ImportError:
    nb_logger.warning("Shim Layer 预导入失败，可能是启动顺序问题。")
    Message = Any
    MessageReceive = Any
    MessageSend = Any
    call_bot = None

# -------------------------------------------------------------------
# 2. 模拟 gsuid_core 的命令注册 (sv.py)
# -------------------------------------------------------------------
COMMAND_HANDLERS: Dict[str, Callable[..., Any]] = {}
"""全局命令注册表，存储 { "命令名": 对应函数}"""

class CommandRegistry:
    """模拟 sv_kuro_login 对象与 on_command 装饰器。"""
    def on_command(self, commands: Tuple[str, ...]):
        def decorator(func: Callable[..., Any]):
            # 注册所有命令别名到同一个处理函数
            for alias in commands:
                COMMAND_HANDLERS[alias] = func
                nb_logger.debug(f"[Shim] 注册命令: {alias}")
            return func
        return decorator

# 模拟 gsuid_core.compat.command_sv.sv_kuro_login
sv_kuro_login = CommandRegistry()
waves_bind_uid = CommandRegistry()
waves_add_ck = CommandRegistry()
waves_del_ck = CommandRegistry()
waves_get_ck = CommandRegistry()
waves_del_all_invalid_ck = CommandRegistry()


# -------------------------------------------------------------------
# 3. 模拟 gsuid_core 的 Bot 和 Event (models.py, bot.py)
# -------------------------------------------------------------------
class Bot:
    """模拟 gsuid_core.bot.Bot 类"""
    def __init__(self, msg_receive: MessageReceive):
        self.bot_id = msg_receive.bot_id
        self.bot_self_id = msg_receive.bot_self_id
        # 为 login.py 中错误的 bot.send 调用提供 fallback
        self._shim_event: "Event" | None = None

    async def send(
        self,
        message: Union[str, List[str]],
        ev: Optional["Event"] = None, # 允许 ev 为 None
        at_sender: bool = False,
        message_type: str = "text",
        **kwargs
    ) -> None:
        """
        模拟 Bot.send()。
        兼容 login.py 中 `bot.send(msg, at_sender=True)` (缺少 ev) 的调用方式。
        """

        # 兼容 login.py 中不传入 ev 的情况
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
        if isinstance(message, list):
            # 处理节点消息或多条消息
            for item in message:
                if isinstance(item, str) and item.startswith("[IMAGE:"):
                    # 解析 MessageSegment.image 模拟
                    img_data = item.split(":", 1)[1]
                    content_list.append(Message(type="image", data=img_data))
                elif isinstance(item, str):
                    content_list.append(Message(type="text", data=item))
        elif isinstance(message, str):
             if message.startswith("[NODE:"):
                 # 解析 MessageSegment.node 模拟
                 # 在 sayu_protocol 中没有原生节点消息，简化为文本
                 nb_logger.warning("[Shim] 节点消息 (node) 已被简化为文本发送。")
                 content_list.append(Message(type="text", data="[节点消息] " + str(message[6:-1])))
             elif message.startswith("[IMAGE:"):
                 # 解析 MessageSegment.image 模拟
                 img_data = message.split(":", 1)[1]
                 content_list.append(Message(type="image", data=img_data))
             else:
                 content_list.append(Message(type="text", data=message))

        # 3. 创建 MessageSend 并发送
        msg_send = MessageSend(
            bot_id=self.bot_id,
            bot_self_id=self.bot_self_id,
            target_type=target_type,
            target_id=target_id,
            content=content_list,
        )
        # 确保 call_bot 已经加载 (防止启动时循环导入)
        global call_bot
        if not call_bot:
             from .client import call_bot as cb_real
             call_bot = cb_real

        await call_bot(msg_send)

class Event:
    """模拟 gsuid_core.models.Event 类"""
    def __init__(self, msg_receive: MessageReceive, raw_command_text: str):
        self._msg = msg_receive

        # 暴露核心逻辑需要的属性
        self.user_id: Optional[str] = msg_receive.user_id
        self.bot_id: str = msg_receive.bot_id
        self.group_id: Optional[str] = msg_receive.group_id
        self.text: str = raw_command_text # 包含命令和参数的文本
        self.user_type: str = msg_receive.user_type

    @property
    def is_group(self) -> bool:
        return self.user_type == "group"

# 模拟 gsuid_core.logger.logger
logger = nb_logger

# 模拟 gsuid_core.web_app.app
app = get_app()


# 模拟 gsuid_core.segment.MessageSegment
class MessageSegment:
    @staticmethod
    def image(data: str) -> str:
        # 返回一个可被 Bot.send 解析的标记
        return f"[IMAGE:{data}]"

    @staticmethod
    def node(nodes: list) -> str:
        # 返回一个可被 Bot.send 解析的标记
        return f"[NODE:{nodes}]"



# 模拟 gsuid_core.utils.cookie_manager.qrlogin.get_qrcode_base64
async def get_qrcode_base64(url: str, path: Path, bot_id: str) -> str:
    """模拟 QR 码生成，返回 Base64 占位符"""
    nb_logger.info(f"[Shim] 正在生成模拟二维码: {url}")
    # 返回一个 base64 编码的占位符图片数据
    placeholder_svg = f'<svg xmlns="[http://www.w3.org/2000/svg](http://www.w3.org/2000/svg)" width="100" height="100" viewBox="0 0 100 100"><text x="10" y="50" font-size="10">{url.split("/")[-1]}</text></svg>'
    return "base64://" + base64.b64encode(placeholder_svg.encode()).decode()

# -------------------------------------------------------------------
# 6. 模拟 `..wutheringwaves` (插件内部)
# -------------------------------------------------------------------

# 模拟 ..utils.waves_api.waves_api
class WavesApi:
    async def login(self, phone: str, code: str, did: str) -> Any:
        class Result:
            def __init__(self, success, msg, data=None):
                self.success = success
                self.msg = msg
                self.data = data
            def throw_msg(self):
                return f"[API 模拟错误]: {self.msg}"

        nb_logger.info(f"[Shim] 模拟 waves_api.login (手机号: {phone})")
        if phone == "12345678901" and code == "666666":
            return Result(True, "登录成功", {"token": "success_token"})
        elif phone == "11111111111":
            return Result(True, "系统繁忙，请稍后再试")
        return Result(False, "验证码或手机号错误")


# TODO 模拟 ..wutheringwaves_config.PREFIX, WutheringWavesConfig
PREFIX = "/" # 您可以从 NoneBot config 中读取



# 模拟 httpx (因为它是 gsuid_core 的依赖, login.py 直接用了)
# 实际项目中，您应该 `pdm add httpx`
try:
    import httpx
except ImportError:
    nb_logger.error("[Shim] 缺少 `httpx` 依赖，请运行 `pdm add httpx`")
    httpx = None

# 模拟 async_timeout
try:
    from async_timeout import timeout
except ImportError:
    nb_logger.error("[Shim] 缺少 `async_timeout` 依赖，请检查 pyproject.toml")
    async def timeout(delay): # type: ignore
        return asyncio.sleep(0) # 返回一个无操作的 awaitable