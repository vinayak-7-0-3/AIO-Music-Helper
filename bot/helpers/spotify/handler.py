import re
import os
import aigpy
import asyncio

from bot import LOGGER
from config import Config
from pydub import AudioSegment
from librespot.metadata import TrackId, EpisodeId
from librespot.audio.decoders import AudioQuality, VorbisOnlyAudioQuality

from bot.helpers.translations import lang
from bot.helpers.spotify.spotifyapi import spotify
from bot.helpers.database.postgres_impl import set_db
from bot.helpers.utils.metadata import base_metadata, set_metadata

CHUNK_SIZE = 50000
REINTENT_DOWNLOAD = 30
sanitize = ["\\", "/", ":", "*", "?", "'", "<", ">", '"']

class SpotifyDL:
#=================================
# AUTH
#=================================
    async def login(self):
        await spotify.login(Config.SPOTIFY_EMAIL, Config.SPOTIFY_PASS)
        await self.load_settings()
        LOGGER.info("Loaded Spotify Succesfully")
        

#=================================
# DOWNLOAD
#=================================
    async def start(self, link, bot, update, r_id, u_name):
        type_id, link_type = await self.parse_url(link)
        if link_type == 'track':
            await self.getTrack(bot, update, r_id, u_name, type_id)
        elif link_type == 'album':
            await self.getAlbum(type_id, bot, update, r_id, u_name)

    async def getTrack(self, bot, update, r_id, u_name, track_id=None):
        err = None
        quality = spotify.quality
        data, err = await spotify.get_song_info(track_id)
        if err: return
        metadata, scraped_song_id = await self.get_metadata(data)
        if scraped_song_id != track_id:
            track_id = scraped_song_id
        await self.downloadTrack(track_id, metadata, quality, bot, update, r_id, u_name)


    async def getAlbum(self, album_id, bot, update, r_id, u_name):
        album_data = await spotify.get_album_name(album_id)
        metadata, _ = await self.get_metadata(album_data, 'album')
        await self.post_cover(metadata, bot, update, r_id, u_name)
        for track in album_data['tracks']['items']:
            await self.getTrack(bot, update, r_id, u_name, track['id'])
            await asyncio.sleep(5)
        

    async def downloadTrack(self, track_id, metadata, quality, bot, update, r_id, u_name):
        track_id = TrackId.from_base62(track_id)
        file_path = f"{Config.DOWNLOAD_BASE_DIR}/spotify/{r_id}/"
        file_name = file_path + await self.sanitize_data(f"{metadata['artist']} - {metadata['title']}.{metadata['extension']}")
        thumb_path = file_path + f'_thumbnail.jpg'

        aigpy.net.downloadFile(metadata['thumbnail'], thumb_path)

        stream = spotify.session.content_feeder().load(
            track_id, VorbisOnlyAudioQuality(quality), False, None
        )
        
        os.makedirs(file_path, exist_ok=True)
        
        # MAIN DOWNLOADING PART
        total_size = stream.input_stream.size
        downloaded = 0
        fail = 0
        _CHUNK_SIZE = CHUNK_SIZE
        with open(file_name, "wb") as file:
            while downloaded <= total_size:
                data = stream.input_stream.stream().read(_CHUNK_SIZE)
                downloaded += len(data)
                file.write(data)
                if (total_size - downloaded) < _CHUNK_SIZE:
                    _CHUNK_SIZE = total_size - downloaded
                if len(data) == 0:
                    fail += 1
                if fail > REINTENT_DOWNLOAD:
                    break

        if spotify.reencode:
            await self.convert_audio_format(file_name, quality)

        await set_metadata(file_name, metadata)

        await bot.send_audio(
            chat_id=update.chat.id,
            audio=file_name,
            duration=int(metadata['duration']),
            performer=metadata['artist'],
            title=metadata['title'],
            thumb=thumb_path,
            reply_to_message_id=r_id
        )

        
