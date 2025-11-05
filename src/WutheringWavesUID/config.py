from pydantic import BaseModel, Extra
class Config(BaseModel, extra=Extra.ignore):
    """鸣潮原生插件配置项"""
    WWS_API_URL: str = "https://api.kurobbs.com/gamer/api/"
    WWS_PROXY: str | None = None