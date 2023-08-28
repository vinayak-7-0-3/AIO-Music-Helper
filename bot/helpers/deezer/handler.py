import re
from requests import get
from config import Config
from urllib.parse import urlparse

from bot.logger import LOGGER
from bot.helpers.translations import lang
from bot.helpers.deezer.dzapi import deezerapi
from bot.helpers.utils.tg_utils import send_message
from bot.helpers.database.postgres_impl import set_db
from bot.helpers.utils.metadata import base_metadata, set_metadata
from bot.helpers.utils.common import post_cover, get_file_name, check_music_exist, \
        handle_upload


class DeezerDL:
#=================================
# AUTH
#=================================
    async def login(self, with_arl=False):
        # LOGIN WITH ARL IF GIVEN
        if with_arl:
            arl = Config.DEEZER_ARL
            deezerapi.login_via_arl(arl)
        else:
            arl, _ = deezerapi.login_via_email(Config.DEEZER_EMAIL, Config.DEEZER_PASSWORD)
        await self.check_settings()
        LOGGER.debug('Loaded DEEZER Successfully')

#=================================
# DOWNLOAD
#=================================
    async def start(self, url, user):
        type, id = self.url_parse(url)
        if type == 'track':
            await self.getTrack(id, user)
        if type == 'album':
            await self.getAlbum(id, user)
        if type == 'artist':
            await self.getArtist(id, user)

    async def getTrack(self, track_id, user, type='track'):
        is_user_upped = int(track_id) < 0
        if not is_user_upped:
            track_data = deezerapi.get_track(track_id)['DATA']
            track_data = track_data['FALLBACK'] if 'FALLBACK' in track_data else track_data
            q_tier, is_spatial, msg = await self.check_quality(track_data)
        else:
            # For user-up songs | quality will be mp3 here
            track_data = deezerapi.get_track_data(track_id)
            track_data = track_data['FALLBACK'] if 'FALLBACK' in track_data else track_data
            q_tier = 'MP3_MISC'

        err = await self.check_country(track_data)
        if err:
            await LOGGER.error(err, user)
            await send_message(user, err)
            return
        
        metadata = await self.get_metadata(track_data, q_tier, is_spatial)
        metadata['item_id'] = track_id
        dupe = await check_music_exist(metadata, user, t_source=type)
        if dupe: return

        await self.dlTrack(track_data, q_tier, metadata, user, type, is_spatial)
        
    async def getAlbum(self, album_id, user, type='album'):
        data = deezerapi.get_album(album_id)
        album_data = data['DATA']
        track_data = data['SONGS']['data']
        q_tier, is_spatial, msg = await self.check_quality(track_data, True)
        a_meta = await self.get_metadata(album_data, q_tier, is_spatial, 'album', track_data)
        a_meta['item_id'] = album_id
        dupe = await check_music_exist(a_meta, user, 'album')
        if dupe: return
        await post_cover(a_meta, user)
        for track in track_data:
            await self.getTrack(track['SNG_ID'], user, 'album')

    async def getArtist(self, artist_id, user):
        #artist = deezerapi.get_artist_name(artist_id)
        albums = deezerapi.get_artist_album_ids(artist_id, 0, -1, False)
        for album_id in albums:
            await self.getAlbum(album_id, user, 'artist')

    async def dlTrack(self, t_data, q_tier, metadata, user, type, is_spatial):
        if q_tier in ('MP3_320', 'FLAC'):
            url = deezerapi.get_track_url(t_data['SNG_ID'], t_data['TRACK_TOKEN'], t_data['TRACK_TOKEN_EXPIRE'], q_tier)
        else:
            url = deezerapi.get_legacy_track_url(t_data['MD5_ORIGIN'], q_tier, t_data['SNG_ID'], t_data['MEDIA_VERSION'])

        filepath, _, _ = await get_file_name(user, metadata, type)
        await deezerapi.dl_track(t_data['SNG_ID'], url, filepath)

        # I literally dont how know to deal with spatial audio
        if not is_spatial:
            await set_metadata(filepath, metadata)

        #metadata['thumbnail'] = filepath + f'_thumbnail.jpg'
        await handle_upload(user, filepath, metadata)
        #await send_message(user, filepath, 'audio', metadata)

