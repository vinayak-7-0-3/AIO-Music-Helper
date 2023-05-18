class EN(object):
    

#----------------
#
# BASICS
#
#----------------
    WELCOME_MSG = "Hello {} Sir"
    START_DOWNLOAD = "Starting to download..........."
    ANTI_SPAM_WAIT = "Wait for the current task to complete!"
    TASK_COMPLETED = "Download Finished"    



#----------------
#
# AUTHENTICATIONS
#
#----------------
    CHAT_AUTH_SUCCESS = "Successfully authed {0} <code>{1}</code>"
    ADD_ADMIN_SUCCESS = "Successfully added {} as an admin"
    NO_ID_TO_AUTH = "No ID provided to add!"
    # TIDAL
    TIDAL_NOT_AUTH = "No Tidal Logins Given."
    TIDAL_AUTH_NEXT_STEP = "Go to {0} within the next {1} to complete tidal authentication."
    TIDAL_AUTH_SUCCESS = "Tidal authentication successful.\n\nIt is now valid for {}"
    TIDAL_ALREADY_AUTH = "Your authentication is already done.\nIts is valid for {}"
    TIDAL_API_KEY_CHANGED = "Successfully updated the API Key to {} - {}"
    # KKBOX
    KKBOX_NOT_AUTH = "KKBOX account credentials not given or subcription expired"
    # DEEZER
    DEEZER_NOT_AUTH = "Deezer credentials not provided"
    # QOBUZ
    QOBUZ_NOT_AUTH = "Qobuz credentials not provided"
    # SPOTIFY
    SPOTIFY_NOT_AUTH = "Spotify credentials not provided"



#----------------
#
# MUSIC DETAILS - TELEGRAM
#
#----------------
    USER_MENTION_ALBUM = "❤️ <b>Requested by :</b> {}"
    USER_MENTION_TRACK = "Requested by {}"

    # TIDAL
    TIDAL_ALBUM_DETAILS = """
💽 <b>Title :</b> {0}
👤 <b>Artist :</b> {1}
📅 <b>Release Date :</b> {2}
📀 <b>Number of Tracks :</b> {3}
🕒 <b>Duration :</b> {4}
🔢 <b>Number of Volumes :</b> {5}
"""
    # KKBOX
    KKBOX_ALBUM_DETAILS = """
🎶 <b>Title :</b> {0}
👤 <b>Artist :</b> {1}
📅 <b>Release Date :</b> {2}
📀 <b>Number of Tracks :</b> {3}
"""

    # QOBUZ
    QOBUZ_ALBUM_DETAILS = """
🎶 <b>Title :</b> {0}
👤 <b>Artist :</b> {1}
📅 <b>Release Date :</b> {2}
📀 <b>Number of Tracks :</b> {3}
"""

    
    # DEEZER
    DEEZER_ALBUM_DETAILS = """
🎶 <b>Title :</b> {0}
👤 <b>Artist :</b> {1}
📅 <b>Release Date :</b> {2}
🔢 <b>Total Tracks :</b> {3}
"""


    # SPOTIFY
    SPOTIFY_ALBUM_DETAILS = """
🎶 <b>Title :</b> {0}
👤 <b>Artist :</b> {1}
📅 <b>Release Date :</b> {2}
🔢 <b>Total Tracks :</b> {3}
"""


    QUALITY_ADDON = "💫 <b>Quality :</b> {} \n"

    

    

