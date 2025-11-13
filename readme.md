# NoneBot2 鸣潮插件

基于 NoneBot2 框架的鸣潮游戏数据查询插件，完整迁移自 WutheringWavesUID 项目，支持用户登录、角色信息查询、游戏数据统计等功能。

## 功能特性

- 🔐 **安全登录** - 支持手机号+验证码登录库街区账号
- 📱 **多方式登录** - 支持二维码登录和直接链接登录
- 👤 **用户管理** - 自动绑定用户与游戏UID
- 📊 **数据查询** - 查询角色信息、游戏统计数据
- 🌐 **Web界面** - 提供友好的Web登录页面
- 🔄 **缓存优化** - 智能缓存机制提升查询速度

## 安装方式

### 方式一：使用 pip 安装（推荐）
```bash
pip install nonebot-plugin-wutheringwaves
```

### 方式二：从源码安装
```bash
git clone https://github.com/your-repo/nonebot-plugin-wutheringwaves.git
cd nonebot-plugin-wutheringwaves
pip install -e .
```

## 配置说明

### 基础配置
在 NoneBot2 的 `.env` 文件中添加以下配置：

```ini
# 必填配置
WAVES_API_URL="https://api.kurobbs.com/gamer/api/"

# 登录相关配置
WAVES_LOGIN_URL=""  # 自定义登录页面URL，留空使用内置服务
WAVES_LOGIN_URL_SELF=false  # 是否使用自建登录页面
WAVES_QR_LOGIN=true  # 是否启用二维码登录
WAVES_LOGIN_FORWARD=false  # 是否使用转发消息
WAVES_TENCENT_WORD=false  # 是否使用腾讯文档链接

# 网络代理（可选）
WAVES_PROXY="http://127.0.0.1:7890"  # 代理服务器地址
```

### 机器人配置
在 `pyproject.toml` 或 `bot.py` 中加载插件：

```python
# 加载插件
nonebot.load_plugin("nonebot_plugin_wutheringwaves")
```

## 使用指南

### 登录账号
```
鸣潮登录
```
- 发送登录命令后，机器人会提供登录链接或二维码
- 在浏览器中打开链接，输入手机号和验证码完成登录
- 登录成功后自动绑定游戏UID

### 验证码登录
```
鸣潮验证码登录 13812345678,123456
```
- 直接使用手机号和验证码登录
- 格式：手机号,验证码

### 查询信息
```
鸣潮信息
```
- 查看已绑定账号的角色信息
- 包括UID、昵称、等级等基础信息

### 账号绑定
```
鸣潮绑定 123456789
```
- 绑定指定的游戏UID
- 不填参数时显示当前绑定状态

## 命令列表

| 命令 | 功能 | 示例 |
|------|------|------|
| `鸣潮登录` | 开始登录流程 | `鸣潮登录` |
| `鸣潮验证码登录` | 直接验证码登录 | `鸣潮验证码登录 13812345678,123456` |
| `鸣潮信息` | 查询角色信息 | `鸣潮信息` |
| `鸣潮绑定` | 绑定/查看UID | `鸣潮绑定 123456789` |
| `鸣潮帮助` | 显示帮助信息 | `鸣潮帮助` |

## 数据库说明

插件使用 SQLite 数据库存储以下信息：

- **用户表** (`waves_users`)
  - 用户ID、机器人ID、游戏UID
  - 登录Cookie、设备ID
  - 创建和更新时间

- **绑定表** (`waves_binds`)
  - 用户与游戏UID的绑定关系
  - 群组信息、主绑定标识

- **缓存表** (`waves_cache`)
  - API响应缓存
  - 缓存过期时间管理

## 部署说明

### 环境要求
- Python 3.8+
- NoneBot2 2.0.0+
- 支持的适配器：OneBot V11/V12

### 文件结构
```
nonebot_plugin_wutheringwaves/
├── __init__.py              # 插件入口
├── config.py                # 配置管理
├── models.py                # 数据库模型
├── database.py              # 数据库操作
├── cache.py                 # 缓存系统
├── web_routes.py            # Web路由
├── core/                    # 核心逻辑
│   ├── api/                 # API接口
│   ├── resource/            # 资源管理
│   └── utils/               # 工具函数
├── handlers/                # 命令处理器
└── services/                # 业务服务层
```

### Web服务
插件内置Web服务，默认提供以下路由：

- `GET /waves/i/{token}` - 登录页面
- `POST /waves/login` - 登录提交接口
- `GET /waves/health` - 健康检查

## 常见问题

### Q: 登录失败怎么办？
A: 请检查：
1. 是否已注册库街区账号
2. 手机号和验证码是否正确
3. 网络连接是否正常
4. 代理配置是否正确（如使用代理）

### Q: 查询信息显示"未绑定"？
A: 请先使用 `鸣潮登录` 命令完成账号绑定。

### Q: 如何切换绑定账号？
A: 使用 `鸣潮绑定 新UID` 命令重新绑定，或重新登录。

### Q: 插件无法正常加载？
A: 请检查：
1. NoneBot2 版本是否符合要求
2. 配置文件是否正确
3. 依赖包是否完整安装

## 开发指南

### 自定义扩展
如需扩展功能，可参考以下示例：

```python
from nonebot_plugin_wutheringwaves import waves_api, UserService

# 调用API接口
result = await waves_api.get_user_info(cookie, uid)

# 使用服务层
user_service = UserService()
user = await user_service.get_user(user_id, bot_id)
```

