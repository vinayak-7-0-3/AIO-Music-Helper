from bot.helpers.translations import lang
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

close_button = [
    [
        InlineKeyboardButton(text=lang.CLOSE_BUTTON, callback_data="close")
    ]
]

def get_music_button(user_id: int, links: list, item_id: int):
    inline_keyboard = []
    count = 0
    for link in links:
        inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text=lang.GET_MUSIC_BUTTON.format(links.index(link)),
                    url=link
                )
            ]
        )
    
    inline_keyboard.append(
        [
            InlineKeyboardButton(
                    text=lang.REDOWNLOAD_BUTTON,
                    callback_data=f"GET_{user_id}_{item_id}"
            )
        ]
    )
    inline_keyboard = inline_keyboard + close_button
    return InlineKeyboardMarkup(inline_keyboard)
