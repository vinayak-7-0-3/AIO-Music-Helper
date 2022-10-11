from bot.helpers.translations import lang
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

exit_button = [
    [
        InlineKeyboardButton(text=lang.select.MAIN_MENU_BUTTON, callback_data="main_menu"),
        InlineKeyboardButton(text=lang.select.CLOSE_BUTTON, callback_data="close")
    ]
]


def main_menu_set():
    inline_keyboard = [
        [
            InlineKeyboardButton(
                text=lang.select.TG_AUTH_BUTTON,
                callback_data="tgPanel"
            )
        ],
        [
            InlineKeyboardButton(
                text=lang.select.TIDAL_BUTTON,
                callback_data="tidalPanel"
            )
        ],
        [
            InlineKeyboardButton(
                text=lang.select.QOBUZ_BUTTON,
                callback_data="qobuzPanel"
            )
        ],
        [
            InlineKeyboardButton(
                text=lang.select.DEEZER_BUTTON,
                callback_data="deezerPanel"
            )
        ],
        [
            InlineKeyboardButton(
                text=lang.select.SOUNDCLOUD_BUTTON,
                callback_data="scPanel"
            )
        ],
        [
            InlineKeyboardButton(
                text=lang.select.CLOSE_BUTTON,
                callback_data="close"
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard)


def tidal_menu_set():
    inline_keyboard = [
        [
            InlineKeyboardButton(
                text=lang.select.AUTH_BUTTON,
                callback_data="tidalAUTH"
            ),
            InlineKeyboardButton(
                text=lang.select.QUALITY_BUTTON,
                callback_data="tidalQUALITY"
            )
        ]
    ]
    inline_keyboard = inline_keyboard + exit_button
    return InlineKeyboardMarkup(inline_keyboard)


def tidal_auth_set():
    inline_keyboard = [
        [
            InlineKeyboardButton(
                text=lang.select.ADD_AUTH_BUTTON,
                callback_data="ADA_tidal"
            ),
            InlineKeyboardButton(
                text=lang.select.REMOVE_AUTH_BUTTON,
                callback_data="RMA_tidal_warn"
            )
        ]
    ]
    inline_keyboard = inline_keyboard + exit_button
    return InlineKeyboardMarkup(inline_keyboard)

def confirm_RMA_button():
    inline_keyboard = [
        [
            InlineKeyboardButton(
                text=lang.select.YES_BUTTON,
                callback_data="RMA_tidal_yes"
            ),
            InlineKeyboardButton(
                text=lang.select.REMOVE_AUTH_BUTTON,
                callback_data="RMA_tidal_no"
            )
        ]
    ]
    inline_keyboard = inline_keyboard + exit_button
    return InlineKeyboardMarkup(inline_keyboard)