#----------------
#
# SETTINGS PANEL
#
#----------------
    INIT_SETTINGS_MENU = "<b>Welcome to Bot Settings Menu.</b>\n\nChoose the option to open its settings."
    WARN_REMOVE_AUTH = "<b>Are you sure you want to remove {} auth?</b>"
    RM_AUTH_SUCCESSFULL = "Successfully removed {} auth details."
    QUALITY_SET_PANEL = "<b>Choose the required quality for {0}\n\nCurrent Quality :</b> <code>{1}</code>"
    COMMON_AUTH_PANEL = "<b>Configure {0} Authentication\n\nAuth Status : </b>{1}"
    DZ_SPATIAL_PANEL = "<b>Configure Spatial Audio Settings For Deezer</b>"
    #
    # TIDAL PANEL
    #
    TIDAL_SETTINGS_PANEL = """
<b>Configure Tidal Settings Here</b>

<b><u>CURRENT SETTINGS</u></b>

<b>Quality : </b><code>{0}</code>
<b>API : </b><code>{1}</code>
<b>Auth Status : </b><code>{2}</code>
"""
    TIDAL_SELECT_API_KEY = """
<b><u>API KEY SETTING PANEL</u></b>
Current API Platform : <code>{0}</code>
Available Formats : <code>{1}</code>
API Key Valid : <code>{2}</code>
<b><u>API PLATFORM INFO</u></b>
{3}
<b>RELOGIN NEEDED AFTER CHANGING API PLATFORM</b>
"""
    #
    # KKBOX PANEL
    #
    KKBOX_SETTINGS_PANEL = """
<b>Configure KKBOX Settings Here</b>

<b><u>CURRENT SETTINGS</u></b>

<b>Quality : </b><code>{0}</code>
<b>Auth Status : </b><code>{1}</code>
"""
    #
    # QOBUZ PANEL
    #
    QOBUZ_SETTINGS_PANEL = """
<b>Configure Qobuz Settings Here</b>

<b><u>CURRENT SETTINGS</u></b>

<b>Quality : </b><code>{0}</code>
<b>Auth Status : </b><code>{1}</code>
    """
    #
    # DEEZER PANEL
    #
    DEEZER_SETTINGS_PANEL = """
<b>Configure Deezer Settings Here</b>

<b><u>CURRENT SETTINGS</u></b>

<b>Quality : </b><code>{0}</code>
<b>Auth Status : </b><code>{1}</code>
<b>Auth Method : </b><code>{2}</code>
<b>Get Spatial : </b><code>{3}</code>
    """

    



#----------------
#
# BUTTONS
#
#----------------
    # MAIN MENU
    MAIN_MENU_BUTTON = "MAIN MENU"
    TG_AUTH_BUTTON = "TELEGRAM SETTINGS"
    TIDAL_BUTTON = "TIDAL SETTINGS"
    QOBUZ_BUTTON = "QOBUZ SETTINGS"
    DEEZER_BUTTON = "DEEZER SETTINGS"
    KKBOX_BUTTON = 'KKBOX SETTINGS'
    SOUNDCLOUD_BUTTON = "SOUNDCLOUD SETTINGS"
    CLOSE_BUTTON = "CLOSE"
    API_BUTTON = "API"
    SPATIAL_BUTTON = "Spatial Settings"
    # COMMON BUTTONS
    QUALITY_BUTTON = "QUALITY"
    AUTH_BUTTON = "AUTH"
    REMOVE_AUTH_BUTTON = "REMOVE AUTH"
    ADD_AUTH_BUTTON = "ADD AUTH"
    YES_BUTTON = "YES"
    NO_BUTTON = "NO"
    ENABLE_BUTTON = 'Enable'
    DISABLE_BUTTON = 'Disable'
    # TIDAL QUALITY
    MASTER_QUALITY = "Master - FLAC"
    HIFI_QUALITY = "HiFi"
    HIGH_QUALITY = "High"
    NORMAL_QUALITY = "Normal"
    # QOBUZ_QUALIY
    Q_LOSELESS = "LOSELESS"
    Q_320 = "320K"
    Q_HIRES_7 = "HiRes =< 96"
    Q_HIRES_27 = "HiRes > 96"
    # DEEZER SPATIAL BUTTONS
    DZ_ENABLE_MHM1 = "Use MHM1 Codec"
    DZ_ENABLE_MHA1 = 'Use MHA1 Codec'




#----------------
#
# ERRORS
#
#----------------
    ERR_LINK_RECOGNITION = "Sorry, couldn't recognise the given link."
    # QOBUZ
    ERR_QOBUZ_NOT_STREAMABLE = "This album is not available to download."
    ERR_NO_LINK = "No link provided to download from"
    # DEEZER
    ERR_DZ_QUALITY_NOT_AVAIL = "Selected quality not available in your account."
    ERR_DZ_NOT_AVAILABLE = "Deezer Track not available"
    ERR_DZ_COUNTRY_RSTRCT = "Track not available in your country, try downloading in 128/360RA instead"
    ERR_DZ_QUALITY_FALLBACK = "Selected quality not available for this track. Falling back to {}"
    # TIDAL
    ERR_TD_API_KEY = "Tidal API Key not valid. Please change your API Key."
    # SPOTIFY
    ERR_SPOT_NOT_AVAIL = "Sorry, Track not available"