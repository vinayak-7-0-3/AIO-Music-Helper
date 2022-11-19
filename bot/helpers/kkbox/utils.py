import re
import os
import aigpy

from bot import LOGGER
from config import Config
from urllib.parse import urlparse
from pathvalidate import sanitize_filename

from bot.helpers.translations import lang
from bot.helpers.kkbox.kkapi import kkbox_api
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
        LOGGER.warning(f'Invalid URL: {link}')
        return None, None

    if not path_match:
        LOGGER.warning(f'Invalid URL: {link}')
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
        LOGGER.warning(e)
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

async def postAlbumData(data, r_id, bot, update, u_name):
    url = data['album']['album_photo_info']['url_template']
    url = url.replace('{format}', "jpg")
    url = url.replace('fit/{width}x{height}', 'original')
    url = url.replace('cropresize/{width}x{height}', 'original')

    no_tracks = 0
    for song in data['songs']:
        no_tracks+=1

    post_details = lang.select.KKBOX_ALBUM_DETAILS.format(
            data['album']['album_name'],
            data['album']['artist_name'],
            data['album']['album_date'],
            no_tracks
    )

    if Config.MENTION_USERS == "True":
            post_details = post_details + lang.select.USER_MENTION_ALBUM.format(u_name)
    
    await bot.send_photo(
        chat_id=update.chat.id,
        photo=url,
        caption=post_details,
        reply_to_message_id=r_id
    )

async def dlTrack(id, metadata, bot, update, r_id, u_name=None, type=None):
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

    temp_path = Config.DOWNLOAD_BASE_DIR + f"/kkbox/{r_id}/"
    if not os.path.isdir(temp_path):
        os.makedirs(temp_path)

    file_name = f"{metadata['title']}.{metadata['extension']}"
    file_name = sanitize_filename(file_name)

    audio_path = temp_path + file_name

    # MP3 HAS NO DRM
    if format == 'mp3_128k_chromecast':
        aigpy.net.downloadFile(url, audio_path)
    else:
        kkbox_api.kkdrm_dl(url, audio_path)
    LOGGER.info(f"Successfully downloaded {metadata['title']}")

    await set_metadata(audio_path, metadata)

    if type == 'track' and Config.MENTION_USERS == "True":
        text = lang.select.USER_MENTION_TRACK.format(u_name)
    else:
        text = None

    await bot.send_audio(
        chat_id=update.chat.id,
        audio=audio_path,
        caption=text,
        duration=int(metadata['duration']),
        performer=metadata['artist'],
        title=metadata['title'],
        thumb=metadata['thumbnail'],
        reply_to_message_id=r_id
    )

    os.remove(metadata['thumbnail'])
    os.remove(audio_path)
    #os.rmdir(temp_path)

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
        LOGGER.info(f'Quality - {quality} not available for the track - {track_data["song_name"]}')
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