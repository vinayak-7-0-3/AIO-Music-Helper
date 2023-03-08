import json

from bot import LOGGER
from config import Config
from random import randrange
from time import time, sleep
from Cryptodome.Hash import MD5
from Cryptodome.Cipher import ARC4

from bot.helpers.database.postgres_impl import set_db
from bot.helpers.utils.common import create_requests_session

class KkboxAPI:
    def __init__(self, kc1_key):
        self.kc1_key = kc1_key.encode('ascii')

        self.s = create_requests_session()
        self.s.headers.update({
            'user-agent': 'okhttp/3.14.9'
        })

        self.kkid = '%032X' % randrange(16**32)

        self.params = {
            'enc': 'u',
            'ver': '06090076',
            'os': 'android',
            'osver': '11',
            'lang': 'en',
            'ui_lang': 'en',
            'dist': '0021',
            'dist2': '0021',
            'resolution': '411x683',
            'of': 'j',
            'oenc': 'kc1',
        }

    def kc1_decrypt(self, data):
        cipher = ARC4.new(self.kc1_key)
        return cipher.decrypt(data).decode('utf-8')

    def api_call(self, host, path, params={}, payload=None):
        if host == 'ticket':
            payload = json.dumps(payload)

        params.update(self.params)
        params.update({'timestamp': int(time())})

        url = f'https://api-{host}.kkbox.com.tw/{path}'
        if not payload:
            r = self.s.get(url, params=params)
        else:
            r = self.s.post(url, params=params, data=payload)

        resp = json.loads(self.kc1_decrypt(r.content)) if r.content else None
        return resp

    def login(self):
        email = Config.KKBOX_EMAIL
        password = Config.KKBOX_PASSWORD
        md5 = MD5.new()
        md5.update(password.encode('utf-8'))
        pswd = md5.hexdigest()

        resp = self.api_call('login', 'login.php', payload={
            'uid': email,
            'passwd': pswd,
            'kkid': self.kkid,
            'registration_id': '',
        })

        if resp['status'] not in (2, 3):
            if resp['status'] == -1:
                LOGGER.warning('Incorrect Email Provided For KKBOX')
                exit(1)
            elif resp['status'] == -2:
                LOGGER.warning('Incorrect Password Provided For KKBOX')
                exit(1)
            elif resp['status'] == -4:
                LOGGER.warning('IP address is in unsupported region for KKBOX, use a VPN')
                set_db.set_variable("KKBOX_AUTH", False, False, None)
                return
            elif resp['status'] == 1:
                LOGGER.warning('KKBOX Account expired')
                set_db.set_variable("KKBOX_AUTH", False, False, None)
                return
            LOGGER.warning('Login failed')

        self.apply_session(resp)
        self.set_quality()
        set_db.set_variable("KKBOX_AUTH", True, False, None)

    def renew_session(self):
        host = 'login' if not self.region_bypass else 'login-utapass'
        resp = self.api_call(host, 'check.php')
        if resp['status'] not in (2, 3, -4):
            raise self.exception('Session renewal failed')
        self.apply_session(resp)
        self.set_quality()

    def apply_session(self, resp):
        self.sid = resp['sid']
        self.params['sid'] = self.sid

        self.lic_content_key = resp['lic_content_key'].encode('ascii')

        self.available_qualities = ['128k', '192k', '320k']
        if resp['high_quality']:
            self.available_qualities.append('hifi')
            self.available_qualities.append('hires')

    def set_quality(self):
        quality, _ = set_db.get_variable("KKBOX_QUALITY")

        if quality:
            if not quality in self.available_qualities:
                LOGGER.info('KKBOX quality chosen in settings is not available in your subcription now.')
                set_db.set_variable("KKBOX_QUALITY", self.available_qualities[-1], False, None)
        else:
            set_db.set_variable("KKBOX_QUALITY", self.available_qualities[-1], False, None)

    def get_songs(self, ids):
        resp = self.api_call('ds', 'v2/song', payload={
            'ids': ','.join(ids),
            'fields': 'artist_role,song_idx,album_photo_info,song_is_explicit,song_more_url,album_more_url,artist_more_url,genre_name,is_lyrics,audio_quality'
        })
        if resp['status']['type'] != 'OK':
            LOGGER.info('Track not found')
            return None
        return resp['data']['songs']

    def get_song_lyrics(self, id):
        return self.api_call('ds', f'v1/song/{id}/lyrics')

    def get_album(self, id):
        resp = self.api_call('ds', f'v1/album/{id}')
        if resp['status']['type'] != 'OK':
            LOGGER.warning('Album not found')
            return
        return resp['data']

    def get_album_more(self, raw_id):
        return self.api_call('ds', 'album_more.php', params={
            'album': raw_id
        })

    def get_artist(self, id):
        resp = self.api_call('ds', f'v3/artist/{id}')
        if resp['status']['type'] != 'OK':
            raise self.exception('Artist not found')
        return resp['data']
    
    def get_artist_albums(self, raw_id, limit, offset):
        resp = self.api_call('ds', f'v2/artist/{raw_id}/album', params={
            'limit': limit,
            'offset': offset,
        })
        if resp['status']['type'] != 'OK':
            raise self.exception('Artist not found')
        return resp['data']['album']

    def get_playlists(self, ids):
        resp = self.api_call('ds', f'v1/playlists', params={
            'playlist_ids': ','.join(ids)
        })
        if resp['status']['type'] != 'OK':
            raise self.exception('Playlist not found')
        return resp['data']['playlists']

    def search(self, query, types, limit):
        return self.api_call('ds', 'search_music.php', params={
            'sf': ','.join(types),
            'limit': limit,
            'query': query,
            'search_ranking': 'sc-A',
        })

    def get_ticket(self, song_id, play_mode = None):
        resp = self.api_call('ticket', 'v1/ticket', payload={
            'sid': self.sid,
            'song_id': song_id,
            'ver': '06090076',
            'os': 'android',
            'osver': '11',
            'kkid': self.kkid,
            'dist': '0021',
            'dist2': '0021',
            'timestamp': int(time()),
            'play_mode': play_mode,
        })

        if resp['status'] != 1:
            if resp['status'] == -1:
                self.renew_session()
                return self.get_ticket(song_id, play_mode)
            elif resp['status'] == -4:
                self.auth_device()
                return self.get_ticket(song_id, play_mode)
            elif resp['status'] == 2:
                # tbh i'm not sure if this is some rate-limiting thing
                # or if it's a bug on their slow-as-hell servers
                sleep(0.5)
                return self.get_ticket(song_id, play_mode)
            LOGGER.warning("Couldn't get track URLs")
            
        return resp['uris']

    def auth_device(self):
        resp = self.api_call('ds', 'active_sid.php', payload={
            'ui_lang': 'en',
            'of': 'j',
            'os': 'android',
            'enc': 'u',
            'sid': self.sid,
            'ver': '06090076',
            'kkid': self.kkid,
            'lang': 'en',
            'oenc': 'kc1',
            'osver': '11',
        })
        if resp['status'] != 1:
            raise self.exception("Couldn't auth device")

    def kkdrm_dl(self, url, path):
        # skip first 1024 bytes of track file
        resp = self.s.get(url, stream=True, headers={'range': 'bytes=1024-'})
        resp.raise_for_status()

        # drop 512 bytes of keystream
        rc4 = ARC4.new(self.lic_content_key, drop=512)

        with open(path, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=4096):
                f.write(rc4.decrypt(chunk))


"""def create_requests_session():
    session_ = requests.Session()
    retries = Retry(total=10, backoff_factor=0.4, status_forcelist=[429, 500, 502, 503, 504])
    session_.mount('http://', HTTPAdapter(max_retries=retries))
    session_.mount('https://', HTTPAdapter(max_retries=retries))
    return session_"""

kkbox_api = KkboxAPI(Config.KKBOX_KEY)