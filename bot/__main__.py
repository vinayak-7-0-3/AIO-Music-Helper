import os
import asyncio

from pyrogram import idle
from bot import aio, Config
from bot.logger import LOGGER
from bot.helpers.utils.tg_utils import get_chats
from bot.helpers.utils.providers import loadConfigs


async def start():
    # Load telegram chat auths etc
    await get_chats()
    # Load all Music Platform Modules
    await loadConfigs()
    
    if Config.ANIT_SPAM_MODE == "True":
            LOGGER.debug("BOT : ANTI-SPAM MODE ON")

if __name__ == "__main__":
    if not os.path.isdir(Config.DOWNLOAD_BASE_DIR):
        os.makedirs(Config.DOWNLOAD_BASE_DIR)
    
    loop = asyncio.new_event_loop()
    future = loop.run_until_complete(start())
    aio.start()
    LOGGER.debug("❤ MUSIC HELPER BOT BETA v0.30 STARTED SUCCESSFULLY ❤")
    idle()
    aio.stop()
    LOGGER.debug('Bot Exited Successfully ! Bye..........')