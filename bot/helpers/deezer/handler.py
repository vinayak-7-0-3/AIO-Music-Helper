import re
import os
import aigpy
from requests import get
from config import Config
from urllib.parse import urlparse
from pathvalidate import sanitize_filename

from bot import LOGGER
from bot.helpers.translations import lang
from bot.helpers.deezer.dzapi import deezerapi
from bot.helpers.database.postgres_impl import set_db
from bot.helpers.utils.metadata import base_metadata, set_metadata

class DeezerDL:
#=================================
# AUTH
#=================================
    async def login(self, with_arl=False):
        # LOGIN WITH ARL IF GIVEN
        """if with_arl:
            arl = Config.DEEZER_ARL
            LOGGER.info('Trying to login to Deezer with ARL given')
        else:
            # CHECK FOR SAVED ARL WITH USER CREDS
            arl, _ = set_db.get_variable("DEEZER_ARL")
            LOGGER.info('Found a saved Deezer ARL. Trying to login')"""
        if with_arl:
            arl = Config.DEEZER_ARL
            deezerapi.login_via_arl(arl)
        else:
            arl, _ = deezerapi.login_via_email(Config.DEEZER_EMAIL, Config.DEEZER_PASSWORD)
            #set_db.set_variable("DEEZER_ARL", arl, False, None)
        LOGGER.info('Loaded DEEZER Successfully')

#=================================
# DOWNLOAD
#=================================
    async def start(self, url, bot, update, r_id, u_name):
        type, id = self.url_parse(url)
        if type == 'track':
            await self.getTrack(id, bot, update, r_id, u_name)
        if type == 'album':
            await self.getAlbum(id, bot, update, r_id, u_name) 

    async def getTrack(self, track_id, bot, update, r_id, u_name, isalbum=False):
        is_user_upped = int(track_id) < 0

        if not is_user_upped:
            track_data = deezerapi.get_track(track_id)
            track_data = track_data['DATA']
            if 'FALLBACK' in track_data:
                track_data = track_data['FALLBACK']
            q_tier = 'MP3_128'
        else:
            track_data = deezerapi.get_track_data(track_id)
            if 'FALLBACK' in track_data:
                track_data = track_data['FALLBACK']
            q_tier = 'MP3_MISC'

        if q_tier not in deezerapi.available_formats:
            raise Exception("Selected Deezer Quality not available on you account")

        metadata = await self.get_metadata(track_data, q_tier)
        await self.dlTrack(track_data, q_tier, metadata, bot, update, r_id, u_name, isalbum)
        #await self.post_details(metadata, bot, update, r_id, u_name)
        
    async def getAlbum(self, album_id, bot, update, r_id, u_name):
        data = deezerapi.get_album(album_id)
        album_data = data['DATA']
        track_data = data['SONGS']['data']
        q_tier = 'FLAC'
        a_meta = await self.get_metadata(album_data, q_tier, 'album', track_data)
        
        await self.post_details(a_meta, bot, update, r_id, u_name)
        
        for track in track_data:
            await self.getTrack(track['SNG_ID'], bot, update, r_id, u_name, True)
        

    async def dlTrack(self, t_data, q_tier, metadata, bot, update, r_id, u_name, isalbum):
        if q_tier in ('MP3_320', 'FLAC'):
            url = deezerapi.get_track_url(t_data['SNG_ID'], t_data['TRACK_TOKEN'], t_data['TRACK_TOKEN_EXPIRE'], q_tier)
        else:
            url = deezerapi.get_legacy_track_url(t_data['MD5_ORIGIN'], q_tier, t_data['SNG_ID'], t_data['MEDIA_VERSION'])

        filename = f"{metadata['title']} - {metadata['artist']}.{metadata['extension']}"
        filename = sanitize_filename(filename)
        temp_path = f"{Config.DOWNLOAD_BASE_DIR}/deezer/{r_id}/"
        if not os.path.isdir(temp_path):
            os.makedirs(temp_path)
        filepath = temp_path + f"{filename}"

        await deezerapi.dl_track(t_data['SNG_ID'], url, filepath)

        await set_metadata(filepath, metadata)

        if not isalbum and Config.MENTION_USERS == "True":
            text = lang.select.USER_MENTION_TRACK.format(u_name)
        else:
            text = None

        thumb_path = filepath + f'_thumbnail.jpg'
        aigpy.net.downloadFile(metadata['thumbnail'], thumb_path)

        await bot.send_audio(
            chat_id=update.chat.id,
            audio=filepath,
            caption=text,
            duration=int(metadata['duration']),
            performer=metadata['artist'],
            title=metadata['title'],
            thumb=thumb_path,
            reply_to_message_id=r_id
        )

