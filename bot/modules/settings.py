from config import Config
from bot import CMD, LOGGER
from pyrogram import Client, filters
from pyrogram.errors import MessageNotModified

import bot.helpers.tidal_func.apikey as tidalAPI

from bot.helpers.translations import lang
from bot.helpers.qobuz.qopy import qobuz_api
from bot.helpers.kkbox.kkapi import kkbox_api
from bot.helpers.deezer.handler import deezerdl
from bot.helpers.qobuz.utils import human_quality
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


# KKBOX SETTINGS PANEL
@Client.on_callback_query(filters.regex(pattern=r"^kkboxPanel"))
async def kkbox_panel_cb(bot, update):
    if await check_id(update.from_user.id, restricted=True):
        quality, _ = set_db.get_variable("KKBOX_QUALITY")
        auth, _ = set_db.get_variable("KKBOX_AUTH")
        await bot.edit_message_text(
            chat_id=update.message.chat.id,
            message_id=update.message.id,
            text=lang.select.KKBOX_SETTINGS_PANEL.format(
                quality.upper(),
                auth
            ),
            reply_markup=kkbox_menu_set()
        )

# QOBUZ SETTINGS PANEL
@Client.on_callback_query(filters.regex(pattern=r"^qobuzPanel"))
async def qobuz_panel_cb(bot, update):
    if await check_id(update.from_user.id, restricted=True):
        quality, _ = set_db.get_variable("QOBUZ_QUALITY")
        quality = await human_quality(int(quality))
        auth, _ = set_db.get_variable("QOBUZ_AUTH")
        await bot.edit_message_text(
            chat_id=update.message.chat.id,
            message_id=update.message.id,
            text=lang.select.QOBUZ_SETTINGS_PANEL.format(
                quality,
                auth
            ),
            reply_markup=qobuz_menu_set()
        )

# DEEZER SETTINGS PANEL
@Client.on_callback_query(filters.regex(pattern=r"^deezerPanel"))
async def deezer_panel_cb(bot, update):
    if await check_id(update.from_user.id, restricted=True):
        quality, _ = set_db.get_variable("DEEZER_QUALITY")
        spatial, _ = set_db.get_variable("DEEZER_SPATIAL")
        quality = await deezerdl.parse_quality(quality, False, True)
        auth, _ = set_db.get_variable("DEEZER_AUTH")
        auth_by = 'By ARL' if Config.DEEZER_ARL != "" else 'By Creds'
        await bot.edit_message_text(
            chat_id=update.message.chat.id,
            message_id=update.message.id,
            text=lang.select.DEEZER_SETTINGS_PANEL.format(
                quality,
                auth,
                auth_by,
                spatial
            ),
            reply_markup=deezer_menu_set()
        )
        

# API SETTINGS FOR TIDAL-DL
@Client.on_callback_query(filters.regex(pattern=r"^apiTidal"))
async def tidal_api_cb(bot, update, refresh=False):
    if await check_id(update.from_user.id, restricted=True):
        option = update.data.split("_")[1]
        current_api = TIDAL_SETTINGS.apiKeyIndex
        api, platform, validity, quality = await getapiInfoTidal()
        info = ""
        for number in api:
            info += f"<b>● {number} - {platform[number]}</b>\nFormats - <code>{quality[number]}</code>\nValid - <code>{validity[number]}</code>\n"
        if option == "panel" or refresh == True:
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
            await update.answer(
                lang.select.TIDAL_API_KEY_CHANGED.format(
                    int(option),
                    tidalAPI.getItem(int(option))['platform'],
                )
            )
            TIDAL_SETTINGS.read()
            await checkAPITidal()
            try:
                await tidal_api_cb(bot, update, True)
            except:
                pass

# SPATIAL AUDIO SETTINGS FOR DEEZER
@Client.on_callback_query(filters.regex(pattern=r"^spaDZ"))
async def dz_spatial_cb(bot, update):
    if await check_id(update.from_user.id, restricted=True):
        pref_mhm1, allow_spatial = await deezerdl.spatial_deezer('get')
        await bot.edit_message_text(
            chat_id=update.message.chat.id,
            message_id=update.message.id,
            text=lang.select.DZ_SPATIAL_PANEL,
            reply_markup=deezer_spatial_buttons(pref_mhm1, allow_spatial)
        )

# SET SPATIAL SETTINGS FOR DEEZER
@Client.on_callback_query(filters.regex(pattern=r"^setspaDZ"))
async def set_dz_spatial_cb(bot, update):
    if await check_id(update.from_user.id, restricted=True):
        option = update.data.split("_")[1]
        # Values after setting the user input
        pref_mhm1, allow_spatial = await deezerdl.spatial_deezer('set', option)
        await bot.edit_message_text(
            chat_id=update.message.chat.id,
            message_id=update.message.id,
            text=lang.select.DZ_SPATIAL_PANEL,
            reply_markup=deezer_spatial_buttons(pref_mhm1, allow_spatial)
        )


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
        data = None
        if provider == "tidal":
            current_quality, _ = set_db.get_variable("TIDAL_QUALITY")
            if not current_quality:
                current_quality = "Default"
        elif provider == 'kkbox':
            current_quality, _ = set_db.get_variable("KKBOX_QUALITY")
            data  = kkbox_api.available_qualities
        elif provider == 'qobuz':
            _quality, _ = set_db.get_variable("QOBUZ_QUALITY")
            current_quality = await human_quality(int(_quality))
        elif provider == 'deezer':
            _quality, _ = set_db.get_variable("DEEZER_QUALITY")
            current_quality = await deezerdl.parse_quality(_quality, False, True)

        await bot.edit_message_text(
            chat_id=update.message.chat.id,
            message_id=update.message.id,
            text=lang.select.QUALITY_SET_PANEL.format(provider.title(), current_quality),
            reply_markup=quality_buttons(provider, data)
        )
            

# FOR SETTING QUALITY
@Client.on_callback_query(filters.regex(pattern=r"^SQA"))
async def set_quality_cb(bot, update):
    if await check_id(update.from_user.id, restricted=True):
        provider = update.data.split("_")[1]
        quality = update.data.split("_")[2]
        data = None
        if provider == "tidal":
            set_db.set_variable("TIDAL_QUALITY", quality, False, None)
            current_quality, _ = set_db.get_variable("TIDAL_QUALITY")
            if not current_quality:
                current_quality = "Default"
        elif provider == 'kkbox':
            set_db.set_variable("KKBOX_QUALITY", quality, False, None)
            current_quality = quality
            data = kkbox_api.available_qualities
        elif provider == 'qobuz':
            set_db.set_variable("QOBUZ_QUALITY", quality, False, None)
            qobuz_api.quality = int(quality)
            current_quality = await human_quality(int(quality))
        elif provider == 'deezer':
            await deezerdl.set_quality(quality)
            current_quality = quality
        try:
            await bot.edit_message_text(
                chat_id=update.message.chat.id,
                message_id=update.message.id,
                text=lang.select.QUALITY_SET_PANEL.format(provider.title(), current_quality),
                reply_markup=quality_buttons(provider, data)
            )
        except MessageNotModified:
            pass
        except Exception as e:
            LOGGER.warning(e)


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