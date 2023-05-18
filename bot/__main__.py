import os

from pyrogram import Client
from bot import Config, LOGGER

from bot.helpers.utils.auth_check import get_chats

from bot.helpers.qobuz.handler import qobuz
from bot.helpers.deezer.handler import deezerdl
from bot.helpers.kkbox.kkbox_helper import kkbox
from bot.helpers.spotify.handler import spotify_dl
from bot.helpers.database.postgres_impl import set_db
from bot.helpers.tidal_func.events import checkAPITidal
from bot.helpers.tidal_func.settings import TIDAL_SETTINGS, TIDAL_TOKEN

plugins = dict(
    root="bot/modules"
)

async def loadConfigs():
    # TIDAL
    TIDAL_SETTINGS.read()
    TIDAL_TOKEN.read("./tidal-dl.token.json")
    await checkAPITidal()
    LOGGER.info('Loaded TIDAL Successfully')
    # KKBOX
    if not "" in {Config.KKBOX_EMAIL, Config.KKBOX_KEY, Config.KKBOX_PASSWORD}:
        await kkbox.login()
        LOGGER.info('Loaded KKBOX Successfully')
    else:
        set_db.set_variable("KKBOX_AUTH", False, False, None)
    # QOBUZ
    if not "" in {Config.QOBUZ_EMAIL, Config.QOBUZ_PASSWORD}:
        await qobuz.login()
    else:
        set_db.set_variable("QOBUZ_AUTH", False, False, None)
    # DEEZER
    if not "" in {Config.DEEZER_EMAIL, Config.DEEZER_PASSWORD}:
        if Config.DEEZER_BF_SECRET == "":
            LOGGER.warning("Deezer BF Secret not provided. Get it from OrpheusDL Telegram Chat.")
            exit(1)
        if Config.DEEZER_TRACK_URL_KEY == "":
            LOGGER.warning("Deezer Track URL Key not provided. Get it from OrpheusDL Telegram Chat.")
            exit(1)
        await deezerdl.login()
    elif Config.DEEZER_ARL != "":
        await deezerdl.login(True)
    else:
        set_db.set_variable("DEEZER_AUTH", False, False, None)
    if not "" in {Config.SPOTIFY_EMAIL, Config.SPOTIFY_PASS}:
        await spotify_dl.login()
        set_db.set_variable("SPOTIFY_AUTH", True, False, None)
    else:
        set_db.set_variable("SPOTIFY_AUTH", False, False, None)
        

class Bot(Client):
    def __init__(self):
        super().__init__(
            "AIO-Music-Bot",
            api_id=Config.APP_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.TG_BOT_TOKEN,
            plugins=plugins,
            workdir=Config.WORK_DIR
        )

    async def start(self):
        await super().start()

        await loadConfigs()
        
        if Config.ANIT_SPAM_MODE == "True":
            LOGGER.info("ANTI-SPAM MODE ON")
        await get_chats()
        LOGGER.info("❤ MUSIC HELPER BOT BETA v0.30 STARTED SUCCESSFULLY ❤")

    async def stop(self, *args):
        await super().stop()
        LOGGER.info('Bot Exited Successfully ! Bye..........')

if __name__ == "__main__":
    if not os.path.isdir(Config.DOWNLOAD_BASE_DIR):
        os.makedirs(Config.DOWNLOAD_BASE_DIR)
    app = Bot()
    app.run()
