# NodePay CLI Bot

## 简介
这是一个用于 **NodePay** 平台的自动化工具，支持以下功能：
- 自动注册账户。
- 自动登录账户。
- 使用代理执行挖矿任务。

此工具通过命令行界面 (CLI) 运行，并支持多线程、CAPTCHA 验证和代理轮换。

---

## 安装与运行

### 1. 克隆仓库
首先，从 Git 仓库克隆项目代码：
```bash
git clone http://github.com/ziqing888/Nodepay-py.git

cd Nodepay-py
```
### 2. 安装依赖
在项目目录下，运行以下命令安装依赖：
```
pip install -r requirements.txt
```
### 3. 配置文件
在运行程序之前，请根据需要修改 data/settings.ini 文件，配置所需参数：
```
[DEFAULT]
AccountsFile = data/accounts.txt      # 账户文件路径
ProxiesFile = data/proxies.txt        # 代理文件路径
ReferralCodes = REF1,REF2,REF3        # 推荐码（逗号分隔）
Threads = 5                           # 并发线程数
CaptchaService = capmonster           # CAPTCHA 服务提供商
CaptchaAPIKey = your-captcha-api-key  # CAPTCHA API Key
DelayMin = 1                          # 最小延迟（秒）
DelayMax = 2                          # 最大延迟（秒）
```
### 文件说明
data/accounts.txt：

存储注册或登录账户信息，每行一个账户，格式为：
```
user1@example.com:password1
user2@example.com:password2
```
data/proxies.txt：

存储代理 IP，每行一个，支持 http 和 socks5 格式：
```
http://proxy1.example.com:8080
socks5://127.0.0.1:1080
```
CaptchaAPIKey：

在注册和登录时，需要通过 CAPTCHA 服务解决验证码。请根据您选择的 CAPTCHA 服务提供商获取 API Key：
CapMonster
2Captcha
示例：如果您使用 CapMonster，请填写您的 API Key：
```
CaptchaAPIKey = abcd1234efgh5678ijkl90mnopqr

```
运行程序
运行以下命令启动工具：
```
python main.py
```
根据提示选择所需功能：
```
==================================================
   NodePay CLI Bot
==================================================
1. 注册账户
2. 开始挖矿
3. 查看配置
4. 退出
==================================================
请输入你的选择：
```
### 功能详情
1. 注册账户
选择菜单中的 1，工具会自动读取 data/accounts.txt 和 data/proxies.txt，为每个账户完成注册。

注册所需的参数：

邮箱和密码（来自 accounts.txt）。
推荐码（从 ReferralCodes 中随机选择）。
CAPTCHA 验证（通过 CaptchaAPIKey 提供的服务解决）。

注册成功的日志示例：
```
INFO - 账户 user1@example.com 注册成功
```
2. 挖矿任务
选择菜单中的 2，工具会：

自动登录账户，获取用户的 Token 和 UID。
使用代理依次执行挖矿任务。
挖矿所需的参数：

登录账户的邮箱和密码。
每个账户使用三个代理执行挖矿任务。
挖矿操作发送到 API https://nw.nodepay.org/api/network/ping。
挖矿成功的日志示例：
```
INFO - 账户 user1@example.com 挖矿成功，代理 http://proxy1.example.com:8080
INFO - 账户 user1@example.com 挖矿成功，代理 http://proxy2.example.com:8080
INFO - 账户 user1@example.com 挖矿成功，代理 http://proxy3.example.com:8080
```
### 常见问题
如何处理 CAPTCHA 验证失败？

请确保 CaptchaAPIKey 填写正确。
检查您的 CAPTCHA 服务账户余额是否充足。
代理连接失败怎么办？

确保 proxies.txt 中的代理格式正确。
测试代理可用性，必要时更换代理源。
如何提高挖矿成功率？

增加代理数量，避免代理被封禁。
设置合理的延迟范围 (DelayMin 和 DelayMax) 以降低频率。
