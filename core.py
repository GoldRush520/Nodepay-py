import asyncio
import os
import configparser
import random
from collections import deque
from loguru import logger
from faker import Faker
from pyuseragents import random as random_useragent

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
    def __init__(self, threads, ref_codes, captcha_service):
        self.threads = threads
        self.ref_codes = ref_codes
        self.captcha_service = captcha_service
        self.fake = Faker()

    async def register_account(self, email, password, proxies):
        for proxy in proxies:
            logger.info(f"注册账户：{email} 使用代理：{proxy}")
            await asyncio.sleep(random.uniform(1, 3))  # 模拟任务

    async def mine_account(self, email, token, proxies):
        for proxy in proxies:
            logger.info(f"账户 {email} 正在挖矿，使用代理：{proxy}")
            await asyncio.sleep(random.uniform(1, 3))  # 模拟任务

    async def process_account(self, email, password, action):
        proxies = await get_proxies(count=3)  # 获取 3 个代理
        try:
            if action == "register":
                await self.register_account(email, password, proxies)
            elif action == "mine":
                await self.mine_account(email, "dummy-token", proxies)
        finally:
            await release_proxies(proxies)  # 释放代理

# 命令行菜单
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
            threads=int(settings["Threads"]),
            ref_codes=settings["ReferralCodes"].split(","),
            captcha_service=captcha_service,
        )

        if choice == "1":
            for account in accounts:
                email, password = account.split(":")
                await manager.process_account(email, password, "register")
        elif choice == "2":
            for account in accounts:
                email, password = account.split(":")
                await manager.process_account(email, password, "mine")
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
