import asyncio
from core import ConsoleMenu

if __name__ == "__main__":
    menu = ConsoleMenu()
    asyncio.run(menu.run())
