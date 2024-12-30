# Nodepay 机器人
Nodepay 机器人



## 功能

  - 自动获取账户信息  
  - 如果选择 1，自动运行并使用自动代理 [使用 [Monosans 代理](https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/all.txt)]  
  - 如果选择 2，自动运行并使用手动代理 [将您的个人代理粘贴到 manual_proxy.txt 文件中]  
  - 如果选择 3，自动运行不使用代理  
  - 自动完成可用任务  
  - 每 1 分钟自动发送 Ping（3 种连接状态）  
  - 支持多账户并行运行

## 先决条件

确保您已安装 Python 3.9 和 PIP。

## 安装

1. **克隆仓库：**
   ```bash
   git clone https://github.com/ziqing888/Nodepay-py.git
   ```
```bash
cd Nodepay-py
 ```
2.安装依赖：
```bash
pip install -r requirements.txt #或者 pip3 install -r requirements.txt
```
## 配置
tokens.txt： 您将在项目目录中找到 tokens.txt 文件。确保 tokens.txt 文件包含符合脚本要求格式的数据。以下是文件格式示例：
```bash
  eyjxxxxx1
  eyjxxxxx2
```
manual_proxy.txt： 您将在项目目录中找到 manual_proxy.txt 文件。确保 manual_proxy.txt 文件包含符合脚本要求格式的数据。以下是文件格式示例：
```bash
ip:port（http 或 socks5 - 在 108 行更改协议）
http://ip:port
socks4://ip:port
socks5://ip:port
http://ip:port@user:pass（不确定是否有效，因为我没有认证代理）
socks4://ip:port@user:pass（不确定是否有效，因为我没有认证代理）
socks5://ip:port@user:pass（不确定是否有效，因为我没有认证代理）
```
## 运行脚本
```
python bot.py #或者 python3 bot.py
```
## 获取 nodepay 的 token

在浏览器中打开 开发者工具（右键 > 检查 或 按 Ctrl+Shift+I，或 F12）。

进入开发者工具中的“控制台”或“Console”标签。

输入以下命令获取令牌：
```bash
localStorage.getItem('np_webapp_token')
```
![image](https://github.com/user-attachments/assets/a806a4c5-0a7b-40e1-ac04-b0907b3552b8)


红色的就是 token

## 感谢您访问本仓库，别忘了给我们关注和加星。如果您有任何问题、发现问题或有改进建议，请随时联系我或在 GitHub 仓库中创建 issue。

