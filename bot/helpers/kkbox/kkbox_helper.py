from bot.helpers.kkbox.utils import *
from bot.helpers.kkbox.kkapi import kkbox_api
from bot.helpers.database.postgres_impl import set_db

class Kkbox_Helper:
    async def login(self):
        kkbox_api.login()

    async def start(self, link, bot, update, r_id, u_name):
        type, id = k_url_parse(link)
        
        if type == 'track':
            await self.getTrack(id, bot, update, r_id, u_name)
        elif type == 'playlist':
            pass
        elif type == 'album':
            await self.getAlbum(id, bot, update, r_id, u_name)
        elif type == 'artist':
            pass

    async def getTrack(self, id, bot, update, r_id, u_name):
        track_data = kkbox_api.get_songs([id])[0]
        album_data = kkbox_api.get_album(track_data['album_id'])
        metadata = await get_metadata(track_data, album_data, r_id)
        await dlTrack(id, metadata, bot, update, r_id,  u_name, 'track')

    async def getAlbum(self, id, bot, update, r_id, u_name):
        post = True
        album_data = kkbox_api.get_album(id)
        if post:
            await postAlbumData(album_data, r_id, bot, update, u_name)
        for track in album_data['songs']:
            track_data = kkbox_api.get_songs([track['encrypted_song_id']])[0]
            metadata = await get_metadata(track_data, album_data, r_id)
            await dlTrack(track['encrypted_song_id'], metadata, bot, update, r_id,  u_name, 'album')

kkbox = Kkbox_Helper()