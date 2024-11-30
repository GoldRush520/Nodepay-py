import aiohttp
import uuid
import time
import re
from fake_useragent import UserAgent
from nodepaybot import logger  # 引入自定义日志

# 配置常量
HIDE_PROXY = "[HIDDEN]"
PING_INTERVAL = 1
RETRIES_LIMIT = 60
DOMAIN_API_ENDPOINTS = {
    "SESSION": ["https://api.nodepay.ai/api/auth/session"],
    "PING": [
        "http://52.77.10.116/api/network/ping",
        "http://13.215.134.222/api/network/ping"
    ]
}
CONNECTION_STATES = {
    "CONNECTED": 1,
    "DISCONNECTED": 2,
    "NO_CONNECTION": 3
}

# 会话和代理管理
status_connect = CONNECTION_STATES["NO_CONNECTION"]
browser_id = None
account_info = {}
last_ping_time = {}

def generate_uuid():
    return str(uuid.uuid4())

def validate_response(response):
    if not response or "code" not in response or response["code"] < 0:
        raise ValueError("无效的响应")
    return response

async def send_request(url, payload, proxy, token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": UserAgent().random,
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://app.nodepay.ai",
        "Origin": "chrome-extension://lgmpfmgeabnnlemejacfljbmonaomfmm",
        "X-Requested-With": "NodepayExtension"
    }
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=payload, headers=headers, proxy=proxy, timeout=60) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            error_code = getattr(e, 'status', 'Unknown')
            logger.log("ERROR", f"API请求失败: {e}")
            raise ValueError(f"API请求失败")

async def start_ping_loop(proxy, token):
    try:
        while True:
            await send_ping(proxy, token)
            await asyncio.sleep(PING_INTERVAL)
    except asyncio.CancelledError:
        pass
    except Exception:
        pass

async def send_ping(proxy, token):
    global last_ping_time, RETRIES_LIMIT, status_connect
    last_ping_time[proxy] = time.time()

    try:
        data = {
            "id": account_info.get("uid"),
            "browser_id": browser_id,
            "timestamp": int(time.time())
        }

        response = await send_request(DOMAIN_API_ENDPOINTS["PING"][0], data, proxy, token)
        if response["code"] == 0:
            ip_address = HIDE_PROXY if not proxy else re.search(r'(?<=@)[^:]+', proxy).group()
            logger.log("INFO", f"Ping成功, IP得分: {response['data'].get('ip_score')}, Proxy: {ip_address}")
            RETRIES_LIMIT = 0
            status_connect = CONNECTION_STATES["CONNECTED"]
        else:
            handle_ping_failure(proxy, response)
    except Exception:
        handle_ping_failure(proxy, None)

def handle_ping_failure(proxy, response):
    global RETRIES_LIMIT, status_connect
    RETRIES_LIMIT += 1
    ip_address = HIDE_PROXY if not proxy else re.search(r'(?<=@)[^:]+', proxy).group()
    error_message = response.get("message") if response else "No response from server"

    if response and response.get("code") == 403:
        logger.log("ERROR", f"Ping失败: Unauthorized Access, Proxy: {ip_address}")
    else:
        logger.log("ERROR", f"Ping失败, 原因: {error_message}, Proxy: {ip_address}")
        status_connect = CONNECTION_STATES["DISCONNECTED"]
