import time
import aigpy

import bot.helpers.tidal_func.apikey as apiKey

from bot.logger import LOGGER
from bot.helpers.translations import lang
from bot.helpers.utils.tg_utils import edit_message
from bot.helpers.database.postgres_impl import set_db
from bot.helpers.buttons.settings_buttons import common_auth_set
from bot.helpers.utils.common import post_cover, check_music_exist

from bot.helpers.tidal_func.tidal import *
from bot.helpers.tidal_func.enums import *
from bot.helpers.tidal_func.download import *
from bot.helpers.tidal_func.settings import TIDAL_TOKEN

def __displayTime__(seconds, granularity=2):
    if seconds <= 0:
        return "unknown"

    result = []
    intervals = (
        ('weeks', 604800),
        ('days', 86400),
        ('hours', 3600),
        ('minutes', 60),
        ('seconds', 1),
    )

    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append("{} {}".format(value, name))
    return ', '.join(result[:granularity])

async def loginByWeb(user):
    try:
        url = TIDAL_API.getDeviceCode()
        await edit_message(user, None, lang.TIDAL_AUTH_NEXT_STEP.format(url,__displayTime__(TIDAL_API.key.authCheckTimeout)))
        start = time.time()
        elapsed = 0
        while elapsed < TIDAL_API.key.authCheckTimeout:
            elapsed = time.time() - start
            if not TIDAL_API.checkAuthStatus():
                time.sleep(TIDAL_API.key.authCheckInterval + 1)
                continue

            await edit_message(
                user, 
                None, 
                lang.TIDAL_AUTH_SUCCESS.format(__displayTime__(int(TIDAL_API.key.expiresIn))),
                common_auth_set("tidal")
            )

            TIDAL_TOKEN.userid = TIDAL_API.key.userId
            TIDAL_TOKEN.countryCode = TIDAL_API.key.countryCode
            TIDAL_TOKEN.accessToken = TIDAL_API.key.accessToken
            TIDAL_TOKEN.refreshToken = TIDAL_API.key.refreshToken
            TIDAL_TOKEN.expiresAfter = time.time() + int(TIDAL_API.key.expiresIn)
            TIDAL_TOKEN.save()
            return True, None

        raise Exception("Tidal Login Operation timed out.")
    except Exception as e:
        return False, e

def loginByConfig():
    try:
        if aigpy.string.isNull(TIDAL_TOKEN.accessToken):
            return False, None
        # If token is valid, return True
        if TIDAL_API.verifyAccessToken(TIDAL_TOKEN.accessToken):
            msg = lang.TIDAL_ALREADY_AUTH.format(
                __displayTime__(int(TIDAL_TOKEN.expiresAfter - time.time())))

            TIDAL_API.key.countryCode = TIDAL_TOKEN.countryCode
            TIDAL_API.key.userId = TIDAL_TOKEN.userid
            TIDAL_API.key.accessToken = TIDAL_TOKEN.accessToken
            return True, msg
        # If token is not valid but refresh token is, refresh token and return True
        if TIDAL_API.refreshAccessToken(TIDAL_TOKEN.refreshToken):
            msg = lang.TIDAL_ALREADY_AUTH.format(
                __displayTime__(int(TIDAL_API.key.expiresIn)))

            TIDAL_TOKEN.userid = TIDAL_API.key.userId
            TIDAL_TOKEN.countryCode = TIDAL_API.key.countryCode
            TIDAL_TOKEN.accessToken = TIDAL_API.key.accessToken
            TIDAL_TOKEN.expiresAfter = time.time() + int(TIDAL_API.key.expiresIn)
            TIDAL_TOKEN.save()
            return True, msg
        else:
            TokenSettings().save()
            return False, None
    except Exception as e:
        return False, None

async def checkLoginTidal():
    db_auth, _ = set_db.get_variable("TIDAL_AUTH_DONE")
    if not db_auth:
        return False, lang.TIDAL_NOT_AUTH
    auth, msg = loginByConfig()
    if auth:
        return True, msg
    else:
        return False, lang.TIDAL_NOT_AUTH

async def loadTidal():
    TIDAL_SETTINGS.read()
    TIDAL_TOKEN.read()
    await checkAPITidal()

'''
=================================
START DOWNLOAD
=================================
'''
async def startTidal(string, user):
    strings = string.split(" ")
    for item in strings:
        if aigpy.string.isNull(item):
            continue
        try:
            etype, obj, sid = TIDAL_API.getByString(item)
        except Exception as e:
            await LOGGER.error(str(e) + " [" + item + "]", user)
            return

        try:
            await start_type(etype, obj, sid, user)
        except Exception as e:
            await LOGGER.error(str(e), user)

async def start_type(etype: Type, obj, sid, user):
    if etype == Type.Album:
        await start_album(obj, sid, user)
    elif etype == Type.Track:
        await start_track(obj, sid, user)
    elif etype == Type.Artist:
        await start_artist(obj, sid, user)
    elif etype == Type.Playlist:
        await start_playlist(obj, sid, user)
    elif etype == Type.Mix:
        await start_mix(obj, sid, user)

async def start_mix(obj: Mix, sid, user):
    for index, item in enumerate(obj.tracks):
        album = TIDAL_API.getAlbum(item.album.id)
        item.trackNumberOnPlaylist = index + 1
        await downloadTrack(item, album, user=user, type='mix', sid=sid)

async def start_playlist(obj: Playlist, sid, user):
    tracks, videos = TIDAL_API.getItems(obj.uuid, Type.Playlist)
    for index, item in enumerate(tracks):
        album = TIDAL_API.getAlbum(item.album.id)
        item.trackNumberOnPlaylist = index + 1
        await downloadTrack(item, album, obj, user=user, type='playlist', sid=sid)

async def start_artist(obj: Artist, sid, user):
    albums = TIDAL_API.getArtistAlbums(obj.id, TIDAL_SETTINGS.includeEP)
    for item in albums:
        await start_album(item, sid, user)

async def start_track(obj: Track, sid, user):
    album = TIDAL_API.getAlbum(obj.album.id)
    await downloadTrack(obj, album, user=user, sid=sid)

async def start_album(obj: Album, sid, user):
    tracks, _ = TIDAL_API.getItems(obj.id, Type.Album)
    meta = await albumMeta(tracks[0], obj)
    meta['item_id'] = sid
    dupe = await check_music_exist(meta, user, 'album')
    if dupe: return
    await post_cover(meta, user)
    await downloadTracks(tracks, obj, None, user=user)


'''
=================================
TIDAL API CHECKS
=================================
'''

async def checkAPITidal():
    if not apiKey.isItemValid(TIDAL_SETTINGS.apiKeyIndex):
        await LOGGER.error(lang.ERR_TD_API_KEY)
    else:
        index = TIDAL_SETTINGS.apiKeyIndex
        TIDAL_API.apiKey = apiKey.getItem(index)

async def getapiInfoTidal():
    i = 0
    platform = []
    validity = []
    quality = []
    index = []
    list = apiKey.__API_KEYS__
    for item in list['keys']:
        index.append(i)
        platform.append(item['platform'])
        validity.append(item['valid'])
        quality.append(item['formats'])
        i += 1
    return index, platform, validity, quality
