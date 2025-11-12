import json
from typing import Dict, Any
from .client import api_client
from .models import APIResponse, LoginResponse, UserInfoResponse
from ...config import plugin_config

class WavesAPI:
    """鸣潮API封装"""

    def __init__(self):
        self.base_url = plugin_config.WAVES_API_URL

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
        """获取统计数据"""
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

waves_api = WavesAPI()