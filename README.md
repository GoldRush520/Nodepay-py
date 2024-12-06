一个用于自动化 Nodepay 空投交互的机器人，包括会话管理和带代理支持的 Ping 功
能。
1.获取 nodepay 的 token
在浏览器中打开 开发者工具（右键 > 检查 或 按 Ctrl+Shift+I，或 F12）。
进入开发者工具中的“控制台”或“Console”标签。
输入以下命令获取令牌：
先复制一遍命令
localStorage.getItem('np_webapp_token')
会出现以下字样
手动输入
allow pasting
再重新复制命令
红色的就是 token
并将您的 token 粘贴到文件中（每行一个令牌）。token.txt
例：token.txt
示例
ey...
ey...
ey...
2. 添加代理
将代理信息添加到 proxy.txt 中。每行的格式如下：
http://username:pass@ip:port
token.txt 里面一个 token 复制三遍，对应三个不同 IP
tokens.txt 一行一个 token 不用复制，这个文件用来检查代理的运行情况
