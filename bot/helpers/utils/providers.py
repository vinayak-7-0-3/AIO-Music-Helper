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
from bot.helpers.utils.common import botsetting

async def checkLogins(provider):
    # return Error and Error Message
    if provider == "tidal":
        auth, msg = await checkLoginTidal()
        if auth:
            return False, msg
        else:
            return True, msg
    elif provider == "qobuz":
        if not botsetting.qobuz_auth:
            return True, lang.QOBUZ_NOT_AUTH
        return False, None
    elif provider == "deezer":
        if not botsetting.deezer_auth:
            return True, lang.DEEZER_NOT_AUTH
        return False, None
    elif provider == "kkbox":
        if not botsetting.kkbox_auth:
            return True, lang.KKBOX_NOT_AUTH
        return False, None
    elif provider == "spotify":
        if not botsetting.spotify_auth:
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
        botsetting.kkbox_auth = False
    # QOBUZ
    if not "" in {Config.QOBUZ_EMAIL, Config.QOBUZ_PASSWORD}:
        await qobuz.login('email')
    elif not "" in {Config.QOBUZ_USER, Config.QOBUZ_TOKEN}:
        await qobuz.login('token')
    else:
        botsetting.qobuz_auth = False
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
        botsetting.deezer_auth = False
    # SPOTIFY
    if not "" in {Config.SPOTIFY_EMAIL, Config.SPOTIFY_PASS}:
        try:
            await spotify_dl.login()
            botsetting.spotify_auth = True
        except Exception as e:
            LOGGER.debug('SPOTIFY : ' + e)
            botsetting.spotify_auth = False
    else:
        botsetting.spotify_auth = False

async def check_link(link):
    tidal = ["https://tidal.com", "https://listen.tidal.com", "tidal.com", "listen.tidal.com"]
    deezer = ["https://deezer.page.link", "https://deezer.com", "deezer.com", "https://www.deezer.com"]
    qobuz = ["https://play.qobuz.com", "https://open.qobuz.com", "https://www.qobuz.com"]
    kkbox = ["https://www.kkbox.com"]
    spotify = ["https://open.spotify.com"]
    if link.startswith(tuple(tidal)):
        return "tidal"
    elif link.startswith(tuple(deezer)):
        return "deezer"
    elif link.startswith(tuple(qobuz)):
        return "qobuz"
    elif link.startswith(tuple(kkbox)):
        return "kkbox"
    elif link.startswith(tuple(spotify)):
        return 'spotify'
    else:
        return None
