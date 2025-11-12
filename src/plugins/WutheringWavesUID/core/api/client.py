import httpx
from typing import Dict, Any, Optional
from ...config import plugin_config

class APIClient:
    """HTTP客户端"""

    def __init__(self):
        self.proxy = plugin_config.WAVES_PROXY
        self.client = httpx.AsyncClient(
            proxies=self.proxy,
            timeout=30.0,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )

    async def request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """发送请求"""
        try:
            response = await self.client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"retcode": -1, "message": str(e)}

    async def close(self):
        await self.client.aclose()

api_client = APIClient()