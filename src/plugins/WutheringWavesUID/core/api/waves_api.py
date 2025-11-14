# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/core/api/waves_api.py

import json
from typing import Dict, Any
from .client import api_client
from .models import APIResponse, LoginResponse, UserInfoResponse
# --- 修复导入 ---
from ... import plugin_config  # 正确: 从 __init__.py 导入实例


# from ...config import plugin_config # 错误
# --- 修复结束 ---

class WavesAPI:
    """鸣潮API封装"""

    def __init__(self):
        self.base_url = plugin_config.WAVES_API_URL

    # --- 新增方法 (来自 wutheringwaves_login/login.py) ---
    async def get_captcha_code(self, phone: str) -> APIResponse:
        """获取手机验证码"""
        url = f"{self.base_url}get_captcha"
        data = {"phone": phone, "source": 2}

        result = await api_client.request("POST", url, json=data)

        # 验证码 API 的 retcode 是 1
        if result.get("retcode") == 1:
            return APIResponse(
                success=True,
                data=result.get("data", {}),
                msg=result.get("message", "验证码发送成功")
            )
        else:
            return APIResponse(
                success=False,
                msg=result.get("message", "验证码发送失败")
            )

    # --- 新增方法结束 ---

    async def login(self, phone: str, code: str, did: str) -> LoginResponse:
        """手机号登录"""
        url = f"{self.base_url}login"
        data = {
            "phone": phone,
            "captcha": code,
            "deviceId": did,
            "source": 2
        }

        result = await api_client.request("POST", url, json=data)

        if result.get("retcode") == 0:
            data = result.get("data", {})
            return LoginResponse(
                success=True,
                data=data,
                token=data.get("token", ""),
                user_info=data.get("user_info", {}),
                msg=result.get("message", "登录成功")
            )
        else:
            return LoginResponse(
                success=False,
                msg=result.get("message", "登录失败")
            )

    async def get_user_info(self, cookie: str, uid: str) -> UserInfoResponse:
        """获取用户信息"""
        url = f"{self.base_url}user/info"
        headers = {"Cookie": cookie}
        params = {"uid": uid}

        result = await api_client.request("GET", url, headers=headers, params=params)

        if result.get("retcode") == 0:
            data = result.get("data", {})
            return UserInfoResponse(
                success=True,
                data=data,
                uid=data.get("uid", ""),
                nickname=data.get("nickname", ""),
                level=data.get("level", 0),
                msg="获取成功"
            )
        else:
            return UserInfoResponse(
                success=False,
                msg=result.get("message", "获取失败")
            )

    async def get_role_info(self, cookie: str, uid: str) -> APIResponse:
        """获取角色信息"""
        url = f"{self.base_url}role/info"
        headers = {"Cookie": cookie}
        params = {"uid": uid}

        result = await api_client.request("GET", url, headers=headers, params=params)

        if result.get("retcode") == 0:
            return APIResponse(
                success=True,
                data=result.get("data", {}),
                msg="获取成功"
            )
        else:
            return APIResponse(
                success=False,
                msg=result.get("message", "获取失败")
            )

    async def get_stats(self, cookie: str, uid: str) -> APIResponse:
        """获取统计数据 (包含体力)"""
        url = f"{self.base_url}game/stats"
        headers = {"Cookie": cookie}
        params = {"uid": uid}

        result = await api_client.request("GET", url, headers=headers, params=params)

        if result.get("retcode") == 0:
            return APIResponse(
                success=True,
                data=result.get("data", {}),
                msg="获取成功"
            )
        else:
            return APIResponse(
                success=False,
                msg=result.get("message", "获取失败")
            )

    async def get_explore_info(self, cookie: str, uid: str) -> APIResponse:
        """获取探索度信息"""
        url = f"{self.base_url}explore/info"
        headers = {"Cookie": cookie}
        params = {"uid": uid}

        result = await api_client.request("GET", url, headers=headers, params=params)

        if result.get("retcode") == 0:
            return APIResponse(
                success=True,
                data=result.get("data", {}),
                msg="获取成功"
            )
        else:
            return APIResponse(
                success=False,
                msg=result.get("message", "获取失败")
            )

    async def get_tower_info(self, cookie: str, uid: str) -> APIResponse:
        """获取深境之塔信息"""
        url = f"{self.base_url}tower/info"
        headers = {"Cookie": cookie}
        params = {"uid": uid}
        result = await api_client.request("GET", url, headers=headers, params=params)
        return APIResponse(
            success=result.get("retcode") == 0,
            data=result.get("data", {}),
            msg=result.get("message", "获取失败")
        )

    async def get_challenge_info(self, cookie: str, uid: str) -> APIResponse:
        """获取全息战略信息"""
        url = f"{self.base_url}challenge/info"
        headers = {"Cookie": cookie}
        params = {"uid": uid}
        result = await api_client.request("GET", url, headers=headers, params=params)
        return APIResponse(
            success=result.get("retcode") == 0,
            data=result.get("data", {}),
            msg=result.get("message", "获取失败")
        )

    async def get_slash_info(self, cookie: str, uid: str) -> APIResponse:
        """获取冥歌海墟信息"""
        url = f"{self.base_url}slash/info"
        headers = {"Cookie": cookie}
        params = {"uid": uid}
        result = await api_client.request("GET", url, headers=headers, params=params)
        return APIResponse(
            success=True,
            data=result.get("data", {}),
            msg=result.get("message", "获取失败")
        )

    async def get_gacha_logs(
            self, base_url: str, params: Dict[str, Any]
    ) -> APIResponse:
        """
        获取抽卡记录
        """
        url = f"{base_url}/api/gachaInfo/list"
        result = await api_client.request("GET", url, params=params)

        if result.get("code") == 0 or result.get("code") == "0":
            return APIResponse(
                success=True,
                data=result.get("data", []),
                msg=result.get("message", "获取成功")
            )
        else:
            return APIResponse(
                success=False,
                msg=result.get("message", "获取失败")
            )

    async def get_period_info(self, cookie: str, uid: str) -> APIResponse:
        """获取资源统计 (月卡、星声、活跃度)"""
        url = f"{self.base_url}game/period"
        headers = {"Cookie": cookie}
        params = {"uid": uid}
        result = await api_client.request("GET", url, headers=headers, params=params)
        return APIResponse(
            success=result.get("retcode") == 0,
            data=result.get("data", {}),
            msg=result.get("message", "获取失败")
        )


waves_api = WavesAPI()