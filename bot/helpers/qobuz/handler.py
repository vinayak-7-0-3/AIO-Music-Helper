from bot.helpers.qobuz.utils import *
from bot.helpers.qobuz.qopy import qobuz_api
from bot.helpers.utils.tg_utils import send_message
from bot.helpers.utils.common import post_cover, check_music_exist
from bot.helpers.database.postgres_impl import set_db


class QobuzDL:
    def __init__(self):
        self.embed_art = False
        self.ignore_singles_eps = False
        self.no_m3u_for_playlists = False
        self.quality_fallback = True

    async def login(self, auth):
        try:
            qobuz_api.login(auth)
            set_db.set_variable("QOBUZ_AUTH", True, False, None)
        except Exception as e:
            await LOGGER.error(e)
            set_db.set_variable("QOBUZ_AUTH", False, False, None)

    async def start(self, url, user):
        items, item_id, type_dict, content = await check_type(url)

        if items:
            # FOR ARTIST/LABEL
            if type_dict['iterable_key'] == 'albums':
                    for item in items:
                        await self.startAlbum(item['id'], user)
            else:
            # FOR PLAYLIST 
                for item in items:
                    await self.startTrack(item['id'], user)
        else:
            if type_dict["album"]:
                await self.startAlbum(item_id, user)
            else:
                await self.startTrack(item_id, user)

    async def startTrack(self, item_id, user, type='track'):
        metadata, raw_meta, err = await get_metadata(item_id)
        if err:
            await LOGGER.error(err, user)
            await send_message(user, err)
            return
        
        dupe = await check_music_exist(metadata, user, t_source=type)
        if dupe: return
        
        metadata['extension'], metadata['quality'] = await check_quality(raw_meta)        
        
        await download_track(item_id, user, metadata, type)

    async def startAlbum(self, item_id, user):
        metadata, raw_meta, err = await get_metadata(item_id, 'album')
        if err:
            await LOGGER.error(err, user)
            return
        
        dupe = await check_music_exist(metadata, user, 'album')
        if dupe: return

        ext, quality = await check_quality(raw_meta, 'album')
        metadata['quality'] = quality
        metadata['extension'] = ext
        await post_cover(metadata, user)
        tracks = raw_meta['tracks']['items']
        for track in tracks:
            try:
                await self.startTrack(track['id'], user, 'album')
            except Exception as e:
                await LOGGER.error(e, user)

qobuz = QobuzDL()