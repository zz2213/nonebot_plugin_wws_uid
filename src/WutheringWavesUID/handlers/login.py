# WutheringWavesUID/handlers/login.py
from nonebot import on_command, on_regex
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.adapters import Bot, Event, Message
from . import create_adapter

# 导入重构后的核心逻辑
from ..core_logic import api as wwapi
from ..core_logic.models import UserData, LoginResult  # 导入 Pydantic 模型
from ..adapters import MessageAdapter
from .user import bind_user  # 导入重构后的绑定函数


# --- 鸣潮登录 (二维码) ---
# [修正]：将 .handle() 正确地作为装饰器应用
@on_command(
    "鸣潮登录", aliases={"wws登录", "ww登录"}, priority=10, block=True
).handle()
async def _login(matcher: Matcher, bot: Bot, event: Event):
  adapter = create_adapter(bot, event, matcher)
  if not adapter: return

  user_id = int(adapter.get_user_id())

  try:
    await adapter.reply("正在获取登录二维码...")
    # 调用重构后的 API
    resp_data = await wwapi.login(user_id, "")
    resp = LoginResult.model_validate(resp_data)  # 转换为 Pydantic 模型

    if not resp.url:
      await adapter.reply("获取二维码失败，请稍后再试。")
      return

    # 这就是您记忆中的“链接”
    await adapter.reply(f"请扫描二维码登录: {resp.url}")

  except Exception as e:
    await adapter.reply(f"登录失败: {e}")


# --- 手机号登录 ---
# [修正]：将 .handle() 正确地作为装饰器应用
@on_command("手机号登录", priority=10, block=True).handle()
async def _phone_login(matcher: Matcher, bot: Bot, event: Event, args: Message = CommandArg()):
  adapter = create_adapter(bot, event, matcher)
  if not adapter: return

  user_id = int(adapter.get_user_id())
  phone = args.extract_plain_text().strip()

  if not phone.isdigit() or len(phone) != 11:
    await adapter.reply("手机号格式不正确，请输入11位手机号。")
    return

  try:
    await adapter.reply(f"正在获取{phone}的验证码,请等待...")
    resp_data = await wwapi.login(user_id, phone)
    resp = LoginResult.model_validate(resp_data)

    if not resp.code:
      await adapter.reply(f"获取验证码失败: {resp.msg or '未知错误'}")
      return

    await adapter.reply(f"{phone}的验证码为 {resp.code}, 请在120s内输入:")

    # --- [原生实现] sv.wait_for ---
    code_input = await adapter.wait_for_message(timeout=120, regex=r"^\d{6}$")
    if not code_input:
      return  # 超时或格式错误，adapter.wait_for_message 已回复
    # --- 替换结束 ---

    await adapter.reply("验证码已收到，正在登录...")
    resp_data = await wwapi.login(user_id, phone, code_input)
    resp = LoginResult.model_validate(resp_data)

    if not resp.uid:
      await adapter.reply(f"登录失败: {resp.msg or '未获取到UID'}")
      return

    await adapter.reply(f"登录成功！UID: {resp.uid}，正在为您自动绑定...")
    # 调用重构后的 bind_user
    result = await bind_user(adapter, resp.uid)
    await adapter.reply(result)

  except Exception as e:
    await adapter.reply(f"登录时发生错误: {e}")


# --- 验证码接收器 ---
# [修正]：将 .handle() 正确地作为装饰器应用
@on_regex(r"^\d{6}$", priority=6, block=True).handle()
async def _handle_code(matcher: Matcher, bot: Bot, event: Event):
  # 这是一个““哑””处理器
  # 它的作用是捕获 6 位数字，但什么也不做
  # 真正的逻辑在 _phone_login 函数的 adapter.wait_for_message() 中处理
  # 它的存在是为了确保 wait_for_message 能正确接收到事件
  pass