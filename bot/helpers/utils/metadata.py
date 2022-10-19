# From Orpheusdl - tagging.py
import aigpy

"""
metadata = {
    'title': ,
    'album': ,
    'artist': ,
    'albumartist': ,
    'tracknumber': ,
    'date': ,
    'lyrics': ,
    'isrc': ,
    'totaltracks': ,
    'albumart' :
} 
"""

async def kkbox_metadata(audio_path, ext, data, album_data, album_art=None):
    try:
        artist = data['artist_role']['mainartists'] + data['artist_role']['featuredartists']
        album_artist = data['artist_role']['mainartists'] + data['artist_role']['featuredartists']
    except:
        artist = data['artist_name']
        album_artist = data['artist_name']
    try:
        album = data['album_name']
    except:
        album = None

    totaltracks = 0
    for songs in album_data['songs']:
        totaltracks+=1

    metadata = {
        'title': data['song_name'],
        'album': album,
        'artist': artist,
        'albumartist': album_artist,
        'tracknumber': data['song_idx'],
        'date': album_data['album']['album_date'],
        'lyrics': '',
        'isrc': '',
        'totaltracks': totaltracks,
        'albumart': album_art
    }

    await set_metadata(audio_path, metadata)

async def set_metadata(audio_path, data):
    obj = aigpy.tag.TagTool(audio_path)
    obj.title = data['title']
    obj.album = data['album']
    obj.artist = data['artist']
    obj.tracknumber = data['tracknumber']
    obj.isrc = data['isrc']
    obj.albumartist = data['albumartist']
    obj.date = data['date']
    obj.lyrics = data['lyrics']
    obj.totaltrack = data['totaltracks']
    obj.save(data['albumart'])