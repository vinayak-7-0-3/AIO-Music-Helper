from time import time
from math import ceil
from config import Config
from random import randint
from Cryptodome.Hash import MD5
from requests.models import HTTPError
from Cryptodome.Cipher import Blowfish, AES

from bot import LOGGER
from bot.helpers.database.postgres_impl import set_db
from bot.helpers.utils.common import create_requests_session

class APIError(Exception):
    def __init__(self, type, msg, payload):
        self.type = type
        self.msg = msg
        self.payload = payload
    def __str__(self):
        return ', '.join((self.type, self.msg, str(self.payload)))

class DeezerAPI:
    def __init__(self):
        self.gw_light_url = 'https://www.deezer.com/ajax/gw-light.php'
        self.api_token = ''
        self.client_id = '447462'
        self.client_secret = 'a83bf7f38ad2f137e444727cfc3775cf'
        if Config.DEEZER_TRACK_URL_KEY != "":
            self.legacy_url_cipher = AES.new(Config.DEEZER_TRACK_URL_KEY.encode('ascii'), AES.MODE_ECB)
        self.bf_secret = Config.DEEZER_BF_SECRET.encode('ascii')
        
        self.set_quality = None
        self.allow_spatial = False
        self.pref_mhm1 = False

        self.s = create_requests_session()
        self.s.headers.update({
            'accept': '*/*',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
            'content-type': 'text/plain;charset=UTF-8',
            'origin': 'https://www.deezer.com',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'same-origin',
            'sec-fetch-dest': 'empty',
            'referer': 'https://www.deezer.com/',
            'accept-language': 'en-US,en;q=0.9',
        })

    def _api_call(self, method, payload={}):
        api_token = self.api_token if method not in ('deezer.getUserData', 'user.getArl') else ''
        params = {
            'method': method,
            'input': 3,
            'api_version': 1.0,
            'api_token': api_token,
            'cid': randint(0, 1e9),
        }

        resp = self.s.post(self.gw_light_url, params=params, json=payload).json()

        if resp['error']:
            type = list(resp['error'].keys())[0]
            msg = list(resp['error'].values())[0]
            if type=='VALID_TOKEN_REQUIRED':
                try:
                    self._api_call('deezer.getUserData')
                    return self._api_call(method, payload)
                except:
                    pass
            raise APIError(type, msg, resp['payload'])


        if method == 'deezer.getUserData':
            self.api_token = resp['results']['checkForm']
            self.country = resp['results']['COUNTRY']
            self.license_token = resp['results']['USER']['OPTIONS']['license_token']
            self.renew_timestamp = ceil(time())
            self.language = resp['results']['USER']['SETTING']['global']['language']
            
            self.available_formats = ['MP3_128']
            format_dict = {'web_hq': 'MP3_320', 'web_lossless': 'FLAC'}
            for k, v in format_dict.items():
                if resp['results']['USER']['OPTIONS'][k]:
                    self.available_formats.append(v)

        return resp['results']

    def login_via_email(self, email: str, password: str):
        password = MD5.new(password.encode()).hexdigest()

        params = {
            'app_id': self.client_id,
            'login': email,
            'password': password,
            'hash': MD5.new((str(self.client_id) + email + password + self.client_secret).encode()).hexdigest(),
        }

        json = self.s.get('https://connect.deezer.com/oauth/user_auth.php', params=params).json()

        if 'error' in json:
            LOGGER.warning('Error while getting access token, check your credentials')

        headers = {'Authorization': f'Bearer {json["access_token"]}'}

        # server sends set-cookie header with account sid
        self.s.get('https://api.deezer.com/platform/generic/track/80085', headers=headers)

        arl = self._api_call('user.getArl')

        return arl, self.login_via_arl(arl)

    def login_via_arl(self, arl):
        self.s.cookies.set('arl', arl, domain='.deezer.com')
        user_data = self._api_call('deezer.getUserData')

        if not user_data['USER']['USER_ID']:
            self.s.cookies.clear()
            LOGGER.warning('Invalid arl')

        set_db.set_variable("DEEZER_AUTH", True, False, None)
        return user_data

    def get_track(self, id):
        return self._api_call('deezer.pageTrack', {'sng_id': id})

    def get_track_data(self, id):
        return self._api_call('song.getData', {'sng_id': id})

    def get_track_lyrics(self, id):
        return self._api_call('song.getLyrics', {'sng_id': id})

    def get_track_contributors(self, id):
        return self._api_call('song.getData', {'sng_id': id, 'array_default': ['SNG_CONTRIBUTORS']})['SNG_CONTRIBUTORS']

    def get_track_cover(self, id):
        return self._api_call('song.getData', {'sng_id': id, 'array_default': ['ALB_PICTURE']})['ALB_PICTURE']

    def get_track_url(self, id, track_token, track_token_expiry, format):
        # renews license token
        if time() - self.renew_timestamp >= 3600:
            self._api_call('deezer.getUserData')

        # renews track token
        if time() - track_token_expiry >= 0:
            track_token = self._api_call('song.getData', {'sng_id': id, 'array_default': ['TRACK_TOKEN']})['TRACK_TOKEN']

        json = {
            'license_token': self.license_token,
            'media': [
                {
                    'type': 'FULL',
                    'formats': [{'cipher': 'BF_CBC_STRIPE', 'format': format}]
                }
            ],
            'track_tokens': [track_token]
        }
        resp = self.s.post('https://media.deezer.com/v1/get_url', json=json).json()
        return resp['data'][0]['media'][0]['sources'][0]['url']

    def get_legacy_track_url(self, md5_origin, format, id, media_version):
        format_num = {
            'MP3_MISC': '0',
            'MP3_128': '1',
            'MP4_RA1': '13',
            'MP4_RA2': '14',
            'MP4_RA3': '15',
            'MHM1_RA1': '16',
            'MHM1_RA2': '17',
            'MHM1_RA3': '18'
        }[format]

        # mashing a bunch of metadata and hashing it with MD5
        info = b"\xa4".join([i.encode() for i in [
            md5_origin, format_num, str(id), str(media_version)
        ]])
        hash = MD5.new(info).hexdigest()

        # hash + metadata
        hash_metadata = hash.encode() + b"\xa4" + info + b"\xa4"

        # padding
        while len(hash_metadata) % 16 > 0:
            hash_metadata += b"\0"

        # AES encryption
        result = self.legacy_url_cipher.encrypt(hash_metadata).hex()

        # getting url
        return f"https://cdns-proxy-{md5_origin[0]}.dzcdn.net/mobile/1/{result}"
    
    def _get_blowfish_key(self, track_id):
        # yeah, you use the bytes of the hex digest of the hash. bruh moment
        md5_id = MD5.new(str(track_id).encode()).hexdigest().encode('ascii')

        key = bytes([md5_id[i] ^ md5_id[i + 16] ^ self.bf_secret[i] for i in range(16)])

        return key

    def get_album(self, id):
        try:
            return self._api_call('deezer.pageAlbum', {'alb_id': id, 'lang': self.language})
        except APIError as e:
            if e.payload:
                return self._api_call('deezer.pageAlbum', {'alb_id': e.payload['FALLBACK']['ALB_ID'], 'lang': self.language})
            else:
                raise e
            
    def get_artist_name(self, id):
        return self._api_call('artist.getData', {'art_id': id, 'array_default': ['ART_NAME']})['ART_NAME']

    def get_artist_album_ids(self, id, start, nb, credited_albums):
        payload = {
            'art_id': id,
            'start': start,
            'nb': nb,
            'filter_role_id': [0,5] if credited_albums else [0],
            'nb_songs': 0,
            'discography_mode': 'all' if credited_albums else None,
            'array_default': ['ALB_ID']
        }
        resp = self._api_call('album.getDiscography', payload)
        return [a['ALB_ID'] for a in resp['data']]

    async def dl_track(self, id, url, path):
        bf_key = self._get_blowfish_key(id)
        req = self.s.get(url, stream=True)
        req.raise_for_status()

        with open(path, "ab") as file:
            for i, chunk in enumerate(req.iter_content(2048)):
                # every 3rd chunk is encrypted
                if i % 3 == 0 and len(chunk) == 2048:
                    # yes, the cipher has to be reset on every chunk.
                    # those deezer devs were prob smoking crack when they made this DRM
                    cipher = Blowfish.new(bf_key, Blowfish.MODE_CBC, b"\x00\x01\x02\x03\x04\x05\x06\x07")
                    chunk = cipher.decrypt(chunk)
                file.write(chunk)

    def check_format(self, md5_origin, format, id, media_version):
        url = self.get_legacy_track_url(md5_origin, format, id, media_version)
        try:
            resp = self.s.get(url, stream=True)
            resp.raise_for_status()
        except HTTPError:
            return False
        else:
            return True


deezerapi = DeezerAPI()