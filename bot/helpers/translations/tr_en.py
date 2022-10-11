class EN(object):
    

#----------------
#
# BASICS
#
#----------------
    WELCOME_MSG = "Hello {} Sir"
    START_DOWNLOAD = "Starting to download..........."



#----------------
#
# AUTHENTICATIONS
#
#----------------
    CHAT_AUTH_SUCCESS = "Successfully authed {} <code>{}</code>"
    ADD_ADMIN_SUCCESS = "Successfully added {} as an admin"
    NO_ID_TO_AUTH = "No ID provided to add!"
    # TIDAL
    TIDAL_NOT_AUTH = "No Tidal Logins Given."
    TIDAL_AUTH_NEXT_STEP = "Go to {} within the next {} to complete tidal authentication."
    TIDAL_AUTH_SUCCESS = "Tidal authentication successful.\n\nIt is now valid for {}"
    TIDAL_ALREADY_AUTH = "Your authentication is already done.\nIts is valid for {}"



#----------------
#
# MUSIC DETAILS - TELEGRAM
#
#----------------
    ALBUM_DETAILS = """
💽 <b>Title :</b> {0}
👤 <b>Artist :</b> {1}
📅 <b>Release Date :</b> {2}
📀 <b>Number of Tracks :</b> {3}
🕒 <b>Duration :</b> {4}
🔢 <b>Number of Volumes :</b> {5}
"""

    USER_MENTION_ALBUM = "❤️ <b>Requested by :</b> {}"
    USER_MENTION_TRACK = "Requested by {}"

    

#----------------
#
# SETTINGS PANEL
#
#----------------
    INIT_SETTINGS_MENU = "<b>Welcome to Bot Settings Menu.</b>\n\nChoose the option to open its settings."
    WARN_REMOVE_AUTH = "<b>Are you sure you want to remove Tidal auth?</b>"
    #
    # TIDAL PANEL
    #
    TIDAL_SETTINGS_PANEL = "<b>Configure Tidal Settings Here</b>"
    TIDAL_AUTH_PANEL = "<b>Configure Tidal Authentication\n\nAuth Status : </b>{}"



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
    SOUNDCLOUD_BUTTON = "SOUNDCLOUD SETTINGS"
    CLOSE_BUTTON = "CLOSE"
    # COMMON BUTTONS
    QUALITY_BUTTON = "QUALITY"
    AUTH_BUTTON = "AUTH"
    REMOVE_AUTH_BUTTON = "REMOVE AUTH"
    ADD_AUTH_BUTTON = "ADD AUTH"
    YES_BUTTON = "YES"
    NO_BUTTON = "NO"