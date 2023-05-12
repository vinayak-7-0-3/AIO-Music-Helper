import re
import os
import aigpy

from config import Config
from urllib.parse import urlparse

from bot.logger import LOGGER
from bot.helpers.kkbox.kkapi import kkbox_api
from bot.helpers.utils.common import get_file_name
from bot.helpers.utils.tg_utils import send_message
from bot.helpers.database.postgres_impl import set_db
from bot.helpers.utils.metadata import base_metadata, set_metadata


def k_url_parse(link):
    url = urlparse(link)
    path_match = None
    if url.hostname == 'play.kkbox.com':
        path_match = re.match(r'^\/(track|album|artist|playlist)\/([a-zA-Z0-9-_]{18})', url.path)
    elif url.hostname == 'www.kkbox.com':
        path_match = re.match(r'^\/[a-z]{2}\/[a-z]{2}\/(song|album|artist|playlist)\/([a-zA-Z0-9-_]{18})', url.path)
    else:
        LOGGER.debug(f'Invalid URL: {link}')
        return None, None

    if not path_match:
        LOGGER.debug(f'Invalid URL: {link}')
        return None, None
    
    type = path_match.group(1)
    if type == 'song':
        type = 'track'

    media_id = path_match.group(2)
    return type, media_id

async def getAlbumArt(data, r_id, res='80x80', type='thumb'):
    try:
        url = data['cover_photo_info']['url_template']
    except KeyError:
        url = data['album_photo_info']['url_template']
    except Exception as e:
        await LOGGER.error(e)
        return

    url = url.replace('{format}', "jpg")

    thumb_path = Config.DOWNLOAD_BASE_DIR + f"/kkbox/{r_id}/{type}/{r_id}.jpg"
    if type == 'albumart':
        url = url.replace('fit/{width}x{height}', 'original')
        url = url.replace('cropresize/{width}x{height}', 'original')
    else:  
        url = url.replace('{width}x{height}', res)
    aigpy.net.downloadFile(url, thumb_path)
    return thumb_path

async def getAlbumMeta(data):
    url = data['album']['album_photo_info']['url_template']
    url = url.replace('{format}', "jpg")
    url = url.replace('fit/{width}x{height}', 'original')
    url = url.replace('cropresize/{width}x{height}', 'original')

    metadata = base_metadata.copy()
    metadata['title'] = data['album']['album_name']
    metadata['artist'] = data['album']['artist_name']
    metadata['date'] = data['album']['album_date']
    # TODO Add more details here
    no_tracks = 0
    for song in data['songs']:
        no_tracks+=1
    metadata['totaltracks'] = no_tracks
    return metadata

async def dlTrack(id, metadata, user, type=None):
    format = metadata['quality']
    play_mode = None
    if format == 'mp3_128k_chromecast':
        play_mode = 'chromecast'

    url = None
    urls = kkbox_api.get_ticket(id, play_mode)
    for fmt in urls:
        if fmt['name'] == format:
            url = fmt['url']
            break

    audio_path, _, _ = await get_file_name(user, metadata, type)        

    # MP3 HAS NO DRM
    if format == 'mp3_128k_chromecast':
        aigpy.net.downloadFile(url, audio_path)
    else:
        kkbox_api.kkdrm_dl(url, audio_path)
    await LOGGER.info(f"Successfully downloaded {metadata['title']}")

    await set_metadata(audio_path, metadata)

    await send_message(user, audio_path, 'audio', metadata)

    os.remove(audio_path)

async def get_metadata(track_data, album_data, r_id):
    metadata = base_metadata.copy()

    metadata['title'] = track_data['song_name']
    metadata['album'] = track_data['album_name']
    metadata['tracknumber'] = track_data['song_idx']
    metadata['date'] = album_data['album']['album_date']
    metadata['genre'] = track_data['genre_name']
    metadata['provider'] = 'kkbox'

    artist, albumartist = await get_artist(track_data, album_data)
    metadata['artist'] = artist
    metadata['albumartist'] = albumartist

    tracks = 0
    for track in album_data['songs']:
        tracks+=1
    metadata['totaltracks'] = tracks

    # Track thumbnail 
    force_album_thumb = False
    _data = album_data if force_album_thumb else track_data
    metadata['albumart'] = await getAlbumArt(_data, r_id, '1280x1280', 'albumart')
    metadata['thumbnail'] = await getAlbumArt(_data, r_id)
    metadata['quality'] = await get_quality(track_data)
    metadata['extension'] = await get_extension(metadata['quality'])
    return metadata

async def get_artist(track_data, album_data):
    artists = []
    album_artist = []
    for artist in track_data['artist_role']['mainartists']:
        artists.append(artist)
    try:
        for artist in track_data['artist_role']['featuredartists']:
            artists.append(artist)
    except:
        pass
    for artist in album_data['album']['artist_role']['mainartists']:
        album_artist.append(artist)
    try:
        for artist in album_data['album']['artist_role']['featuredartists']:
            album_artist.append(artist)
    except:
        pass
    return ', '.join([str(name) for name in artists]), ', '.join([str(name) for name in album_artist])

async def get_quality(track_data):
    quality, _ = set_db.get_variable("KKBOX_QUALITY")

    if not quality in track_data['audio_quality']:
        await LOGGER.error(f'KKBOX - Quality - {quality} not available for the track - {track_data["song_name"]}')
        quality = track_data['audio_quality'][-1]

    format = {
        '128k': 'mp3_128k_chromecast',
        '192k': 'mp3_192k_kkdrm1',
        '320k': 'aac_320k_m4a_kkdrm1',
        'hifi': 'flac_16_download_kkdrm',
        'hires': 'flac_24_download_kkdrm',
    }[quality]

    return format

async def get_extension(quality):
    extension = quality.split('_')[0]
    if extension == 'aac':
        extension = 'm4a'
    return extension