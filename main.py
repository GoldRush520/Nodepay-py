from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout
)
from curl_cffi import requests
from aiohttp_socks import ProxyConnector
from colorama import *
from datetime import datetime
from fake_useragent import FakeUserAgent
import asyncio, time, json, os, uuid, pytz

wib = pytz.timezone('Asia/Shanghai')

class Nodepay:
    def __init__(self) -> None:
        self.headers = {
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9", 
            "Origin": "https://app.nodepay.ai",
            "Referer": "https://app.nodepay.ai/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "User-Agent": FakeUserAgent().random
        }
        self.proxies = []
        self.proxy_index = 0

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}自动Ping {Fore.BLUE + Style.BRIGHT}Nodepay - 机器人
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<水印信息>
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    async def load_auto_proxies(self):
        url = "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/all.txt"
        try:
            async with ClientSession(timeout=ClientTimeout(total=20)) as session:
                async with session.get(url=url) as response:
                    response.raise_for_status()
                    content = await response.text()
                    with open('proxy.txt', 'w') as f:
                        f.write(content)

                    self.proxies = content.splitlines()
                    if not self.proxies:
                        self.log(f"{Fore.RED + Style.BRIGHT}下载的代理列表中没有找到代理！{Style.RESET_ALL}")
                        return
                    
                    self.log(f"{Fore.GREEN + Style.BRIGHT}代理成功下载.{Style.RESET_ALL}")
                    self.log(f"{Fore.YELLOW + Style.BRIGHT}加载了 {len(self.proxies)} 个代理.{Style.RESET_ALL}")
                    self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"*75)
                    await asyncio.sleep(3)
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}加载代理失败: {e}{Style.RESET_ALL}")
            return []
        
    async def load_manual_proxy(self):
        try:
            if not os.path.exists('manual_proxy.txt'):
                print(f"{Fore.RED + Style.BRIGHT}未找到代理文件 'manual_proxy.txt'！{Style.RESET_ALL}")
                return

            with open('manual_proxy.txt', "r") as f:
                proxies = f.read().splitlines()

            self.proxies = proxies
            self.log(f"{Fore.YELLOW + Style.BRIGHT}加载了 {len(self.proxies)} 个代理.{Style.RESET_ALL}")
            self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"*75)
            await asyncio.sleep(3)
        except Exception as e:
            print(f"{Fore.RED + Style.BRIGHT}加载手动代理失败: {e}{Style.RESET_ALL}")
            self.proxies = []

    def get_next_proxy(self):
        if not self.proxies:
            self.log(f"{Fore.RED + Style.BRIGHT}没有可用的代理！{Style.RESET_ALL}")
            return None

        proxy = self.proxies[self.proxy_index]
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
    
    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        
        return f"http://{proxies}"
    
    def hide_token(self, token):
        hide_token = token[:3] + '*' * 3 + token[-3:]
        return hide_token
    
    async def user_session(self, token: str, proxy=None):
        url = "http://api.nodepay.ai/api/auth/session"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Length": "2",
            "Content-Type": "application/json",
        }
        connector = ProxyConnector.from_url(proxy) if proxy else None
        try:
            async with ClientSession(connector=connector, timeout=ClientTimeout(total=30)) as session:
                async with session.post(url=url, headers=headers, json={}) as response:
                    response.raise_for_status()
                    result = await response.json()
                    return result['data']
        except (Exception, ClientResponseError) as e:
            return None
    
    async def user_earning(self, token: str, proxy=None):
        url = "http://api.nodepay.ai/api/earn/info"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        connector = ProxyConnector.from_url(proxy) if proxy else None
        try:
            async with ClientSession(connector=connector, timeout=ClientTimeout(total=30)) as session:
                async with session.get(url=url, headers=headers) as response:
                    response.raise_for_status()
                    result = await response.json()
                    return result['data']
        except (Exception, ClientResponseError) as e:
            return None
    
    async def mission_lists(self, token: str, proxy=None):
        url = "http://api.nodepay.ai/api/mission"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        connector = ProxyConnector.from_url(proxy) if proxy else None
        try:
            async with ClientSession(connector=connector, timeout=ClientTimeout(total=30)) as session:
                async with session.get(url=url, headers=headers) as response:
                    response.raise_for_status()
                    result = await response.json()
                    return result['data']
        except (Exception, ClientResponseError) as e:
            return None
    
    async def complete_missions(self, token: str, mission_id: str, proxy=None):
        url = "http://api.nodepay.ai/api/mission/complete-mission"
        data = json.dumps({'mission_id':mission_id})
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json",
        }
        connector = ProxyConnector.from_url(proxy) if proxy else None
        try:
            async with ClientSession(connector=connector, timeout=ClientTimeout(total=30)) as session:
                async with session.post(url=url, headers=headers, data=data) as response:
                    response.raise_for_status()
                    result = await response.json()
                    return result['data']
        except (Exception, ClientResponseError) as e:
            return None

    def send_ping(self, token: str, id: str, proxy=None, retries=60):
        url = "https://nw.nodepay.org/api/network/ping"
        data = json.dumps({
            "id":id, 
            "browser_id":str(uuid.uuid4()), 
            "timestamp":int(time.time()), 
            "version":"2.2.7"
        })
        headers = {
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9",  # 设置为中文
            "Authorization": f"Bearer {token}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json",
            "Origin": "chrome-extension://lgmpfmgeabnnlemejacfljbmonaomfmm",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "User-Agent": FakeUserAgent().random
        }
        for attempt in range(retries):
            try:
                response = requests.post(
                    url=url, 
                    headers=headers, 
                    data=data, 
                    proxies={"http": proxy, "https": proxy} if proxy else None, 
                    timeout=30, 
                    impersonate="safari15_5"
                )
                response.raise_for_status()
                result = response.json()
                return result['data']
            except requests.RequestsError as e:
                if attempt < retries - 1:
                    continue
                return None
        
    async def connection_state(self, token, username, id, proxy):
        while True:
            result = await asyncio.to_thread(self.send_ping, token, id, proxy)
            if result and isinstance(result, dict):
                ip_score = result.get("ip_score")
                if ip_score is not None:
                    self.log(
                        f"{Fore.MAGENTA + Style.BRIGHT}[ 账号{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {username} {Style.RESET_ALL}"
                        f"{Fore.GREEN + Style.BRIGHT}Ping成功{Style.RESET_ALL} "
                        f"{Fore.WHITE + Style.BRIGHT}使用代理 {proxy} {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}] [ Ip分数{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {ip_score} {Style.RESET_ALL} "
                        f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                    )
            else:
                self.log(
                    f"{Fore.MAGENTA + Style.BRIGHT}[ 账号{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {username} {Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT}Ping失败{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} 使用代理 {proxy} {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.BLUE + Style.BRIGHT} 正在尝试下一个代理... {Style.RESET_ALL}"
                )
                proxy = self.get_next_proxy()
                if not proxy:
                    self.log(
                        f"{Fore.MAGENTA + Style.BRIGHT}[ 账号{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {username} {Style.RESET_ALL}"
                        f"{Fore.RED + Style.BRIGHT}没有找到代理{Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT} ]{Style.RESET_ALL}"
                    )
                    break
                proxy = self.check_proxy_schemes(proxy)

            print(
                f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT}下一次Ping将在1分钟后进行{Style.RESET_ALL}"
                f"{Fore.YELLOW + Style.BRIGHT} 等待... {Style.RESET_ALL}",
                end="\r"
            )
            await asyncio.sleep(60)
        
    async def question(self):
        while True:
            try:
                print("1. 使用自动代理运行")
                print("2. 使用手动代理运行")
                print("3. 不使用代理运行")
                choose = int(input("请选择 [1/2/3] -> ").strip())

                if choose in [1, 2, 3]:
                    proxy_type = (
                        "使用自动代理" if choose == 1 else 
                        "使用手动代理" if choose == 2 else 
                        "不使用代理"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}选择了 {proxy_type} 模式.{Style.RESET_ALL}")
                    await asyncio.sleep(1)
                    return choose
                else:
                    print(f"{Fore.RED + Style.BRIGHT}请输入1、2或3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}无效输入。请输入数字（1、2或3）。{Style.RESET_ALL}")
            
    async def process_accounts(self, token: str, use_proxy: bool):
        # 隐藏token信息，提升安全性
        hide_token = self.hide_token(token)
        proxy = None

        if not use_proxy:
            # 不使用代理时，直接获取用户信息和收益信息
            user = await self.user_session(token)
            earn = await self.user_earning(token)
            
            if not user or not earn:
                # 登录失败日志输出
                self.log(
                    f"{Fore.MAGENTA + Style.BRIGHT}[ 账号{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {hide_token} {Style.RESET_ALL}"
                    f"{Fore.RED + Style.BRIGHT} 登录失败{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} 无代理 {proxy} {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                )
                return
            
            # 获取用户名和用户ID
            username = user['name']
            id = user['uid']
            
            # 登录成功并输出用户收益情况
            self.log(
                f"{Fore.MAGENTA + Style.BRIGHT}[ 账号{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {username} {Style.RESET_ALL}"
                f"{Fore.GREEN + Style.BRIGHT} 登录成功{Style.RESET_ALL}"
                f"{Fore.MAGENTA + Style.BRIGHT} ] [ 收益{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} 总计 {earn['total_earning']} 积分 {Style.RESET_ALL}"
                f"{Fore.MAGENTA + Style.BRIGHT} -{Style.RESET_ALL} "
                f"{Fore.WHITE + Style.BRIGHT} 今日 {earn['today_earning']} 积分 {Style.RESET_ALL}"
                f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
            )
            await asyncio.sleep(1)

            # 获取任务列表
            missions = await self.mission_lists(token)
            if missions:
                completed = False
                for mission in missions:
                    mission_id = mission['id']
                    status = mission['status']
                    if mission and status == "AVAILABLE":
                        # 完成任务
                        complete = await self.complete_missions(token, mission_id)
                        if complete:
                            self.log(
                                f"{Fore.MAGENTA + Style.BRIGHT}[ 账号{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} {username} {Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT} -{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} {mission['title']} {Style.RESET_ALL}"
                                f"{Fore.GREEN + Style.BRIGHT} 已完成{Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT} ] [ 奖励{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} {mission['point']} {Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                            )
                        else:
                            self.log(
                                f"{Fore.MAGENTA + Style.BRIGHT}[ 账号{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} {username} {Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT} -{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} {mission['title']} {Style.RESET_ALL}"
                                f"{Fore.RED + Style.BRIGHT} 未完成{Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT} ]{Style.RESET_ALL}"
                            )
                    else:
                        completed = True

                if completed:
                    self.log(
                        f"{Fore.MAGENTA + Style.BRIGHT}[ 账号{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {username} {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT} -{Style.RESET_ALL}"
                        f"{Fore.GREEN + Style.BRIGHT} 可用任务已完成 {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                    )
            else:
                self.log(
                    f"{Fore.MAGENTA + Style.BRIGHT}[ 账号{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {username} {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT} -{Style.RESET_ALL}"
                    f"{Fore.RED + Style.BRIGHT} 任务数据为空 {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                )
            await asyncio.sleep(1)

            # 输出正在进行的ping请求状态
            print(
                f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT} 正在发送 Ping,{Style.RESET_ALL}"
                f"{Fore.YELLOW + Style.BRIGHT} 等待中... {Style.RESET_ALL}",
                end="\r",
                flush=True
            )
            await asyncio.sleep(1)

            while True:
                ping = self.send_ping(token, id)
                if not ping:
                    self.log(
                        f"{Fore.MAGENTA + Style.BRIGHT}[ 账号{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {username} {Style.RESET_ALL}"
                        f"{Fore.YELLOW + Style.BRIGHT} Ping失败{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} 无代理 {proxy} {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                    )
                    await asyncio.sleep(1)

                    print(
                        f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.BLUE + Style.BRIGHT} 下一次Ping在1分钟后.{Style.RESET_ALL}"
                        f"{Fore.YELLOW + Style.BRIGHT} 等待中... {Style.RESET_ALL}",
                        end="\r"
                    )
                    await asyncio.sleep(60)
                    continue

                self.log(
                    f"{Fore.MAGENTA + Style.BRIGHT}[ 账号{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {username} {Style.RESET_ALL}"
                    f"{Fore.GREEN + Style.BRIGHT} Ping成功{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} 无代理 {proxy} {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}] [ IP得分{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {ping['ip_score']} {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                )
                await asyncio.sleep(1)

                print(
                    f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                    f"{Fore.BLUE + Style.BRIGHT} 下一次Ping在1分钟后.{Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT} 等待中... {Style.RESET_ALL}",
                    end="\r"
                )
                await asyncio.sleep(60)

        else:
            # 使用代理时，获取代理并循环进行尝试
            user = None
            earn = None
            proxies = self.get_next_proxy()
            proxy = self.check_proxy_schemes(proxies)

            while user is None or earn is None:
                user = await self.user_session(token, proxy)
                earn = await self.user_earning(token, proxy)

                if not user or not earn:
                    self.log(
                        f"{Fore.MAGENTA + Style.BRIGHT}[ 账号{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {hide_token} {Style.RESET_ALL}"
                        f"{Fore.RED + Style.BRIGHT} 登录失败{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} 使用代理 {proxy} {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                    )
                    await asyncio.sleep(1)

                    print(
                        f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.BLUE + Style.BRIGHT} 正在尝试下一个代理,{Style.RESET_ALL}"
                        f"{Fore.YELLOW + Style.BRIGHT} 等待中... {Style.RESET_ALL}",
                        end="\r",
                        flush=True
                    )

                    proxies = self.get_next_proxy()
                    proxy = self.check_proxy_schemes(proxies)
                    continue
            
            # 用户登录成功后的操作与不使用代理时类似
            username = user['name']
            id = user['uid']

            self.log(
                f"{Fore.MAGENTA + Style.BRIGHT}[ 账号{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {username} {Style.RESET_ALL}"
                f"{Fore.GREEN + Style.BRIGHT} 登录成功{Style.RESET_ALL}"
                f"{Fore.MAGENTA + Style.BRIGHT} ] [ 收益{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} 总计 {earn['total_earning']} 积分 {Style.RESET_ALL}"
                f"{Fore.MAGENTA + Style.BRIGHT} -{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} 今日 {earn['today_earning']} 积分 {Style.RESET_ALL}"
                f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
            )
            await asyncio.sleep(1)

            # 获取任务列表并处理
            missions = await self.mission_lists(token, proxy)
            if missions:
                completed = False
                for mission in missions:
                    mission_id = mission['id']
                    status = mission['status']
                    if mission and status == "AVAILABLE":
                        complete = await self.complete_missions(token, mission_id, proxy)
                        if complete:
                            self.log(
                                f"{Fore.MAGENTA + Style.BRIGHT}[ 账号{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} {username} {Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT} -{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} {mission['title']} {Style.RESET_ALL}"
                                f"{Fore.GREEN + Style.BRIGHT} 已完成{Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT} ] [ 奖励{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} {mission['point']} {Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                            )
                        else:
                            self.log(
                                f"{Fore.MAGENTA + Style.BRIGHT}[ 账号{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} {username} {Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT} -{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} {mission['title']} {Style.RESET_ALL}"
                                f"{Fore.RED + Style.BRIGHT} 未完成{Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT} ]{Style.RESET_ALL}"
                            )
                    else:
                        completed = True

                if completed:
                    self.log(
                        f"{Fore.MAGENTA + Style.BRIGHT}[ 账号{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {username} {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT} -{Style.RESET_ALL}"
                        f"{Fore.GREEN + Style.BRIGHT} 可用任务已完成 {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                    )
            else:
                self.log(
                    f"{Fore.MAGENTA + Style.BRIGHT}[ 账号{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {username} {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT} -{Style.RESET_ALL}"
                    f"{Fore.RED + Style.BRIGHT} 任务数据为空 {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                )
            await asyncio.sleep(1)

            # 输出正在进行的ping请求状态
            print(
                f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT} 正在发送 Ping,{Style.RESET_ALL}"
                f"{Fore.YELLOW + Style.BRIGHT} 等待中... {Style.RESET_ALL}",
                end="\r",
                flush=True
            )
            await asyncio.sleep(1)

            # 选择多个代理并进行连接状态验证
            selected_proxies = []

            for _ in range(3):
                proxy = self.get_next_proxy()
                if proxy:
                    selected_proxies.append(self.check_proxy_schemes(proxy))

            # 创建多个任务进行并发处理
            tasks = [
                asyncio.create_task(self.connection_state(token, username, id, proxy))
                for proxy in selected_proxies
            ]
            await asyncio.gather(*tasks)

    async def main(self):
        try:
            with open('tokens.txt', 'r') as file:
                tokens = [line.strip() for line in file if line.strip()]

            use_proxy_choice = await self.question()

            use_proxy = False
            if use_proxy_choice in [1, 2]:
                use_proxy = True

            self.clear_terminal()
            self.welcome()
            self.log(
                f"{Fore.GREEN + Style.BRIGHT}总账户数: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(tokens)}{Style.RESET_ALL}"
            )
            self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"*75)

            if use_proxy and use_proxy_choice == 1:
                await self.load_auto_proxies()
            elif use_proxy and use_proxy_choice == 2:
                await self.load_manual_proxy()

            while True:
                tasks = []
                for token in tokens:
                    token = token.strip()
                    if token:
                        tasks.append(self.process_accounts(token, use_proxy))

                await asyncio.gather(*tasks)

        except FileNotFoundError:
            self.log(f"{Fore.RED}文件 'tokens.txt' 未找到。{Style.RESET_ALL}")
            return
        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}错误: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        bot = Nodepay()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ 退出 ] Nodepay - 机器人{Style.RESET_ALL}                                       "                              
        )
