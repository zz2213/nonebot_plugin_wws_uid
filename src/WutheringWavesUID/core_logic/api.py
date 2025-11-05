# wws_native/core_logic/api.py
from typing import Any
import httpx
from nonebot import get_driver
from ..config import Config

# 加载配置
plugin_config = Config.parse_obj(get_driver().config)
base_url = plugin_config.WWS_API_URL

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Content-Type": "application/json", "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.kurobbs.com/", "Origin": "https://www.kurobbs.com",
}

async def _post(endpoint: str, payload: dict) -> dict[str, Any]:
    """通用的POST请求方法"""
    url = base_url + endpoint
    try:
        async with httpx.AsyncClient(proxies=plugin_config.WWS_PROXY) as client:
            resp = await client.post(url, json=payload, headers=HEADERS, timeout=15.0)
            resp.raise_for_status()
            data = resp.json()

        if data.get("code") != 200:
            raise ValueError(f"API返回错误: {data.get('msg', '未知')}")
        if not data.get("data"):
            raise ValueError("API未返回任何数据")
        return data["data"]
    except Exception as e:
        raise ConnectionError(f"网络请求失败: {e}")

async def login(user_id: int, phone: str, code: str = ""):
    """[重构] 登录API"""
    endpoint = "wutheringWaves/login"
    payload = {"user_id": user_id, "phone": phone, "code": code}
    return await _post(endpoint, payload)

# --- 未来迁移其他功能时，从原项目 `wwapi.py` 移植其他函数到这里 ---
async def get_player_info(uid: int):
    return await _post("wutheringWaves/getInfo", {"uid": str(uid)})

async def get_roles_list(uid: int):
     return await _post("wutheringWaves/getRoleList", {"uid": str(uid)})