#=================================
# HELPERS
#=================================
    async def get_metadata(self, data, type='track'):
        metadata = base_metadata.copy()
        scraped_song_id = None
        if type == 'track':
            metadata['album'] = data["album"]["name"]
            metadata['artist'] = await self.get_artists_from_meta(data)
            metadata['albumartist'] = await self.get_albumartist_from_meta(data)
            metadata['tracknumber'] = data["track_number"]
            metadata['date'] = data["album"]["release_date"]
            metadata['isrc'] = data["external_ids"]["isrc"]
            metadata['totaltracks'] = data["album"]["total_tracks"]
            metadata['volume'] = data["disc_number"]
            metadata['thumbnail'] = await self.get_albumart(data, 'min')
            metadata['duration'] = int(data["duration_ms"]) / 1000
            scraped_song_id = data["id"]
        elif type == 'album':
            metadata['date'] = data['release_date']
            metadata['upc'] = data['external_ids']['upc']
            metadata['totaltracks'] = data['total_tracks']

        metadata['title'] = data["name"]
        metadata['quality'] = '160'
        metadata['provider'] = 'spotify'
        metadata['extension'] = spotify.music_format
        metadata['artist'] = await self.get_artists_from_meta(data)
        metadata['albumart'] = await self.get_albumart(data, 'max', type)
            
        return metadata, scraped_song_id
    
    async def post_cover(self, metadata, bot, update, r_id, u_name):
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
            photo=metadata['albumart'],
            caption=post_details,
            reply_to_message_id=r_id
        )

    async def get_artists_from_meta(self, data):
        artists = []
        for artist in data['artists']:
            artists.append(artist["name"])
        return ', '.join([str(name) for name in artists])
    
    async def get_albumartist_from_meta(self, data):
        artists = []
        for artist in data["album"]["artists"]:
            artists.append(artist["name"])
        return ', '.join([str(name) for name in artists])
    
    async def get_albumart(self, data, size='max', type='track'):
        if type == 'track':
            data = data["album"]["images"]
        elif type == 'album':
             data = data['images']
        sizes = []
        for item in data:
            sizes.append(item["height"])
        if size == 'max':
            max_size = max(sizes)
            for image in data:
                if int(image["height"]) == max_size:
                    return image["url"]
        elif size == 'min':
            min_size = min(sizes)
            for image in data:
                if int(image["height"]) == min_size:
                    return image["url"]
                
    async def convert_audio_format(self, filename, quality):
        raw_audio = AudioSegment.from_file(
            filename, format="ogg", frame_rate=44100, channels=2, sample_width=2
        )
        if quality == AudioQuality.VERY_HIGH:
            bitrate = "320k"
        else:
            bitrate = "160k"

        raw_audio.export(filename, format=spotify.music_format, bitrate=bitrate)

    # Loads quality details from DB
    async def load_settings(self):
        quality, _ = set_db.get_variable("SPOTIFY_QUALITY")
        reencode, _ = set_db.get_variable("SPOTIFY_REENCODE")
        format, _ = set_db.get_variable("SPOTIFY_FORMAT")

        if quality == "320":
            spotify.quality = AudioQuality.VERY_HIGH
        elif quality == "160":
            spotify.quality = AudioQuality.HIGH
        else:
            # Adds default data to DB cuz nothing there
            set_db.set_variable("SPOTIFY_QUALITY", "160", False, None)
            spotify.quality = AudioQuality.HIGH

        #spotify.reencode = True if reencode else False
        #spotify.music_format = 'mp3' if format == 'mp3' and reencode else 'ogg'
        spotify.token = spotify.session.tokens().get("user-read-email")

    async def sanitize_data(self, value):
        for i in sanitize:
            value = value.replace(i, "")
        return value.replace("|", "-")


    async def parse_url(self, link):
        track_uri_search = re.search(
        r"^spotify:track:(?P<TrackID>[0-9a-zA-Z]{22})$", link
        )
        track_url_search = re.search(
            r"^(https?://)?open\.spotify\.com/track/(?P<TrackID>[0-9a-zA-Z]{22})(\?si=.+?)?$",
            link,
        )

        album_uri_search = re.search(
            r"^spotify:album:(?P<AlbumID>[0-9a-zA-Z]{22})$", link
        )
        album_url_search = re.search(
            r"^(https?://)?open\.spotify\.com/album/(?P<AlbumID>[0-9a-zA-Z]{22})(\?si=.+?)?$",
            link,
        )

        playlist_uri_search = re.search(
            r"^spotify:playlist:(?P<PlaylistID>[0-9a-zA-Z]{22})$", link
        )
        playlist_url_search = re.search(
            r"^(https?://)?open\.spotify\.com/playlist/(?P<PlaylistID>[0-9a-zA-Z]{22})(\?si=.+?)?$",
            link,
        )

        episode_uri_search = re.search(
            r"^spotify:episode:(?P<EpisodeID>[0-9a-zA-Z]{22})$", link
        )
        episode_url_search = re.search(
            r"^(https?://)?open\.spotify\.com/episode/(?P<EpisodeID>[0-9a-zA-Z]{22})(\?si=.+?)?$",
            link,
        )

        show_uri_search = re.search(
            r"^spotify:show:(?P<ShowID>[0-9a-zA-Z]{22})$", link
        )
        show_url_search = re.search(
            r"^(https?://)?open\.spotify\.com/show/(?P<ShowID>[0-9a-zA-Z]{22})(\?si=.+?)?$",
            link,
        )

        artist_uri_search = re.search(
            r"^spotify:artist:(?P<ArtistID>[0-9a-zA-Z]{22})$", link
        )
        artist_url_search = re.search(
            r"^(https?://)?open\.spotify\.com/artist/(?P<ArtistID>[0-9a-zA-Z]{22})(\?si=.+?)?$",
            link,
        )

        if track_uri_search is not None or track_url_search is not None:
            track_id_str = (
                track_uri_search if track_uri_search is not None else track_url_search
            ).group("TrackID")
            link_type = 'track'
            return track_id_str, link_type

        if album_uri_search is not None or album_url_search is not None:
            album_id_str = (
                album_uri_search if album_uri_search is not None else album_url_search
            ).group("AlbumID")
            link_type = 'album'
            return album_id_str, link_type

        if playlist_uri_search is not None or playlist_url_search is not None:
            playlist_id_str = (
                playlist_uri_search
                if playlist_uri_search is not None
                else playlist_url_search
            ).group("PlaylistID")
            link_type = 'playlist'
            return playlist_id_str, link_type

        if episode_uri_search is not None or episode_url_search is not None:
            episode_id_str = (
                episode_uri_search if episode_uri_search is not None else episode_url_search
            ).group("EpisodeID")
            link_type = 'episode'
            return episode_id_str, link_type

        if show_uri_search is not None or show_url_search is not None:
            show_id_str = (
                show_uri_search if show_uri_search is not None else show_url_search
            ).group("ShowID")
            link_type = 'show'
            return show_id_str, link_type

        if artist_uri_search is not None or artist_url_search is not None:
            artist_id_str = (
                artist_uri_search if artist_uri_search is not None else artist_url_search
            ).group("ArtistID")
            link_type = 'artist'
            return artist_id_str, link_type
        
        return None, None


        

spotify_dl = SpotifyDL()