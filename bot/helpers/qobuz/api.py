from config import Config

class QobuzDL:
    def __init__(self):
        self.quality = 6
        self.embed_art = False
        self.ignore_singles_eps = False
        self.no_m3u_for_playlists = False
        self.quality_fallback = True
        self.folder_format = "{artist} - {album} ({year}) [{bit_depth}B-"
        "{sampling_rate}kHz]"
        self.track_format = Config.QOBUZ_TRACK_FORMAT