#=================================
# HELPERS
#=================================
    def url_parse(self, link):
        url = urlparse(link)

        if url.hostname == 'deezer.page.link':
            r = get('https://deezer.page.link' + url.path, allow_redirects=False)
            if r.status_code != 302:
                LOGGER.warning(f'Invalid URL: {link}')
            url = urlparse(r.headers['Location'])

        path_match = re.match(r'^\/(?:[a-z]{2}\/)?(track|album|artist|playlist)\/(\d+)\/?$', url.path)
        if not path_match:
            LOGGER.warning(f'Invalid URL: {link}')

        media_type = path_match.group(1)
        media_id = path_match.group(2)
        return media_type, media_id

    async def parse_quality(self, data):
        try:
            ext = data.split('_')[0].lower()
            quality = data.split('_')[1] + 'k'
        except:
            ext = 'flac'
            quality = 'FLAC'
        return ext, quality

    async def get_metadata(self, data, q_tier, type='track', t_data=None):
        metadata = base_metadata.copy()
        if type == 'track':
            metadata = base_metadata.copy()
            metadata['title'] = data['SNG_TITLE']
            metadata['album'] = data['ALB_TITLE']
            metadata['artist'] = await self.get_artists(data)
            metadata['albumartist'] = data['ART_NAME']
            metadata['tracknumber'] = data.get('TRACK_NUMBER')
            metadata['volume'] = data.get('DISK_NUMBER')
            metadata['date'] = data.get('PHYSICAL_RELEASE_DATE')
            metadata['isrc'] = data['ISRC']
            metadata['albumart'] = await self.get_image_url(data['ALB_PICTURE'], 'art')
            metadata['thumbnail'] = await self.get_image_url(data['ALB_PICTURE'], 'thumb')
            metadata['duration'] = int(data['DURATION'])
            metadata['copyright'] = data.get('COPYRIGHT')
            metadata['provider'] = 'deezer'
            metadata['extension'], metadata['quality'] = await self.parse_quality(q_tier)
        elif type == 'album':
            metadata['title'] = data['ALB_TITLE']
            metadata['artist'] = data['ART_NAME']
            metadata['date'] = data.get('ORIGINAL_RELEASE_DATE') or data['PHYSICAL_RELEASE_DATE']
            try:
                metadata['totaltracks'] = int(t_data[-1]['TRACK_NUMBER'])
            except:
                pass
            metadata['albumart'] = await self.get_image_url(data['ALB_PICTURE'], 'art')
            _, metadata['quality'] = await self.parse_quality(q_tier)
            metadata['provider'] = 'deezer'
        return metadata

    async def get_artists(self, data):
        artists = []
        for artist in data['ARTISTS']:
            artists.append(artist['ART_NAME'])
        return ', '.join([str(name) for name in artists])

    async def get_image_url(self, md5, img_type):
        #res = 3000
        if img_type == 'art':
            res = 3000
        elif img_type == 'thumb':
            res = 80

        filename = f'{res}x0-000000-100-0-0.jpg'

        return f'https://cdns-images.dzcdn.net/images/cover/{md5}/{filename}'
        
    async def post_details(self, metadata, bot, update, r_id, u_name):
        url = metadata['albumart']

        post_details = lang.select.DEEZER_ALBUM_DETAILS.format(
            metadata['title'],
            metadata['artist'],
            metadata['date'],
            metadata['totaltracks']
        )
        quality = metadata['quality']
        if quality != '':
            post_details = post_details + lang.select.QUALITY_ADDON.format(quality)
        if Config.MENTION_USERS == "True":
            post_details = post_details + lang.select.USER_MENTION_ALBUM.format(u_name)

        await bot.send_photo(
            chat_id=update.chat.id,
            photo=url,
            caption=post_details,
            reply_to_message_id=r_id
        )

    """async def check_quality(self, t_data):
        q_tier = 'FLAC'
        premium_formats = ['FLAC', 'MP3_320']
        countries = t_data['AVAILABLE_COUNTRIES']['STREAM_ADS']
        if not countries:
            raise Exception('Track not available')
        elif q_tier in premium_formats:
            spatial, _ = set_db.get_variable("DEEZER_360")
            prefer_mhm1 = False

            formats_360 = ['MP4_RA3', 'MP4_RA2', 'MP4_RA1'] if not prefer_mhm1 else ['MHM1_RA3', 'MHM1_RA2', 'MHM1_RA1']

            if q_tier =='FLAC' and spatial == 'True':
                for f in formats_360:
                    if deezerapi.check_format(t_data['MD5_ORIGIN'], f, t_data['SNG_ID'], t_data['MEDIA_VERSION']):
                        q_tier = f
                        break

            if q_tier not in formats_360:
                formats_to_check = premium_formats
                while len(formats_to_check) != 0:
                    if formats_to_check[0] != q_tier:
                        formats_to_check.pop(0)
                    else:
                        break
                
                temp_f = None
                for f in formats_to_check:
                    if t_data[f'FILESIZE_{f}'] != '0':
                        temp_f = f
                        break
                if temp_f is None:
                    temp_f = 'MP3_128'
                q_tier = temp_f

                if deezerapi.country not in countries:
                    raise Exception('Track not available in your country, try downloading in 128/360RA instead')
                elif format not in deezerapi.available_formats:
                    raise Exception('Format not available by your subscription')

                print(q_tier)
                return q_tier"""
                    


deezerdl = DeezerDL()