### API文档
插件提供的核心API：

- `WavesAPI.login(phone, code, did)` - 用户登录
- `WavesAPI.get_user_info(cookie, uid)` - 获取用户信息
- `WavesAPI.get_role_info(cookie, uid)` - 获取角色信息
- `WavesAPI.get_stats(cookie, uid)` - 获取统计数据

## 更新日志

### v1.0.0 (2024-01-01)
- ✅ 完整迁移原 WutheringWavesUID 功能
- ✅ 支持手机号+验证码登录
- ✅ 支持二维码登录
- ✅ 用户信息查询
- ✅ 游戏数据统计

## 技术支持

- 项目主页: [GitHub Repository](https://github.com/your-repo/nonebot-plugin-wutheringwaves)
- 问题反馈: [Issues](https://github.com/your-repo/nonebot-plugin-wutheringwaves/issues)
- 交流群组: [QQ群: 123456789]

## 免责声明

本插件仅供学习交流使用，不得用于商业用途。使用本插件即表示您同意：

1. 遵守库街区用户协议
2. 不进行任何形式的账号交易
3. 不利用插件进行恶意行为
4. 自行承担使用风险

## 开源协议

本项目采用 MIT 开源协议，详见 [LICENSE](LICENSE) 文件。

---

**注意**: 使用前请确保已阅读并同意相关服务条款，合理使用插件功能。



这是一个非常棒的迁移项目！从你现有的 `nonebot_plugin_wws_uid` 结构来看，你已经有了一个很好的开端，特别是将 API 和服务 (Service) 进行了分离。

原项目 (`WutheringWavesUID1`, `WutheringWavesUID2`) 功能非常强大，但它的核心都集中在 `utils` 目录和各个模块的 `draw_*.py` 文件中。

迁移的**核心思想**是：

1.  **复用你的 `services` 层**：作为获取所有数据的统一入口（无论是来自游戏 API 还是排行 API）。
2.  **迁移 `utils`**：将原项目的 `utils` 目录下的核心工具（绘图、数据、计算）平移到你新项目的 `core` 目录下。
3.  **迁移 `draw_*.py`**：将所有绘图逻辑（视图 View）迁移过来，并改造它们，让它们的数据源从原来的直接调用 API 改为调用你的 `services` 层。
4.  **迁移 `__init__.py`**：将原项目各个模块 `__init__.py` 中的命令注册（控制器 Controller）迁移到你的 `handlers` 目录中。

🌟 迁移计划
🏛️ 阶段 0：基础建设 (资源与数据) (✅)
[✅] 迁移所有 Assets (texture2d) (按模块分离到 assets/images/ 下)

[✅] 迁移字体 (到 assets/fonts/)

[✅] 迁移核心游戏数据 (map) (到 core/data/)

[✅] 迁移别名数据 (alias) (到 core/data/alias/)

🛠️ 阶段 1：核心工具迁移 (Utilities) (✅)
[✅] 迁移字体工具 (core/utils/fonts.py)

[✅] 迁移绘图工具 (重构 imagetool.py 和 image.py，移除 gsuid_core 依赖，合并为 core/utils/image_helpers.py 和 drawing_helpers.py)

[✅] 迁移伤害计算 (迁移 utils/damage 和 utils/ascension 到 core/damage 和 core/ascension，并适配路径)

[✅] 迁移别名服务 (创建 services/alias_service.py 和 handlers/alias.py)

🖼️ 阶段 2：核心功能迁移 (1) - 角色面板 (✅)
[✅] 迁移数据处理逻辑 (创建 services/character_service.py 和 core/utils/scoring.py)

[✅] 迁移绘图逻辑 (创建 core/drawing/character_card.py 并重构)

[✅] 创建 Handler (创建 handlers/character.py)

🏆 阶段 3：核心功能迁移 (2) - 排行榜 (✅)
[✅] 迁移 API 封装 (创建 core/api/ranking_api.py)

[✅] 迁移数据处理逻辑 (更新 services/game_service.py 以集成 ranking_api)

[✅] 迁移绘图逻辑 (创建 core/drawing/ranking_card.py 并重构)

[✅] 创建 Handler (创建 handlers/ranking.py)

🧩 阶段 4：模块化迁移其他功能 (🏃‍♂️ 进行中...)
[🏃‍♂️] 迁移角色列表 (wutheringwaves_charlist)

[✅] 1. 迁移数据处理逻辑 (我上一条回复中，已更新 services/character_service.py，添加了 get_character_list_data 方法)

[✅] 2. 迁移绘图逻辑 

[✅]3. 创建 Handler

[✅] 迁移体力查询 (wutheringwaves_stamina)(← 我们现在在这里 📍)

[✅] 迁移声骸列表 (wutheringwaves_echo)

[✅]迁移探索度 (wutheringwaves_explore)

[ ] 迁移深渊 (wutheringwaves_abyss)

[ ] 迁移抽卡记录 (wutheringwaves_gachalog)

[ ] 迁移数据统计 (wutheringwaves_query) (持有率、出场率)

[ ] 迁移 Wiki (wutheringwaves_wiki)

[ ] 迁移日历/材料 (wutheringwaves_calendar, wutheringwaves_develop)

⚙️ 阶段 5：完善与收尾 (⏳ 未开始)
[ ] 数据库模型 (models.py)

[ ] 帮助菜单 (wutheringwaves_help)

[ ] 配置 (wutheringwaves_config)

[ ] 登录逻辑 (功能增强)