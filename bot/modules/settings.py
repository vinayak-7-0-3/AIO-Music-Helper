from bot import CMD
from pyrogram import Client, filters

import bot.helpers.tidal_func.apikey as tidalAPI

from bot.helpers.translations import lang
from bot.helpers.buttons.settings_buttons import *
from bot.helpers.database.postgres_impl import set_db
from bot.helpers.tidal_func.settings import TIDAL_SETTINGS
from bot.helpers.utils.auth_check import check_id, checkLogins
from bot.helpers.tidal_func.events import loginTidal, getapiInfoTidal, checkAPITidal

# MAIN COMMAND
@Client.on_message(filters.command(CMD.SETTINGS))
async def settings(bot, update):
    if await check_id(update.from_user.id, restricted=True):
        await bot.send_message(
            chat_id=update.chat.id,
            text=lang.select.INIT_SETTINGS_MENU,
            reply_markup=main_menu_set()
        )


# TIDAL SETTINGS PANEL
@Client.on_callback_query(filters.regex(pattern=r"^tidalPanel"))
async def tidal_panel_cb(bot, update):
    if await check_id(update.from_user.id, restricted=True):
        quality, _ = set_db.get_variable("TIDAL_QUALITY")
        api_index = TIDAL_SETTINGS.apiKeyIndex
        db_auth, _ = set_db.get_variable("TIDAL_AUTH_DONE")
        await bot.edit_message_text(
            chat_id=update.message.chat.id,
            message_id=update.message.id,
            text=lang.select.TIDAL_SETTINGS_PANEL.format(
                quality,
                api_index,
                db_auth
            ),
            reply_markup=tidal_menu_set()
        )


# API SETTINGS FOR TIDAL-DL
@Client.on_callback_query(filters.regex(pattern=r"^apiTidal"))
async def tidal_api_cb(bot, update):
    if await check_id(update.from_user.id, restricted=True):
        option = update.data.split("_")[1]
        current_api = TIDAL_SETTINGS.apiKeyIndex
        api, platform, validity, quality = await getapiInfoTidal()
        info = ""
        for number in api:
            info += f"<b>● {number} - {platform[number]}</b>\nFormats - <code>{quality[number]}</code>\nValid - <code>{validity[number]}</code>\n"
        if option == "panel":
            await bot.edit_message_text(
                chat_id=update.message.chat.id,
                message_id=update.message.id,
                text=lang.select.TIDAL_SELECT_API_KEY.format(
                    tidalAPI.getItem(current_api)['platform'],
                    tidalAPI.getItem(current_api)['formats'],
                    tidalAPI.getItem(current_api)['valid'],
                    info
                ),
                reply_markup=tidal_api_set(api, platform)
            )
        else:
            set_db.set_variable("TIDAL_API_KEY_INDEX", option, False, None)
            await update.answer(lang.select.API_KEY_CHANGED.format(
                api,
                tidalAPI.getItem(api)['platform'],
            )
        )
        TIDAL_SETTINGS.read()
        await checkAPITidal()
        try:
            await tidal_api_cb(bot, update)
        except:
            pass


# GLOBAL FUNCTION TO REMOVE AUTH
@Client.on_callback_query(filters.regex(pattern=r"^RMA"))
async def rmauth_cb(bot, update):
    if await check_id(update.from_user.id, restricted=True):
        provider = update.data.split("_")[1]
        remove = update.data.split("_")[2]
        if remove == "warn":
            await bot.edit_message_text(
                chat_id=update.message.chat.id,
                message_id=update.message.id,
                text=lang.select.WARN_REMOVE_AUTH.format(provider.title()),
                reply_markup=confirm_RMA_button()
            )
        else:
            if provider == "tidal":
                set_db.set_variable("TIDAL_AUTH_TOKEN", 0, True, None)
                set_db.set_variable("TIDAL_AUTH_DONE", False, False, None)
                buttons = tidal_menu_set()
            await bot.edit_message_text(
                chat_id=update.message.chat.id,
                message_id=update.message.id,
                text=lang.select.RM_AUTH_SUCCESSFULL.format(provider.title()),
                reply_markup=buttons
            )


# GLOBAL FUNCTION TO ADD AUTH
@Client.on_callback_query(filters.regex(pattern=r"^ADA"))
async def add_auth_cb(bot, update):
    if await check_id(update.from_user.id, restricted=True):
        provider = update.data.split("_")[1]
        option = update.data.split("_")[2]
        if option == "panel":
            if provider == "tidal":
                auth, msg = await checkLogins("tidal")
                await bot.edit_message_text(
                    chat_id=update.message.chat.id,
                    message_id=update.message.id,
                    text=lang.select.COMMON_AUTH_PANEL.format(provider.title(), msg),
                    reply_markup=common_auth_set(provider)
                )
        else:
            if provider == "tidal":
                await loginTidal(bot, update, update.message.chat.id)
                set_db.set_variable("TIDAL_AUTH_DONE", True, False, None)
            else:
                pass

# FOR QUALITY OPTIONS
@Client.on_callback_query(filters.regex(pattern=r"^QA"))
async def quality_cb(bot, update):
    if await check_id(update.from_user.id, restricted=True):
        provider = update.data.split("_")[1]
        if provider == "tidal":
            current_quality, _ = set_db.get_variable("TIDAL_QUALITY")
            if not current_quality:
                current_quality = "Default"
            await bot.edit_message_text(
                chat_id=update.message.chat.id,
                message_id=update.message.id,
                text=lang.select.QUALITY_SET_PANEL.format(provider.title(), current_quality),
                reply_markup=quality_buttons(provider)
            )

# FOR SETTING QUALITY
@Client.on_callback_query(filters.regex(pattern=r"^SQA"))
async def set_quality_cb(bot, update):
    if await check_id(update.from_user.id, restricted=True):
        provider = update.data.split("_")[1]
        quality = update.data.split("_")[2]

        if provider == "tidal":
            set_db.set_variable("TIDAL_QUALITY", quality, False, None)
            current_quality, _ = set_db.get_variable("TIDAL_QUALITY")
            if not current_quality:
                current_quality = "Default"
            await bot.edit_message_text(
                chat_id=update.message.chat.id,
                message_id=update.message.id,
                text=lang.select.QUALITY_SET_PANEL.format(provider.title(), current_quality),
                reply_markup=quality_buttons(provider)
            )

@Client.on_callback_query(filters.regex(pattern=r"^main_menu"))
async def main_menu_cb(bot, update):
    if await check_id(update.from_user.id, restricted=True):
        try:
            await bot.edit_message_text(
                chat_id=update.message.chat.id,
                message_id=update.message.id,
                text=lang.select.INIT_SETTINGS_MENU,
                reply_markup=main_menu_set()
            )
        except:
            pass

@Client.on_callback_query(filters.regex(pattern=r"^close"))
async def close_cb(bot, update):
    if await check_id(update.from_user.id, restricted=True):
        try:
            await bot.delete_messages(
                chat_id=update.message.chat.id,
                message_ids=update.message.id
            )
        except:
            pass