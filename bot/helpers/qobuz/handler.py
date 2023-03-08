from config import LOGGER, Config

from bot.helpers.qobuz.utils import *
from bot.helpers.qobuz.qopy import qobuz_api


class QobuzDL:
    def __init__(self):
        self.embed_art = False
        self.ignore_singles_eps = False
        self.no_m3u_for_playlists = False
        self.quality_fallback = True
        self.folder_format = "{artist} - {album} ({year}) [{bit_depth}B-"
        "{sampling_rate}kHz]"
        self.track_format = Config.QOBUZ_TRACK_FORMAT


    async def login(self):
        qobuz_api.login()

    async def start(self, url, bot, update, r_id, u_name):
        items, item_id, type_dict, content = await check_type(url)

        if items:
            # FOR ARTIST/LABEL
            if type_dict['iterable_key'] == 'albums':
                    for item in items:
                        await self.startAlbum(item['id'], r_id, u_name, bot=bot, update=update)
            else:
            # FOR PLAYLIST 
                for item in items:
                    await self.startTrack(bot, update, item['id'], r_id, u_name)
        else:
            if type_dict["album"]:
                await self.startAlbum(item_id, r_id, u_name, bot=bot, update=update)
            else:
                await self.startTrack(bot, update, item_id, r_id, u_name)

    async def startTrack(self, bot, update, item_id, r_id, u_name, album_meta=None, a_raw_meta=None, album=False):
        metadata, raw_meta, err = await get_metadata(item_id)
        if err:
            return await bot.send_message(
                chat_id=update.chat.id,
                text=err,
                reply_to_message_id=r_id
            )
        ext, quality = await check_quality(raw_meta)
        f_album_thumb = False
        if not album:
            type = 'track'
        else:
            type ='album'
        path = Config.DOWNLOAD_BASE_DIR + f"/qobuz/{r_id}/{metadata['title']}.{ext}"
        metadata['extension'] = ext
        await download_track(bot, update, item_id, r_id, u_name, metadata, path, album_meta, f_album_thumb, type)

    async def startAlbum(self, item_id, r_id, u_name, bot=None, update=None):
        metadata, raw_meta, err = await get_metadata(item_id, 'album')
        if err:
            return await bot.send_message(
                chat_id=update.chat.id,
                text=err,
                reply_to_message_id=r_id
            )

        ext, quality = await check_quality(raw_meta, 'album')
        await post_cover(metadata, bot, update, r_id, u_name, quality)
        tracks = raw_meta['tracks']['items']
        for track in tracks:
            await self.startTrack(bot, update, track['id'], r_id, u_name, metadata, raw_meta, True)
        #await check_quality(parse, 'album')


qobuz = QobuzDL()