from bot.helpers.kkbox.utils import *
from bot.helpers.kkbox.kkapi import kkbox_api

class Kkbox_Helper:
    async def login(self):
        kkbox_api.login()

    async def start(self, link, bot, update, r_id):
        type, id = k_url_parse(link)
        
        if type == 'track':
            await self.getTrack(id, bot, update, r_id)
        elif type == 'playlist':
            pass
        elif type == 'album':
            pass
        elif type == 'artist':
            pass

    async def getTrack(self, id, bot, update, r_id, isbatch=False):
        if isbatch:
            pass
        else:
            data = kkbox_api.get_songs([id])[0]
            album_data = kkbox_api.get_album(data['album_id'])
            await dlTrack(id, data, bot, update, r_id, album_data)

kkbox = Kkbox_Helper()