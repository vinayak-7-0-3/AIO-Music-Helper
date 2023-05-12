import os
import ast
import shutil
import requests

from bot import Config
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

from bot.helpers.translations import lang
from bot.helpers.buttons.extra_button import get_music_button
from bot.helpers.database.postgres_impl import music_db
from bot.helpers.utils.tg_utils import send_message, copy_message, \
        fetch_tg_link


def create_requests_session():
    session_ = requests.Session()
    retries = Retry(total=10, backoff_factor=0.4, status_forcelist=[429, 500, 502, 503, 504])
    session_.mount('http://', HTTPAdapter(max_retries=retries))
    session_.mount('https://', HTTPAdapter(max_retries=retries))
    return session_

# FOLDER STRUCTURE = ./BASE_DIR / PROVIDER / REPLY_TO_ID / TRACK_NAME.EXTENTION
async def clean_up(r_id, provider):
    path = Config.DOWNLOAD_BASE_DIR + f"/{provider}/{r_id}"
    try:
        shutil.rmtree(path)
    except OSError as e:
        pass

async def post_cover(data, user):
    if data['albumart'] != '':
        text = await format_string(lang.ALBUM_TEMPLATE, data, user)
        #msg = await send_message(user, data['albumart'], 'pic', text)
        msg = await handle_upload(user, data['albumart'], data, 'album', text)

async def get_file_name(user, meta, type='track'):
    album = None
    playlist = None
    base_path = Config.DOWNLOAD_BASE_DIR + f"/{meta['provider']}/{user['r_id']}/"
    if type=='track':
        file = base_path + (await format_string(Config.TRACK_NAME_FORMAT, meta, user)) + f".{meta['extension']}"
    elif type == 'album':
        album = base_path + (await format_string(Config.ALBUM_NAME_FORMAT, meta, user))
        file = album + '/' + (await format_string(Config.TRACK_NAME_FORMAT, meta, user)) + f".{meta['extension']}"
    elif type == 'playlist' or type == 'mix':
        playlist = base_path + (await format_string(Config.PLAYLIST_NAME_FORMAT, meta, user)) + f".{meta['extension']}"
    if album:
        os.makedirs(album, exist_ok=True)
    elif playlist:
        os.makedirs(playlist, exist_ok=True)
    else:
        os.makedirs(base_path, exist_ok=True)

    return file, album, playlist

async def format_string(text, data, user=None):
    text = text.replace(R'{title}', data['title'])
    text = text.replace(R'{album}', data['album'])
    text = text.replace(R'{artist}', data['artist'])
    text = text.replace(R'{albumartist}', data['albumartist'])
    text = text.replace(R'{tracknumber}', str(data['tracknumber']))
    text = text.replace(R'{date}', str(data['date']))
    text = text.replace(R'{upc}', str(data['upc']))
    text = text.replace(R'{isrc}', str(data['isrc']))
    text = text.replace(R'{totaltracks}', str(data['totaltracks']))
    text = text.replace(R'{volume}', str(data['volume']))
    text = text.replace(R'{totalvolume}', str(data['totalvolume']))
    text = text.replace(R'{extension}', data['extension'])
    text = text.replace(R'{duration}', str(data['duration']))
    text = text.replace(R'{copyright}', data['copyright'])
    text = text.replace(R'{genre}', data['genre'])
    text = text.replace(R'{provider}', data['provider'].title())
    text = text.replace(R'{quality}', data['quality'])
    text = text.replace(R'{explicit}', str(data['explicit']))
    if user:
        text = text.replace(R'{user}', user['name'])
        text = text.replace(R'{username}', user['user_name'])
    return text

async def handle_upload(user, path, meta, type='track', text=None):
    file_type = 'pic' if type=='album' else 'audio'
    extra = text if type=='album' else meta
    if Config.COPY_AUDIO_FILES == 'True':
        track_id = meta['upc'] if type=='album' else meta['isrc']
        msg = await send_message(user, path, file_type, extra)

        if meta['provider'] == 'tidal':
            msg = await copy_message(user['chat_id'], Config.TIDAL_CHAT, msg.id)
        elif meta['provider'] == 'qobuz':
            msg = await copy_message(user['chat_id'], Config.QOBUZ_CHAT, msg.id)
        elif meta['provider'] == 'deezer':
            msg = await copy_message(user['chat_id'], Config.DEEZER_CHAT, msg.id)
        elif meta['provider'] == 'spotify':
            msg = await copy_message(user['chat_id'], Config.SPOTIFY_CHAT, msg.id)
        elif meta['provider'] == 'kkbox':
            msg = await copy_message(user['chat_id'], Config.KKBOX_CHAT, msg.id)
        meta['lyrics'] = None
        music_db.set_music(msg.id, meta, track_id, type)
    else:
        await send_message(user, path, file_type, extra)

# t_source - The track source, wheather it is from album, playlist
async def check_music_exist(meta, user, type='track', t_source='track'):
    if Config.DUPLICATE_CHECK == 'True':

        if t_source=='album':
            # If track download was initiated from an album
            # link then this downloads the track again (for clean chat)
            return False
        
        track_id = meta['upc'] if type=='album' else meta['isrc']

        text, links = await fetch_dupe_music(track_id, user)
        if text:
            await send_message(
                user, 
                text, 
                markup=get_music_button(user['user_id'],links,meta['item_id'])
            )
            return True
    else:
        return False
    
async def fetch_dupe_music(track_id, user):
    text = lang.SONG_COPY_EXIST
    links = [] # TG message links of the file
    tracks = music_db.get_music_id(track_id)
    count = 0
    if tracks:
        for track in tracks:
            msg_id, metadata, dbtrack_id, song_type = track[0], track[1], track[2], track[3]
            metadata = ast.literal_eval(metadata)
            link = await fetch_tg_link(msg_id, user, metadata['provider'])
            links.append(link)
            code = 'UPC' if song_type == 'album' else 'ISRC'
            text = text + '\n' + lang.SONG_COPY_EXIST_INFO.format(
                count,
                metadata['title'],
                metadata['artist'],
                metadata['provider'].title(),
                metadata['quality'],
                code,
                dbtrack_id
            ) + '\n\n'
            count += 1
        return text, links
    else: return None, None