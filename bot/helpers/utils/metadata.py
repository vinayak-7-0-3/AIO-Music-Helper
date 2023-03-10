import os
import aigpy

from bot import LOGGER
from mutagen import File
from config import Config
from mutagen.flac import FLAC
from mutagen import flac, mp4
from mutagen.mp3 import EasyMP3
from mutagen.mp4 import MP4
from mutagen.id3 import TALB, TCOP, TDRC, TIT2, TPE1, TRCK, APIC, TCON, TOPE, TSRC, USLT


base_metadata = {
    'title': '',
    'album': '',
    'artist': '',
    'albumartist': '',
    'tracknumber': '',
    'date': '',
    'lyrics': '',
    'isrc': '',
    'totaltracks': '',
    'volume' : '',
    'albumart' : '',
    'thumbnail' : '',
    'extension': '',
    'duration': '',
    'copyright': '',
    'genre': '',
    'provider': '',
    'quality': ''
}

async def set_metadata(audio_path, data):
    ext = data['extension']
    handle = File(audio_path)
    if data['duration'] == '':
        await get_duration(audio_path, data, ext)
    if ext == 'flac':
        await set_flac(data, handle)
    elif ext == 'm4a' or ext == 'mp4':
        await set_m4a(data, handle)
    elif ext == 'mp3':
        await set_mp3(data, handle)

async def set_flac(data, handle):
    if handle.tags is None:
            handle.add_tags()
    handle.tags['title'] = data['title']
    handle.tags['album'] = data['album']
    handle.tags['albumartist'] = data['albumartist']
    handle.tags['artist'] = data['artist']
    handle.tags['copyright'] = data['copyright']
    handle.tags['tracknumber'] = str(data['tracknumber'])
    handle.tags['tracktotal'] = str(data['totaltracks'])
    #handle.tags['discnumber'] = 
    #handle.tags['disctotal'] = 
    handle.tags['genre'] = data['genre']
    handle.tags['date'] = data['date']
    #handle.tags['composer'] = 
    handle.tags['isrc'] = data['isrc']
    handle.tags['lyrics'] = data['lyrics']
    await savePic(handle, data)
    handle.save()
    return True

async def set_m4a(data, handle):
    handle.tags['\xa9nam'] = data['title']
    handle.tags['\xa9alb'] = data['album']
    handle.tags['aART'] = data['albumartist']
    handle.tags['\xa9ART'] = data['artist']
    handle.tags['cprt'] = data['copyright']
    handle.tags['trkn'] = [[int(data['tracknumber']), int(data['totaltracks'])]]
    #handle.tags['disk'] = [[__tryInt__(self.discnumber), __tryInt__(self.totaldisc)]]
    handle.tags['\xa9gen'] = data['genre']
    handle.tags['\xa9day'] = data['date']
    #handle.tags['\xa9wrt'] = __tryList__(self.composer)
    handle.tags['\xa9lyr'] = data['lyrics']
    await savePic(handle, data)
    handle.save()
    return True

async def set_mp3(data, handle):
    if handle.tags is None:
            handle.add_tags()
    handle.tags.add(TIT2(encoding=3, text=data['title']))
    handle.tags.add(TALB(encoding=3, text=data['album']))
    handle.tags.add(TOPE(encoding=3, text=data['albumartist']))
    handle.tags.add(TPE1(encoding=3, text=data['artist']))
    handle.tags.add(TCOP(encoding=3, text=data['copyright']))
    handle.tags.add(TRCK(encoding=3, text=str(data['tracknumber'])))
    # handle.tags.add(TRCK(encoding=3, text=self.discnum))
    handle.tags.add(TCON(encoding=3, text=data['genre']))
    handle.tags.add(TDRC(encoding=3, text=data['date']))
    #handle.tags.add(TCOM(encoding=3, text=self.composer))
    handle.tags.add(TSRC(encoding=3, text=data['isrc']))
    handle.tags.add(USLT(encoding=3, lang=u'eng', desc=u'desc', text=data['lyrics']))
    await savePic(handle, data)
    handle.save()
    return True

async def savePic(handle, metadata):
    album_art = metadata['albumart']
    ext = metadata['extension']

    if not os.path.exists(album_art):
        coverPath = Config.DOWNLOAD_BASE_DIR + f"/{metadata['provider']}/albumart/{metadata['album']}.jpg"
        aigpy.net.downloadFile(album_art, coverPath)
        album_art = coverPath

    try:
        with open(album_art, "rb") as f:
            data = f.read()
    except Exception as e:
        LOGGER.warning(e)
        return

    if ext == 'flac':
        pic = flac.Picture()
        pic.data = data
        pic.mime = u"image/jpeg"
        handle.clear_pictures()
        handle.add_picture(pic)

    if ext == 'mp3':
        handle.tags.add(APIC(encoding=3, data=data))

    if ext == 'mp4' or ext == 'm4a':
        pic = mp4.MP4Cover(data)
        handle.tags['covr'] = [pic]
    
    os.remove(album_art)

async def get_duration(path, data, ext):
    if ext == 'mp3':
        audio = EasyMP3(path)
    elif ext == 'm4a':
        audio = MP4(path)
    elif ext == 'flac':
        audio = FLAC(path)
    data['duration'] = audio.info.length
    


