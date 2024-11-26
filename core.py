import asyncio
import os
import configparser
import random
import time
from collections import deque
from loguru import logger
from faker import Faker
from pyuseragents import random as random_useragent
import aiohttp

# 日志设置
logger.add("logs/app.log", rotation="1 day", level="INFO")

# 文件工具
def file_to_list(filename):
    with open(filename, "r") as f:
        return [line.strip() for line in f if line.strip()]

def str_to_file(file_name, msg, mode="a"):
    with open(file_name, mode) as f:
        f.write(f"{msg}\n")

# 代理管理
proxies = deque()
lock = asyncio.Lock()

def load_proxy(proxy_path):
    global proxies
    proxies = deque(file_to_list(proxy_path))

async def get_proxy():
    """获取一个代理"""
    async with lock:
        return proxies.popleft() if proxies else None

async def get_proxies(count=3):
    """获取指定数量的代理"""
    async with lock:
        selected_proxies = [proxies.popleft() for _ in range(min(count, len(proxies)))]
        return selected_proxies

async def release_proxies(used_proxies):
    """释放多个代理回到队列"""
    async with lock:
        proxies.extend(used_proxies)

# CAPTCHA 验证服务
class CaptchaService:
    def __init__(self, api_key):
        self.api_key = api_key

    async def get_captcha_token(self):
        await asyncio.sleep(1)  # 模拟 CAPTCHA 验证
        return "dummy-captcha-token"

# 账户管理器
class AccountManager:
    def __init__(self, captcha_service, ref_codes):
        self.captcha_service = captcha_service
        self.ref_codes = ref_codes
        self.fake = Faker()

    async def register_account(self, email, password, proxy):
        url = "https://api.nodepay.org/api/auth/register"
        captcha_token = await self.captcha_service.get_captcha_token()

        data = {
            "email": email,
            "password": password,
            "username": f"user_{random.randint(1000, 9999)}",
            "referral_code": random.choice(self.ref_codes),
            "recaptcha_token": captcha_token,
        }

        headers = {
            "User-Agent": random_useragent(),
            "Content-Type": "application/json",
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, headers=headers, proxy=proxy) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("success"):
                        logger.info(f"账户 {email} 注册成功")
                        return True
                    else:
                        logger.error(f"账户 {email} 注册失败: {result.get('msg')}")
                        return False
                else:
                    logger.error(f"账户 {email} 注册失败，HTTP状态码: {response.status}")
                    return False

    async def get_auth_token(self, email, password, proxy):
        url = "https://api.nodepay.org/api/auth/login"
        captcha_token = await self.captcha_service.get_captcha_token()

        data = {
            "user": email,
            "password": password,
            "remember_me": True,
            "recaptcha_token": captcha_token,
        }

        headers = {
            "User-Agent": random_useragent(),
            "Content-Type": "application/json",
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, headers=headers, proxy=proxy) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("success"):
                        logger.info(f"账户 {email} 登录成功")
                        uid = result["data"]["user_info"]["uid"]
                        token = result["data"]["token"]
                        return uid, token
                    else:
                        logger.error(f"账户 {email} 登录失败: {result.get('msg')}")
                        return None, None
                else:
                    logger.error(f"账户 {email} 登录失败，HTTP状态码: {response.status}")
                    return None, None

    async def mine_account(self, email, uid, token, proxies):
        url = "https://nw.nodepay.org/api/network/ping"
        headers = {
            "Authorization": f"Bearer {token}",
            "User-Agent": random_useragent(),
            "Content-Type": "application/json",
        }

        data = {
            "id": uid,
            "browser_id": f"browser_{random.randint(1000, 9999)}",
            "timestamp": int(time.time()),
            "version": "2.2.7",
        }

        for proxy in proxies:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, headers=headers, proxy=proxy) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get("success"):
                            logger.info(f"账户 {email} 挖矿成功，代理 {proxy}")
                        else:
                            logger.warning(f"账户 {email} 挖矿失败: {result.get('msg')}")
                    else:
                        logger.error(f"账户 {email} 挖矿失败，HTTP状态码: {response.status}")

# CLI 菜单
class ConsoleMenu:
    def __init__(self, config_file="data/settings.ini"):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        config = configparser.ConfigParser()
        if not os.path.exists(self.config_file):
            logger.error(f"配置文件 {self.config_file} 不存在。")
            exit(1)
        config.read(self.config_file)
        return config

    def print_menu(self):
        print("\n" + "=" * 50)
        print("1. 注册账户")
        print("2. 开始挖矿")
        print("3. 查看配置")
        print("4. 退出")
        print("=" * 50 + "\n")

    async def handle_action(self, choice):
        settings = self.config["DEFAULT"]
        accounts = file_to_list(settings["AccountsFile"])
        load_proxy(settings["ProxiesFile"])  # 加载代理列表
        captcha_service = CaptchaService(api_key=settings["CaptchaAPIKey"])
        manager = AccountManager(
            captcha_service=captcha_service,
            ref_codes=settings["ReferralCodes"].split(","),
        )

        if choice == "1":
            for account in accounts:
                email, password = account.split(":")
                proxy = await get_proxy()
                await manager.register_account(email, password, proxy)
                await release_proxies([proxy])
        elif choice == "2":
            for account in accounts:
                email, password = account.split(":")
                proxy = await get_proxy()
                uid, token = await manager.get_auth_token(email, password, proxy)
                if uid and token:
                    proxies = await get_proxies(count=3)
                    await manager.mine_account(email, uid, token, proxies)
                    await release_proxies(proxies)
        elif choice == "3":
            self.show_settings()

    def show_settings(self):
        for key, value in self.config["DEFAULT"].items():
            print(f"{key}: {value}")

    async def run(self):
        while True:
            self.print_menu()
            choice = input("请输入你的选择：").strip()
            if choice == "4":
                logger.info("退出程序...")
                break
            elif choice in ["1", "2", "3"]:
                await self.handle_action(choice)
            else:
                logger.warning("无效的选择，请重新输入。")

