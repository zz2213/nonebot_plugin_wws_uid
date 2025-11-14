# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/web_routes.py

from nonebot import get_app
from fastapi import Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from .cache import memory_cache
from .core.resource.manager import resource_manager

app = get_app()


class LoginRequest(BaseModel):
    auth: str
    mobile: str
    code: str


@app.get("/waves/i/{auth}")
async def waves_login_page(request: Request, auth: str):
    """登录页面"""
    data = memory_cache.get(auth)
    if data is None:
        return HTMLResponse(resource_manager.render_template("404.html"))

    # --- 修复导入 ---
    from . import plugin_config  # 从 __init__.py 导入实例
    # from .config import plugin_config # 错误
    # --- 修复结束 ---

    host = plugin_config.WAVES_HOST
    port = plugin_config.WAVES_PORT
    server_url = f"http://{host}:{port}"

    return HTMLResponse(resource_manager.render_template(
        "login.html",
        server_url=server_url,
        auth=auth,
        user_id=data.get("user_id", "")
    ))


@app.post("/waves/login")
async def waves_login_submit(request: LoginRequest):
    """处理登录提交"""
    data = memory_cache.get(request.auth)
    if data is None:
        return JSONResponse({"success": False, "msg": "登录超时"})

    # 更新登录数据
    data.update({
        "mobile": request.mobile,
        "code": request.code,
        "status": "pending"
    })
    memory_cache.set(request.auth, data)

    return JSONResponse({"success": True, "msg": "登录信息已提交，请返回 Bot 查看结果"})