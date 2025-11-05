from nonebot import get_app
from fastapi import Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from .utils.cache import cache

app = get_app()

class LoginModel(BaseModel):
    auth: str
    mobile: str
    code: str

@app.get("/waves/i/{auth}")
async def waves_login_index(request: Request, auth: str):
    """登录页面"""
    temp = cache.get(auth)
    if temp is None:
        template = get_template("404.html")
        return HTMLResponse(template.render())
    else:
        from .utils.login_helpers import get_url
        url, _ = await get_url()
        template = get_template("index.html")
        return HTMLResponse(
            template.render(
                server_url=url,
                auth=auth,
                userId=temp.get("user_id", ""),
                kuro_url="https://api.kurobbs.com"
            )
        )

@app.post("/waves/login")
async def waves_login(data: LoginModel):
    """处理登录请求"""
    temp = cache.get(data.auth)
    if temp is None:
        return JSONResponse({"success": False, "msg": "登录超时"})

    temp.update(data.dict())
    cache.set(data.auth, temp)
    return JSONResponse({"success": True})

def get_template(template_name: str):
    """获取模板（简化实现）"""
    from jinja2 import Template
    if template_name == "index.html":
        return Template("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>鸣潮登录</title>
        </head>
        <body>
            <h1>鸣潮登录页面</h1>
            <p>用户ID: {{ userId }}</p>
        </body>
        </html>
        """)
    else:
        return Template("<h1>页面不存在</h1>")