# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/core/api/client.py

import httpx
import json  # <-- 新增修复：导入 json 模块
from ... import plugin_config  # 正确: 从插件根目录的 __init__.py 导入
from nonebot.log import logger


class ApiClient:
    def __init__(self):
        # 这里的 plugin_config 现在可以被正确导入
        self.base_url = plugin_config.WAVES_API_URL
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=10.0, follow_redirects=True)
        logger.info(f"ApiClient initialized with base_url: {self.base_url}")

    async def request(self, method: str, url: str, **kwargs) -> dict:
        """
        发起异步HTTP请求
        :param method: 请求方法 (GET, POST, etc.)
        :param url: 请求URL (可以是相对路径)
        :param kwargs: 传递给 httpx.request 的其他参数 (json, data, params, headers)
        :return: JSON响应 (dict)
        """
        try:
            # 如果 url 是绝对路径，则 base_url 不会生效
            if not url.startswith("http"):
                full_url = f"{self.base_url.rstrip('/')}/{url.lstrip('/')}"
            else:
                full_url = url
                # 如果是绝对路径, 我们需要一个临时的 client
                async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as temp_client:
                    response = await temp_client.request(method, full_url, **kwargs)
                    response.raise_for_status()
                    # 适配：如果返回空，则给一个 {}
                    if not response.text:
                        return {"retcode": 0, "message": "Success (empty response)"}
                    return response.json()

            # logger.debug(f"Request: {method} {url} with kwargs: {kwargs}")
            response = await self._client.request(method, url, **kwargs)
            response.raise_for_status()  # 抛出 HTTP 错误

            # 适配：如果返回空，则给一个 {}
            if not response.text:
                return {"retcode": 0, "message": "Success (empty response)"}

            return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code} while requesting {e.request.url}: {e.response.text}")
            try:
                return e.response.json()  # 尝试返回错误JSON
            except Exception:
                return {"retcode": e.response.status_code, "message": f"HTTP error: {e.response.status_code}"}
        except httpx.RequestError as e:
            logger.error(f"An error occurred while requesting {e.request.url}: {e}")
            return {"retcode": -1, "message": f"Request failed: {e}"}
        except json.JSONDecodeError as e:  # <-- 这里的 'json' 现在是有效的
            logger.error(f"Failed to decode JSON response: {e}")
            # 适配：返回包含原始文本的错误信息
            return {"retcode": -2, "message": f"JSON decode error: {e.doc}"}
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            logger.exception(e)
            return {"retcode": -500, "message": f"Unexpected error: {e}"}


# 创建一个全局唯一的客户端实例
api_client = ApiClient()