import asyncio
import hashlib
import uuid
import re
from pathlib import Path
from typing import Tuple
from async_timeout import timeout

from nonebot.adapters import Bot, Event
from nonebot.adapters.onebot.v11 import MessageSegment

from ...config import plugin_config
from ...core.api.waves_api import waves_api
from ...services.user_service import UserService
from ...services.bind_service import BindService
from ...core.utils.qrcode import generate_qrcode
from ...cache import memory_cache

class LoginManager:
    """登录管理器"""

    def __init__(self, bot: Bot, event: Event):
        self.bot = bot
        self.event = event
        self.user_id = str(getattr(event, 'user_id', ''))
        self.bot_id = event.get_type()
        self.group_id = str(getattr(event, 'group_id', ''))

    def get_token(self) -> str:
        """生成用户token"""
        return hashlib.sha256(f"{self.user_id}_{self.bot_id}".encode()).hexdigest()[:8]

    async def start_login(self):
        """开始登录流程"""
        if not plugin_config.WAVES_ENABLE_LOGIN:
            await self.bot.send(self.event, "登录功能暂未开启")
            return

        url, is_local = await self.get_login_url()

        if is_local:
            await self.local_login(url)
        else:
            await self.remote_login(url)

    async def code_login(self, text: str):
        """验证码登录"""
        try:
            phone, code = text.split(",")
            phone = phone.strip()
            code = code.strip()

            if not self.is_valid_phone_number(phone):
                raise ValueError("手机号格式错误")

            if not self.is_validate_code(code):
                raise ValueError("验证码格式错误")

        except ValueError as e:
            await self.bot.send(
                self.event,
                f"格式错误！{str(e)}\n请使用：手机号,验证码\n示例：13812345678,123456"
            )
            return

        did = str(uuid.uuid4()).upper()
        result = await waves_api.login(phone, code, did)

        if not result.success:
            await self.bot.send(self.event, f"登录失败：{result.msg}")
            return

        token = result.token
        if not token:
            await self.bot.send(self.event, "登录失败：未获取到token")
            return

        # 获取用户UID（从user_info中）
        user_info = result.user_info or {}
        uid = user_info.get("uid", "")

        if not uid:
            # 如果没有UID，尝试通过其他API获取
            user_response = await waves_api.get_user_info(token, "")
            if user_response.success:
                uid = user_response.uid or ""

        if not uid:
            await self.bot.send(self.event, "登录失败：无法获取用户UID")
            return

        # 保存用户信息
        user_service = UserService()
        user = await user_service.create_or_update_user(
            user_id=self.user_id,
            bot_id=self.bot_id,
            uid=uid,
            cookie=token,
            did=did
        )

        if user:
            # 绑定UID
            bind_service = BindService()
            success = await bind_service.bind_user(
                user_id=self.user_id,
                bot_id=self.bot_id,
                uid=uid,
                group_id=self.group_id
            )

            if success:
                await self.send_success_message(uid)
            else:
                await self.bot.send(self.event, "登录失败：绑定UID失败")
        else:
            await self.bot.send(self.event, "登录失败：用户信息保存失败")

    async def local_login(self, base_url: str):
        """本地登录页面"""
        token = self.get_token()
        login_url = f"{base_url}/waves/i/{token}"

        # 保存登录状态到缓存
        memory_cache.set(token, {
            "user_id": self.user_id,
            "bot_id": self.bot_id,
            "group_id": self.group_id,
            "mobile": "",
            "code": ""
        })

        await self.send_login_message(login_url)
        await self.wait_login_result(token)

    async def remote_login(self, base_url: str):
        """远程登录页面"""
        # 实现远程登录逻辑
        await self.bot.send(self.event, "远程登录功能开发中...")

    async def wait_login_result(self, token: str):
        """等待登录结果"""
        try:
            async with timeout(600):  # 10分钟超时
                while True:
                    data = memory_cache.get(token)
                    if data is None:
                        await self.bot.send(self.event, "登录超时！")
                        return

                    if data.get("mobile") and data.get("code"):
                        # 执行验证码登录
                        await self.code_login(f"{data['mobile']},{data['code']}")
                        memory_cache.delete(token)
                        return

                    await asyncio.sleep(1)
        except asyncio.TimeoutError:
            await self.bot.send(self.event, "登录超时！")
            memory_cache.delete(token)

    async def send_login_message(self, login_url: str):
        """发送登录消息"""
        if plugin_config.WAVES_QR_LOGIN:
            # 二维码登录
            qr_path = Path(f"/tmp/{self.user_id}_login.png")
            success = await generate_qrcode(login_url, qr_path)

            if success and qr_path.exists():
                message = [
                    "【鸣潮登录】",
                    f"用户ID：{self.user_id}",
                    "请扫描二维码或在浏览器打开以下链接：",
                    MessageSegment.image(f"file:///{qr_path}"),
                    f"链接：{login_url}",
                    "有效期10分钟"
                ]

                # 清理临时文件
                try:
                    qr_path.unlink()
                except:
                    pass
            else:
                message = [
                    "【鸣潮登录】",
                    f"用户ID：{self.user_id}",
                    "请在浏览器打开以下链接：",
                    login_url,
                    "有效期10分钟"
                ]
        else:
            # 直接链接
            if plugin_config.WAVES_TENCENT_WORD:
                login_url = f"https://docs.qq.com/scenario/link.html?url={login_url}"

            message = [
                "【鸣潮登录】",
                f"用户ID：{self.user_id}",
                "请在浏览器打开以下链接：",
                login_url,
                "有效期10分钟"
            ]

        if plugin_config.WAVES_LOGIN_FORWARD and hasattr(MessageSegment, 'node'):
            await self.bot.send(self.event, MessageSegment.node(message))
        else:
            await self.bot.send(self.event, "\n".join([str(m) for m in message]))

    async def send_success_message(self, uid: str):
        """发送登录成功消息"""
        message = [
            "【登录成功】",
            f"用户ID：{self.user_id}",
            f"游戏UID：{uid}",
            "现在可以使用以下命令：",
            "- 【鸣潮信息】查看角色数据",
            "- 【鸣潮战绩】查看游戏统计",
            "- 【鸣潮绑定】切换绑定账号"
        ]
        await self.bot.send(self.event, "\n".join(message))

    async def get_login_url(self) -> Tuple[str, bool]:
        """获取登录URL"""
        if plugin_config.WAVES_LOGIN_URL:
            url = plugin_config.WAVES_LOGIN_URL
            if not url.startswith("http"):
                url = f"https://{url}"
            return url, plugin_config.WAVES_LOGIN_URL_SELF
        else:
            host = plugin_config.HOST
            port = plugin_config.PORT
            return f"http://{host}:{port}", True

    def is_valid_phone_number(self, phone: str) -> bool:
        """验证手机号格式"""
        pattern = re.compile(r"^1[3-9]\d{9}$")
        return pattern.match(phone) is not None

    def is_validate_code(self, code: str) -> bool:
        """验证验证码格式"""
        pattern = re.compile(r"^\d{6}$")
        return pattern.match(code) is not None