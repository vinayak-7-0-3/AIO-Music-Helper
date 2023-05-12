from bot.helpers.translations import lang
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Some common button addon - Main menu and Close
exit_button = [
    [
        InlineKeyboardButton(text=lang.MAIN_MENU_BUTTON, callback_data="main_menu"),
        InlineKeyboardButton(text=lang.CLOSE_BUTTON, callback_data="close")
    ]
]

def main_menu_set():
    inline_keyboard = [
        [
            InlineKeyboardButton(
                text=lang.TG_AUTH_BUTTON,
                callback_data="tgPanel"
            )
        ],
        [
            InlineKeyboardButton(
                text=lang.TIDAL_BUTTON,
                callback_data="tidalPanel"
            )
        ],
        [
            InlineKeyboardButton(
                text=lang.KKBOX_BUTTON,
                callback_data="kkboxPanel"
            )
        ],
        [
            InlineKeyboardButton(
                text=lang.QOBUZ_BUTTON,
                callback_data="qobuzPanel"
            )
        ],
        [
            InlineKeyboardButton(
                text=lang.DEEZER_BUTTON,
                callback_data="deezerPanel"
            )
        ],
        [
            InlineKeyboardButton(
                text=lang.SOUNDCLOUD_BUTTON,
                callback_data="scPanel"
            )
        ],
        [
            InlineKeyboardButton(
                text=lang.CLOSE_BUTTON,
                callback_data="close"
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard)


def tidal_menu_set():
    inline_keyboard = [
        [
            InlineKeyboardButton(
                text=lang.AUTH_BUTTON,
                callback_data="ADA_tidal_panel"
            )
        ],
        [
            InlineKeyboardButton(
                text=lang.QUALITY_BUTTON,
                callback_data="QA_tidal"
            )
        ],
        [
            InlineKeyboardButton(
                text=lang.API_BUTTON,
                callback_data="apiTidal_panel"
            )
        ]
    ]
    inline_keyboard = inline_keyboard + exit_button
    return InlineKeyboardMarkup(inline_keyboard)

def tidal_api_set(api, platform):
    inline_keyboard = []
    for i in api:
        inline_keyboard.append(
            [
                InlineKeyboardButton(text=f"{i} - {platform[i]}",
                callback_data=f"apiTidal_{i}"
                )
            ]
        )
    inline_keyboard = inline_keyboard + exit_button
    return InlineKeyboardMarkup(inline_keyboard)


def common_auth_set(provider):
    inline_keyboard = [
        [
            InlineKeyboardButton(
                text=lang.ADD_AUTH_BUTTON,
                callback_data=f"ADA_{provider}_add"
            ),
            InlineKeyboardButton(
                text=lang.REMOVE_AUTH_BUTTON,
                callback_data=f"RMA_{provider}_warn"
            )
        ]
    ]
    inline_keyboard = inline_keyboard + exit_button
    return InlineKeyboardMarkup(inline_keyboard)

def confirm_RMA_button():
    inline_keyboard = [
        [
            InlineKeyboardButton(
                text=lang.YES_BUTTON,
                callback_data="RMA_tidal_yes"
            ),
            InlineKeyboardButton(
                text=lang.NO_BUTTON,
                callback_data="RMA_tidal_no"
            )
        ]
    ]
    inline_keyboard = inline_keyboard + exit_button
    return InlineKeyboardMarkup(inline_keyboard)

def quality_buttons(provider, data=None):
    if provider == "tidal":
        inline_keyboard = [
            [
                InlineKeyboardButton(
                    text=lang.MASTER_QUALITY,
                    callback_data="SQA_tidal_Master"
                )
            ],
            [
                InlineKeyboardButton(
                    text=lang.HIFI_QUALITY,
                    callback_data="SQA_tidal_HiFi"
                )
            ],
            [
                InlineKeyboardButton(
                    text=lang.HIGH_QUALITY,
                    callback_data="SQA_tidal_High"
                )
            ],
            [
                InlineKeyboardButton(
                    text=lang.NORMAL_QUALITY,
                    callback_data="SQA_tidal_Normal"
                )
            ]
        ]
    elif provider == 'kkbox':
        inline_keyboard = []
        for quality in data:
            inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text=quality.upper(),
                    callback_data=f"SQA_kkbox_{quality}"
                )
            ]
            )
    elif provider == 'qobuz':
        inline_keyboard = [
            [
                InlineKeyboardButton(
                    text=lang.Q_320,
                    callback_data="SQA_qobuz_5"
                )
            ],
            [
                InlineKeyboardButton(
                    text=lang.Q_LOSELESS,
                    callback_data="SQA_qobuz_6"
                )
            ],
            [
                InlineKeyboardButton(
                    text=lang.Q_HIRES_7,
                    callback_data="SQA_qobuz_7"
                )
            ],
            [
                InlineKeyboardButton(
                    text=lang.Q_HIRES_27,
                    callback_data="SQA_qobuz_27"
                )
            ]
        ]
    elif provider == 'deezer':
        inline_keyboard = [
            [
                InlineKeyboardButton(
                    text=lang.HIFI_QUALITY,
                    callback_data="SQA_deezer_HiFi"
                )
            ],
            [
                InlineKeyboardButton(
                    text=lang.HIGH_QUALITY,
                    callback_data="SQA_deezer_High"
                )
            ],
            [
                InlineKeyboardButton(
                    text=lang.NORMAL_QUALITY,
                    callback_data="SQA_deezer_Normal"
                )
            ]
        ]
    inline_keyboard = inline_keyboard + exit_button
    return InlineKeyboardMarkup(inline_keyboard)