#=================================
# HELPERS
#=================================
    def url_parse(self, link):
        url = urlparse(link)

        if url.hostname == 'deezer.page.link':
            r = get('https://deezer.page.link' + url.path, allow_redirects=False)
            if r.status_code != 302:
                raise Exception(f'DEEZER : Invalid URL: {link}')
            url = urlparse(r.headers['Location'])

        path_match = re.match(r'^\/(?:[a-z]{2}\/)?(track|album|artist|playlist)\/(\d+)\/?$', url.path)
        if not path_match:
            raise Exception(f'DEEZER : Invalid URL: {link}')

        media_type = path_match.group(1)
        media_id = path_match.group(2)
        return media_type, media_id

    async def parse_quality(self, data, is_spatial, human_readable=False):  
        try:
            if is_spatial:
                quality = "360 Spatial"
                ext = 'm4a'
            elif human_readable:
                if data == 'FLAC':
                    return 'HiFi'
                elif data == 'MP3_320':
                    return 'High'
                elif data == 'MP3_128':
                    return 'Normal'
            else:
                ext = data.split('_')[0].lower()
                quality = data.split('_')[1] + 'k'
        except:
            ext = 'flac'
            quality = 'FLAC'
        return ext, quality

    async def get_metadata(self, data, q_tier, is_spatial, type='track', t_data=None):
        metadata = base_metadata.copy()
        if type == 'track':
            metadata['title'] = data['SNG_TITLE']
            #metadata['album'] = data['ALB_TITLE']
            metadata['artist'] = await self.get_artists_from_meta(data)
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
            metadata['extension'], metadata['quality'] = await self.parse_quality(q_tier, is_spatial)
        elif type == 'album':
            metadata['title'] = data['ALB_TITLE']
            metadata['artist'] = data['ART_NAME']
            metadata['albumartist'] = data['ART_NAME']
            metadata['date'] = data.get('ORIGINAL_RELEASE_DATE') or data['PHYSICAL_RELEASE_DATE']
            try:
                metadata['totaltracks'] = int(t_data[-1]['TRACK_NUMBER'])
            except:
                pass

        metadata['album'] = data['ALB_TITLE']
        metadata['albumart'] = await self.get_image_url(data['ALB_PICTURE'], 'art')
        _, metadata['quality'] = await self.parse_quality(q_tier, is_spatial)
        metadata['provider'] = 'deezer'
        return metadata

    async def get_artists_from_meta(self, data):
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

    async def check_settings(self):
        s_quality, _ = set_db.get_variable("DEEZER_QUALITY")
        spatial, _ = set_db.get_variable("DEEZER_SPATIAL")
        pref_mhm1, _ = set_db.get_variable("DEEZER_MHM1")
        if not s_quality:
            # Setting up while startup
            set_db.set_variable("DEEZER_QUALITY", "MP3_128", False, None)
            set_db.set_variable("DEEZER_SPATIAL", False, False, None)
            set_db.set_variable("DEEZER_MHM1", False, False, None)
            deezerapi.set_quality = 'MP3_128'
        else:
            deezerapi.pref_mhm1 = pref_mhm1
            deezerapi.allow_spatial = spatial
            deezerapi.set_quality = s_quality
            u_qualities = deezerapi.available_formats
            # Check if selected quality in settings available in user account
            if not s_quality in u_qualities:
                LOGGER.debug(f"DEEZER - Quality selected in settings - {s_quality} not available in your account.")
                # Fallback to highest available
                set_db.set_variable("DEEZER_QUALITY", str(u_qualities[-1]), False, None)
                deezerapi.set_quality = u_qualities[-1]
            
        
    # s_format - Selected quality in settings | t_data - Track Info    
    async def check_quality(self, t_data, is_album=False):
        t_data = t_data[0] if is_album else t_data

        msg = None
        is_spatial = False
        s_format = deezerapi.set_quality
        if s_format not in deezerapi.available_formats:
            # Directly raise an error so it will cancel the download completly(even if album/playlist)
            raise Exception(lang.select.ERR_DZ_QUALITY_NOT_AVAIL)
        
        try_spatial = deezerapi.allow_spatial
        pref_mhm1 = deezerapi.pref_mhm1

        premium_formats = ['FLAC', 'MP3_320']
        if s_format in premium_formats and try_spatial:
            formats_360 = ['MHM1_RA3', 'MHM1_RA2', 'MHM1_RA1'] if pref_mhm1 else ['MP4_RA3', 'MP4_RA2', 'MP4_RA1']
            for f in formats_360:
                if deezerapi.check_format(t_data['MD5_ORIGIN'], f, t_data['SNG_ID'], t_data['MEDIA_VERSION']):
                    s_format = f
                    is_spatial = True
                    break
        else:
            # Randomly fallback to any available format if the selected one ain't available
            formats_to_check = ['FLAC', 'MP3_320', 'MP3_128']
            if t_data[f'FILESIZE_{s_format}'] == '0':
                for f in formats_to_check:
                    if t_data[f'FILESIZE_{f}'] != '0':
                        s_format = f
                        msg = lang.select.ERR_DZ_QUALITY_FALLBACK.format(f)
                        break
        return s_format, is_spatial, msg
                
    async def check_country(self, t_data):
        # Check track availability
        countries = t_data['AVAILABLE_COUNTRIES']['STREAM_ADS']
        if not countries:
            return lang.select.ERR_DZ_NOT_AVAILABLE
        elif deezerapi.country not in countries:
            return lang.select.ERR_DZ_COUNTRY_RSTRCT
        else:
            return None
        
    async def set_quality(self, quality):
        if quality == 'HiFi':
            deezerapi.set_quality = 'FLAC'
            set_db.set_variable("DEEZER_QUALITY", "FLAC", False, None)
        elif quality == "High":
            deezerapi.set_quality = 'MP3_320'
            set_db.set_variable("DEEZER_QUALITY", "MP3_320", False, None)
        elif quality == "Normal":
            deezerapi.set_quality = 'MP3_128'
            set_db.set_variable("DEEZER_QUALITY", "MP3_128", False, None)

    async def spatial_deezer(self, info, option=None):
        if info == "get":
            return deezerapi.pref_mhm1, deezerapi.allow_spatial
        else:
            if option == 'mhm1':
                set_db.set_variable("DEEZER_MHM1", True, False, None)
                deezerapi.pref_mhm1 = True
            elif option == 'mha1':
                set_db.set_variable("DEEZER_MHM1", False, False, None)
                deezerapi.pref_mhm1 = False
            elif option == 'enable':
                set_db.set_variable("DEEZER_SPATIAL", True, False, None)
                deezerapi.allow_spatial = True
            elif option == 'disable':
                set_db.set_variable("DEEZER_SPATIAL", False, False, None)
                deezerapi.allow_spatial = False
            return deezerapi.pref_mhm1, deezerapi.allow_spatial


deezerdl = DeezerDL()