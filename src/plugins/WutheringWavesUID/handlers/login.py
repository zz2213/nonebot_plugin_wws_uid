# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/handlers/login.py

import httpx
from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, MessageEvent, Bot
from nonebot.typing import T_State
from nonebot.log import logger
import re

from ..config import plugin_config
from ..services.user_service import user_service
from ..core.utils.qrcode import generate_qrcode_image
from ..core.utils.image import pil_to_img_msg

# --- 新增导入 (用于指令式登录) ---
from ..services.user_service import UserService

# --- 导入结束 ---

PHONE_REGEX = re.compile(r"1[3-9]\d{9}")

# --- 现有命令 (Web 登录) ---

wws_login = on_command("鸣潮登录", aliases={"wwslogin", "mc login"}, priority=10, block=True)
wws_login_token = on_command("鸣潮token登录", aliases={"wwstoken"}, priority=10, block=True)


@wws_login.handle()
async def _(bot: Bot, event: MessageEvent, matcher: Matcher):
  user_id = event.get_user_id()

  # 1. 生成登录 URL
  login_url = f"http://127.0.0.1:{bot.config.port}/wws/login?user_id={user_id}"

  # 2. 生成二维码
  try:
    qr_image = generate_qrcode_image(login_url)
    qr_msg = pil_to_img_msg(qr_image)
    await matcher.send(
        "请扫描下方二维码或点击链接进行登录：\n" +
        login_url + "\n" +
        qr_msg
    )
  except Exception as e:
    logger.error(f"生成二维码失败: {e}")
    await matcher.send(
        "生成二维码失败，请点击链接进行登录：\n" +
        login_url
    )


@wws_login_token.handle()
async def _(bot: Bot, event: MessageEvent, matcher: Matcher, args: Message = CommandArg()):
  """
  使用 Token/Cookie 登录
  """
  token = args.extract_plain_text().strip()
  if not token:
    await matcher.finish("请输入你的 Token（Cookie 中的 token 字段值）。")
    return

  user_id = event.get_user_id()
  cookie = f"token={token}"

  # 验证 Token 有效性
  await matcher.send("正在验证 Token...")
  try:
    # 尝试调用 get_user_info 验证
    # TODO: 缺少 UID，无法验证
    # 暂时跳过验证，直接绑定
    # (
    #     我们应该先要求用户提供 UID，
    #     然后再调用 get_user_info(cookie, uid) 验证
    # )

    # 临时方案：先绑定，让用户自己查询
    # TODO: 改进登录逻辑，需要 UID
    await matcher.finish("Token 已设置，但无法验证。\n"
                         "请使用【绑定】命令将此 Token 关联到一个 UID。\n"
                         "例如：绑定 12345678")

  except Exception as e:
    logger.error(f"Token 验证失败: {e}")
    await matcher.finish(f"Token 验证失败: {e}")


# --- 新增命令 (指令式登录) ---

get_captcha_cmd = on_command("获取验证码", priority=10, block=True)
phone_login_cmd = on_command("手机号登录", priority=10, block=True)


@get_captcha_cmd.handle()
async def _(matcher: Matcher, args: Message = CommandArg()):
  phone = args.extract_plain_text().strip()
  if not PHONE_REGEX.match(phone):
    await matcher.finish("请输入正确的手机号。")
    return

  await matcher.send("正在发送验证码，请稍候...")

  try:
    resp = await user_service.get_captcha(phone)
    await matcher.finish(resp.msg)
  except Exception as e:
    logger.error(f"get_captcha failed: {e}")
    await matcher.finish(f"发送验证码时发生内部错误：{e}")


@phone_login_cmd.handle()
async def handle_first_receive(matcher: Matcher, state: T_State, args: Message = CommandArg()):
  """
  “手机号登录”命令的第一步：获取手机号
  """
  phone = args.extract_plain_text().strip()
  if phone and PHONE_REGEX.match(phone):
    state["phone"] = phone
  else:
    await matcher.send("请输入您的手机号：")
    return  # 等待下一次输入


@phone_login_cmd.receive()
async def handle_phone_receive(matcher: Matcher, state: T_State, event: MessageEvent):
  """
  第二步：已获取手机号，发送验证码，并要求输入验证码
  """
  if "phone" not in state:
    phone = event.get_plaintext().strip()
    if not PHONE_REGEX.match(phone):
      await matcher.reject("手机号格式不正确，请重新输入：")
      return
    state["phone"] = phone

  phone = state["phone"]

  # 发送验证码
  await matcher.send(f"正在为 {phone} 发送验证码...")
  try:
    resp = await user_service.get_captcha(phone)
    if not resp.success:
      await matcher.finish(f"验证码发送失败：{resp.msg}")
      return
    await matcher.send(f"验证码发送成功！请输入您收到的6位验证码：")

  except Exception as e:
    logger.error(f"get_captcha (in login) failed: {e}")
    await matcher.finish(f"发送验证码时发生内部错误：{e}")
    return

  # 进入下一步，等待验证码
  state["next_step"] = "wait_code"


@phone_login_cmd.receive()
async def handle_code_receive(matcher: Matcher, state: T_State, event: MessageEvent):
  """
  第三步：已获取验证码，执行登录
  """
  if state.get("next_step") != "wait_code":
    # 异常流程，不应该到这里
    await matcher.finish("流程错误，请重新开始。")
    return

  code = event.get_plaintext().strip()
  if not (code.isdigit() and len(code) == 6):
    await matcher.reject("验证码格式不正确（应为6位数字），请重新输入：")
    return

  phone = state["phone"]
  user_id = str(event.user_id)

  await matcher.send(f"正在使用手机号 {phone} 和验证码 {code} 登录...")

  try:
    login_resp = await user_service.login_by_phone(user_id, phone, code)

    if login_resp.success:
      await matcher.finish(f"🎉 {login_resp.msg}")
    else:
      await matcher.finish(f"登录失败：{login_resp.msg}")

  except Exception as e:
    logger.error(f"login_by_phone failed: {e}")
    await matcher.finish(f"登录时发生内部错误：{e}")