def kkbox_menu_set():
    inline_keyboard = [
        [
            InlineKeyboardButton(
                text=lang.QUALITY_BUTTON,
                callback_data="QA_kkbox"
            )
        ]
    ]
    inline_keyboard = inline_keyboard + exit_button
    return InlineKeyboardMarkup(inline_keyboard)

def qobuz_menu_set():
    inline_keyboard = [
        [
            InlineKeyboardButton(
                text=lang.QUALITY_BUTTON,
                callback_data="QA_qobuz"
            )
        ]
    ]
    inline_keyboard = inline_keyboard + exit_button
    return InlineKeyboardMarkup(inline_keyboard)

def deezer_menu_set():
    inline_keyboard = [
        [
            InlineKeyboardButton(
                text=lang.QUALITY_BUTTON,
                callback_data="QA_deezer"
            )
        ],
        [
            InlineKeyboardButton(
                text=lang.SPATIAL_BUTTON,
                callback_data="spaDZ"
            )
        ]
    ]
    inline_keyboard = inline_keyboard + exit_button
    return InlineKeyboardMarkup(inline_keyboard)

def deezer_spatial_buttons(mhm1, spatial):
    e_mhm1 = lang.DZ_ENABLE_MHM1
    e_mha1 = lang.DZ_ENABLE_MHA1
    e_spatial = lang.ENABLE_BUTTON
    d_spatal = lang.DISABLE_BUTTON
    if mhm1:
        e_mhm1 = e_mhm1 + " ✅" 
    else:
        e_mha1 = e_mha1 + " ✅"
    if spatial:
        e_spatial = e_spatial + " ✅"
    else:
        d_spatal = d_spatal + " ✅"

    inline_keyboard = [
        [
            InlineKeyboardButton(
                text=e_mhm1,
                callback_data="setspaDZ_mhm1"
            ),
            InlineKeyboardButton(
                text=e_mha1,
                callback_data="setspaDZ_mha1"
            )
        ],
        [
            InlineKeyboardButton(
                text=e_spatial,
                callback_data="setspaDZ_enable"
            ),
            InlineKeyboardButton(
                text=d_spatal,
                callback_data="setspaDZ_disable"
            )
        ]
    ]
    inline_keyboard = inline_keyboard + exit_button
    return InlineKeyboardMarkup(inline_keyboard)
