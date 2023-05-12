from config import Config

from bot.logger import LOGGER
from bot.helpers.translations import lang
from bot.helpers.qobuz.handler import qobuz
from bot.helpers.deezer.handler import deezerdl
from bot.helpers.kkbox.kkbox_helper import kkbox
from bot.helpers.spotify.handler import spotify_dl
from bot.helpers.tidal_func.events import loadTidal
from bot.helpers.database.postgres_impl import set_db
from bot.helpers.tidal_func.events import checkLoginTidal


async def checkLogins(provider):
    # return Error and Error Message
    if provider == "tidal":
        auth, msg = await checkLoginTidal()
        if auth:
            return False, msg
        else:
            return True, msg
    elif provider == "qobuz":
        auth, _ = set_db.get_variable("QOBUZ_AUTH")
        if not auth:
            return True, lang.QOBUZ_NOT_AUTH
        return False, None
    elif provider == "deezer":
        auth, _ = set_db.get_variable("DEEZER_AUTH")
        if not auth:
            return True, lang.DEEZER_NOT_AUTH
        return False, None
    elif provider == "kkbox":
        auth, _ = set_db.get_variable("KKBOX_AUTH")
        if not auth:
            return True, lang.KKBOX_NOT_AUTH
        return False, None
    elif provider == "spotify":
        auth, _ = set_db.get_variable("SPOTIFY_AUTH")
        if not auth:
            return True, lang.SPOTIFY_NOT_AUTH
        return False, None
    else:
        pass

async def loadConfigs():
    # TIDAL
    await loadTidal()
    tidal_auth, _ = set_db.get_variable("TIDAL_AUTH_DONE")
    LOGGER.debug(f'Loaded TIDAL - Auth Status : {tidal_auth}')

    # KKBOX
    if not "" in {Config.KKBOX_EMAIL, Config.KKBOX_KEY, Config.KKBOX_PASSWORD}:
        await kkbox.login()
        LOGGER.debug('Loaded KKBOX')
    else:
        set_db.set_variable("KKBOX_AUTH", False, False, None)
    # QOBUZ
    if not "" in {Config.QOBUZ_EMAIL, Config.QOBUZ_PASSWORD}:
        await qobuz.login('email')
    elif not "" in {Config.QOBUZ_USER, Config.QOBUZ_TOKEN}:
        await qobuz.login('token')
    else:
        set_db.set_variable("QOBUZ_AUTH", False, False, None)
    # DEEZER
    if not "" in {Config.DEEZER_EMAIL, Config.DEEZER_PASSWORD}:
        if Config.DEEZER_BF_SECRET == "":
            LOGGER.debug("Deezer BF Secret not provided. Get it from OrpheusDL Telegram Chat.")
            exit(1)
        if Config.DEEZER_TRACK_URL_KEY == "":
            LOGGER.debug("Deezer Track URL Key not provided. Get it from OrpheusDL Telegram Chat.")
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

async def check_link(link):
    tidal = ["https://tidal.com", "https://listen.tidal.com", "tidal.com", "listen.tidal.com"]
    deezer = ["https://deezer.page.link", "https://deezer.com", "deezer.com", "https://www.deezer.com"]
    qobuz = ["https://play.qobuz.com", "https://open.qobuz.com", "https://www.qobuz.com"]
    sc = []
    kkbox = ["https://www.kkbox.com"]
    spotify = ["https://open.spotify.com"]
    if link.startswith(tuple(tidal)):
        return "tidal"
    elif link.startswith(tuple(deezer)):
        return "deezer"
    elif link.startswith(tuple(qobuz)):
        return "qobuz"
    elif link.startswith(tuple(sc)):
        return "sc"
    elif link.startswith(tuple(kkbox)):
        return "kkbox"
    elif link.startswith(tuple(spotify)):
        return 'spotify'
    else:
        return None