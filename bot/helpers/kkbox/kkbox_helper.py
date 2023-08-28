from bot.helpers.kkbox.utils import *
from bot.helpers.kkbox.kkapi import kkbox_api
from bot.helpers.utils.common import post_cover

class Kkbox_Helper:
    async def login(self):
        kkbox_api.login()

    async def start(self, link, user):
        type, id = k_url_parse(link)
        
        if type == 'track':
            await self.getTrack(id, user)
        elif type == 'playlist':
            pass
        elif type == 'album':
            await self.getAlbum(id, user)
        elif type == 'artist':
            pass

    async def getTrack(self, id, user):
        track_data = kkbox_api.get_songs([id])[0]
        album_data = kkbox_api.get_album(track_data['album_id'])
        metadata = await get_metadata(track_data, album_data, user['r_id'])
        await dlTrack(id, metadata, user, 'track')

    async def getAlbum(self, id, user):
        album_data = kkbox_api.get_album(id)
        clean_data = await getAlbumMeta(album_data)
        await post_cover(clean_data, user)
        for track in album_data['songs']:
            track_data = kkbox_api.get_songs([track['encrypted_song_id']])[0]
            metadata = await get_metadata(track_data, album_data, user['r_id'])
            await dlTrack(track['encrypted_song_id'], metadata, user, 'album')

kkbox = Kkbox_Helper()