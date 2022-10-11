from bot import CMD
from pyrogram import Client, filters

from bot.helpers.translations import lang
from bot.helpers.buttons.settings_buttons import *
from bot.helpers.tidal_func.events import loginTidal
from bot.helpers.utils.auth_check import check_id, checkLogins
from bot.helpers.database.postgres_impl import set_db


@Client.on_message(filters.command(CMD.SETTINGS))
async def settings(bot, update):
    if await check_id(update.from_user.id, restricted=True):
        await bot.send_message(
            chat_id=update.chat.id,
            text=lang.select.INIT_SETTINGS_MENU,
            reply_markup=main_menu_set()
        )


@Client.on_callback_query(filters.regex(pattern=r"^tidalPanel"))
async def tidal_panel_cb(bot, update):
    if await check_id(update.from_user.id, restricted=True):
        await bot.edit_message_text(
            chat_id=update.message.chat.id,
            message_id=update.message.id,
            text=lang.select.TIDAL_SETTINGS_PANEL,
            reply_markup=tidal_menu_set()
    )

@Client.on_callback_query(filters.regex(pattern=r"^tidalAUTH"))
async def tidal_auth_cb(bot, update):
    if await check_id(update.from_user.id, restricted=True):
        auth, msg = await checkLogins("tidal")
        await bot.edit_message_text(
            chat_id=update.message.chat.id,
            message_id=update.message.id,
            text=lang.select.TIDAL_AUTH_PANEL.format(msg),
            reply_markup=tidal_auth_set()
        )



#
# GLOBAL FUNCTION TO REMOVE AUTH
#
@Client.on_callback_query(filters.regex(pattern=r"^RMA"))
async def rmauth_cb(bot, update):
    if await check_id(update.from_user.id, restricted=True):
        provider = update.data.split("_")[1]
        remove = update.data.split("_")[2]
        await bot.edit_message_text(
            chat_id=update.message.chat.id,
            message_id=update.message.id,
            text=lang.select.WARN_REMOVE_AUTH,
            reply_markup=confirm_RMA_button()
        )

        # TODO ADD FUNCTION HERE

#
# GLOBAL FUNCTION TO ADD AUTH
#
@Client.on_callback_query(filters.regex(pattern=r"^ADA"))
async def add_auth_cb(bot, update):
    if await check_id(update.from_user.id, restricted=True):
        provider = update.data.split("_")[1]
        if provider == "tidal":
            await loginTidal(bot, update, update.message.chat.id)
            set_db.set_variable("TIDAL_AUTH_DONE", True, False, None)
        else:
            pass
