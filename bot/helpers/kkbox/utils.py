import re
import os
import aigpy

from bot import LOGGER
from config import Config
from urllib.parse import urlparse

from bot.helpers.translations import lang
from bot.helpers.kkbox.kkapi import kkbox_api
from bot.helpers.utils.metadata import kkbox_metadata


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

    thumb_path = Config.DOWNLOAD_BASE_DIR + f"/{type}/{r_id}.jpg"
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

async def dlTrack(id, data, bot, update, r_id, album, u_name=None, type=None):
    quality = "192k"

    if quality in data['audio_quality']:
        format = {
            '128k': 'mp3_128k_chromecast',
            '192k': 'mp3_192k_kkdrm1',
            '320k': 'aac_320k_m4a_kkdrm1',
            'hifi': 'flac_16_download_kkdrm',
            'hires': 'flac_24_download_kkdrm',
        }[quality]

        play_mode = None
        if format == 'mp3_128k_chromecast':
            play_mode = 'chromecast'

        url = None
        urls = kkbox_api.get_ticket(id, play_mode)
        ext = format.split('_')[0]
        for fmt in urls:
            if fmt['name'] == format:
                url = fmt['url']
                break

        temp_path = Config.DOWNLOAD_BASE_DIR + f"/KKBOX/{r_id}/"
        if not os.path.isdir(temp_path):
            os.makedirs(temp_path)
        file_name = f"{data['song_name']}.{ext}"
        audio_path = temp_path + file_name

        # MP3 HAS NO DRM
        if format == 'mp3_128k_chromecast':
            aigpy.net.downloadFile(url, audio_path)
        else:
            kkbox_api.kkdrm_dl(url, audio_path)
        LOGGER.info(f"Successfully downloaded {data['song_name']}")

        thumb_path = await getAlbumArt(data, r_id)
        album_art = await getAlbumArt(data, r_id, '1280x1280', 'albumart')
        
        await kkbox_metadata(audio_path, ext, data, album, album_art)

        if type == 'track' and Config.MENTION_USERS == "True":
            text = lang.select.USER_MENTION_TRACK.format(u_name)
        else:
            text = None

        await bot.send_audio(
            chat_id=update.chat.id,
            audio=audio_path,
            caption=text,
            performer=data['artist_name'],
            title=data['song_name'],
            thumb=thumb_path,
            reply_to_message_id=r_id
        )

        os.remove(thumb_path)
        os.remove(album_art)
        os.remove(audio_path)