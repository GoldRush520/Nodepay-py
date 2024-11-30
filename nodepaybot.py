import asyncio
import time
import uuid
import sys
from termcolor import colored
from fake_useragent import UserAgent
import logging

# 创建自定义日志处理类
class CustomLogger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # 创建控制台输出处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)

        # 定义日志格式化
        formatter = logging.Formatter('%(message)s')
        console_handler.setFormatter(formatter)

        self.logger.addHandler(console_handler)

    def log(self, level, message):
        """
        根据不同的日志级别输出不同的颜色和格式
        """
        time_stamp = f"[{colored('Time', 'blue')}: {colored('%Y-%m-%d %H:%M:%S', 'cyan')}]"
        formatted_message = f"{time_stamp} - {colored(level, 'yellow')} - {message}"

        if level == "INFO":
            self.logger.info(colored(formatted_message, 'green'))
        elif level == "DEBUG":
            self.logger.debug(colored(formatted_message, 'blue'))
        elif level == "WARNING":
            self.logger.warning(colored(formatted_message, 'yellow'))
        elif level == "ERROR":
            self.logger.error(colored(formatted_message, 'red'))
        elif level == "CRITICAL":
            self.logger.critical(colored(formatted_message, 'magenta'))

# 初始化日志
logger = CustomLogger("NodepayBot")

def print_header():
    """
    自定义的程序启动欢迎界面
    """
    welcome_messages = [
        "你好，自动化世界！欢迎使用 NodepayBot，助你一臂之力！",
        "准备好让你的任务变得简单了吗？NodepayBot 即刻启程！",
        "准备迎接高效的工作方式了吗？NodepayBot 开始启动！"
    ]
    selected_welcome = welcome_messages[0]  # 选择欢迎语
    
    # 模拟加载进度条
    loading_bar = "加载中: [                    ]"
    for i in range(1, 21):
        time.sleep(0.2)
        loading_bar = "加载中: [" + "=" * i + " " * (20 - i) + "]"
        print(colored(loading_bar, 'cyan'), end='\r')
    print()

    # 打印欢迎信息
    print(colored("########################################", "green"))
    print(colored("#                                      #", "green"))
    print(colored(f"#         {selected_welcome}         #", "yellow"))
    print(colored("#                                      #", "green"))
    print(colored("########################################", "green"))
    print("-" * 60)
    logger.log("INFO", "NodepayBot启动成功，开始执行任务...")

# 示例主程序逻辑
async def main():
    print_header()

    try:
        logger.log("INFO", "加载配置文件和代理设置...")
        # 进一步的逻辑...
        logger.log("INFO", "配置加载完成。")
        await asyncio.sleep(2)
        logger.log("DEBUG", "开始执行任务...")
    except Exception as e:
        logger.log("ERROR", f"程序运行时遇到错误: {str(e)}")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.log("WARNING", "程序被用户中断。")
