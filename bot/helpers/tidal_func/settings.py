#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   settings.py
@Time    :   2020/11/08
@Author  :   Yaronzz
@Version :   3.0
@Contact :   yaronhuang@foxmail.com
@Desc    :
'''
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
    videoFileFormat = R"{VideoNumber} - {ArtistName} - {VideoTitle}{ExplicitFlag}"

    def getDefaultPathFormat(self, type: Type):
        if type == Type.Album:
            return R"{ArtistName}/{Flag} {AlbumTitle} [{AlbumID}] [{AlbumYear}]"
        elif type == Type.Track:
            return R"{TrackNumber} - {ArtistName} - {TrackTitle}{ExplicitFlag}"
        elif type == Type.Video:
            return R"{VideoNumber} - {ArtistName} - {VideoTitle}{ExplicitFlag}"
        return ""

    def getAudioQuality(self, value):
        for item in AudioQuality:
            if item.name == value:
                return item
        return AudioQuality.Normal

    def read(self):
        api_index, _ = set_db.get_variable("TIDAL_API_KEY_INDEX")
        if api_index:
            self.apiKeyIndex = int(api_index)

        self.trackFileFormat = Config.TIDAL_TRACK_FORMAT

        if self.albumFolderFormat is None:
            self.albumFolderFormat = self.getDefaultPathFormat(Type.Album)
        if self.trackFileFormat is None:
            self.trackFileFormat = self.getDefaultPathFormat(Type.Track)
        if self.videoFileFormat is None:
            self.videoFileFormat = self.getDefaultPathFormat(Type.Video)


class TokenSettings(aigpy.model.ModelBase):
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

    def read(self, path):
        self._path_ = path
        txt = aigpy.file.getContent(self._path_)
        if txt == "" or txt is None:
            _, txt = set_db.get_variable("AUTH_TOKEN")
        try:
            if len(txt) > 0:
                data = json.loads(self.__decode__(txt))
                aigpy.model.dictToModel(data, self)
        except TypeError:
            set_db.set_variable("TIDAL_AUTH_DONE", False, False, None)

    def save(self):
        data = aigpy.model.modelToDict(self)
        txt = json.dumps(data)
        set_db.set_variable("AUTH_TOKEN", 0, True, self.__encode__(txt))
        aigpy.file.write(self._path_, self.__encode__(txt), 'wb')
        set_db.set_variable("TIDAL_AUTH_DONE", True, False, None)


# Singleton
TIDAL_SETTINGS = Settings()
TIDAL_TOKEN = TokenSettings()
