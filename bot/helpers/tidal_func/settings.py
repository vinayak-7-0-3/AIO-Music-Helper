# From yaronzz/Tidal-Media-Downloader
import json
import aigpy
import base64

from config import Config
from bot.helpers.tidal_func.enums import *
from bot.helpers.database.postgres_impl import set_db


class Settings(aigpy.model.ModelBase):
    checkExist = False
    includeEP = True
    saveCovers = True
    language = 0
    lyricFile = False
    apiKeyIndex = 4
    showProgress = False
    showTrackInfo = True
    saveAlbumInfo = False
    downloadPath = Config.DOWNLOAD_BASE_DIR + "/tidal"
    audioQuality = AudioQuality.Master
    usePlaylistFolder = True
    albumFolderFormat = R"{ArtistName}/{Flag} {AlbumTitle} [{AlbumID}] [{AlbumYear}]"
    trackFileFormat = R"{TrackNumber} - {ArtistName} - {TrackTitle}{ExplicitFlag}"


    def getAudioQuality(self, value):
        for item in AudioQuality:
            if item.name == value:
                return item
        return AudioQuality.Normal

    def read(self):
        api_index, _ = set_db.get_variable("TIDAL_API_KEY_INDEX")
        if api_index:
            self.apiKeyIndex = int(api_index)

        #self.trackFileFormat = Config.TIDAL_TRACK_FORMAT


class TokenSettings(aigpy.model.ModelBase):
    _path_ = "./tidal-dl.token.json"
    userid = None
    countryCode = None
    accessToken = None
    refreshToken = None
    expiresAfter = 0

    def __encode__(self, string):
        sw = bytes(string, 'utf-8')
        st = base64.b64encode(sw)
        return st

    def __decode__(self, string):
        try:
            sr = base64.b64decode(string)
            st = sr.decode()
            return st
        except:
            return string

    def read(self):
        txt = aigpy.file.getContent(self._path_)
        if txt == "" or txt is None:
            _, txt = set_db.get_variable("TIDAL_AUTH_TOKEN")
        try:
            if len(txt) > 0:
                data = json.loads(self.__decode__(txt))
                aigpy.model.dictToModel(data, self)
                set_db.set_variable("TIDAL_AUTH_DONE", True, False, None)
        except TypeError:
            set_db.set_variable("TIDAL_AUTH_DONE", False, False, None)

    def save(self):
        data = aigpy.model.modelToDict(self)
        txt = json.dumps(data)
        set_db.set_variable("TIDAL_AUTH_TOKEN", 0, True, self.__encode__(txt))
        aigpy.file.write(self._path_, self.__encode__(txt), 'wb')
        set_db.set_variable("TIDAL_AUTH_DONE", True, False, None)


# Singleton
TIDAL_SETTINGS = Settings()
TIDAL_TOKEN = TokenSettings()
