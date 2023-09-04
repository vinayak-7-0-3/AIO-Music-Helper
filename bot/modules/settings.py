from bot import CMD
from config import Config
from pyrogram import Client, filters
from pyrogram.errors import MessageNotModified

import bot.helpers.tidal_func.apikey as tidalAPI

from bot.logger import LOGGER
from bot.helpers.translations import lang
from bot.helpers.qobuz.handler import qobuz
from bot.helpers.qobuz.qopy import qobuz_api
from bot.helpers.kkbox.kkapi import kkbox_api
from bot.helpers.deezer.handler import deezerdl
from bot.helpers.spotify.spotifyapi import spotify
from bot.helpers.buttons.settings_buttons import *
from bot.helpers.database.postgres_impl import set_db
from bot.helpers.tidal_func.settings import TIDAL_SETTINGS
from bot.helpers.utils.tg_utils import check_id
from bot.helpers.utils.providers import checkLogins
from bot.helpers.utils.tg_utils import send_message, edit_message,fetch_user_details
from bot.helpers.tidal_func.events import loginByWeb, getapiInfoTidal, checkAPITidal
from bot.helpers.utils.common import botsetting


# MAIN COMMAND
@Client.on_message(filters.command(CMD.SETTINGS))
async def settings(bot, update):
    if await check_id(update.from_user.id, restricted=True):
        user = await fetch_user_details(update)
        await send_message(user, lang.INIT_SETTINGS_MENU, markup=main_menu_set())

#
#
# SETTING PANELS
#
#

# TIDAL
@Client.on_callback_query(filters.regex(pattern=r"^tidalPanel"))
async def tidal_panel_cb(bot, update):
    if await check_id(update.from_user.id, restricted=True):
        user = await fetch_user_details(update.message)
        quality, _ = set_db.get_variable("TIDAL_QUALITY")
        api_index = TIDAL_SETTINGS.apiKeyIndex
        text = lang.TIDAL_SETTINGS_PANEL.format(quality, api_index, botsetting.tidal_auth)
        await edit_message(user, update.message.id, text, tidal_menu_set())

# KKBOX
@Client.on_callback_query(filters.regex(pattern=r"^kkboxPanel"))
async def kkbox_panel_cb(bot, update):
    if await check_id(update.from_user.id, restricted=True):
        quality, _ = set_db.get_variable("KKBOX_QUALITY")
        quality = quality if quality else ''
        await bot.edit_message_text(
            chat_id=update.message.chat.id,
            message_id=update.message.id,
            text=lang.KKBOX_SETTINGS_PANEL.format(
                quality.upper(),
                botsetting.kkbox_auth
            ),
            reply_markup=kkbox_menu_set()
        )

# QOBUZ
@Client.on_callback_query(filters.regex(pattern=r"^qobuzPanel"))
async def qobuz_panel_cb(bot, update):
    if await check_id(update.from_user.id, restricted=True):
        quality, _ = set_db.get_variable("QOBUZ_QUALITY")
        quality = await qobuz.human_quality(int(quality))
        await bot.edit_message_text(
            chat_id=update.message.chat.id,
            message_id=update.message.id,
            text=lang.QOBUZ_SETTINGS_PANEL.format(
                quality,
                botsetting.qobuz_auth
            ),
            reply_markup=qobuz_menu_set()
        )

# DEEZER
@Client.on_callback_query(filters.regex(pattern=r"^deezerPanel"))
async def deezer_panel_cb(bot, update):
    if await check_id(update.from_user.id, restricted=True):
        quality, _ = set_db.get_variable("DEEZER_QUALITY")
        spatial, _ = set_db.get_variable("DEEZER_SPATIAL")
        quality = await deezerdl.parse_quality(quality, False, True)
        auth_by = 'By ARL' if Config.DEEZER_ARL != "" else 'By Creds'
        await bot.edit_message_text(
            chat_id=update.message.chat.id,
            message_id=update.message.id,
            text=lang.DEEZER_SETTINGS_PANEL.format(
                quality,
                botsetting.qobuz_auth,
                auth_by,
                spatial
            ),
            reply_markup=deezer_menu_set()
        )

# SPOTIFY
@Client.on_callback_query(filters.regex(pattern=r"^spotifyPanel"))
async def spotify_panel_cb(bot, update):
    if await check_id(update.from_user.id, restricted=True):
        quality, _ = set_db.get_variable("SPOTIFY_QUALITY")
        reencode, _ = set_db.get_variable("SPOTIFY_REENCODE")
        format, _ = set_db.get_variable("SPOTIFY_FORMAT")
        try:
            await bot.edit_message_text(
                chat_id=update.message.chat.id,
                message_id=update.message.id,
                text=lang.SPOTIFY_SETTINGS_PANEL.format(
                    quality,
                    botsetting.spotify_auth,
                    reencode,
                    format.upper()
                ),
                reply_markup=spotify_menu_set(reencode, format)
            )
        except MessageNotModified: pass
#
#
# QUALITY SETTINGS
#
#

# INIT QUALITY PANEL FOR RESPECTIVE MODULE
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
            current_quality = await qobuz.human_quality(int(_quality))
        elif provider == 'deezer':
            _quality, _ = set_db.get_variable("DEEZER_QUALITY")
            current_quality = await deezerdl.parse_quality(_quality, False, True)
        elif provider == 'spotify':
            _quality, _ = set_db.get_variable("SPOTIFY_QUALITY")
            current_quality = str(_quality) + 'k'
            data = spotify.premiuim
        await bot.edit_message_text(
            chat_id=update.message.chat.id,
            message_id=update.message.id,
            text=lang.QUALITY_SET_PANEL.format(provider.title(), current_quality),
            reply_markup=quality_buttons(provider, data)
        )

# SET QUALITY
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
            current_quality = await qobuz.human_quality(int(quality))
        elif provider == 'deezer':
            await deezerdl.set_quality(quality)
            current_quality = quality
        elif provider == 'spotify':
            spotify.handle_quality(int(quality))
            set_db.set_variable("SPOTIFY_QUALITY", quality, False, None)
            current_quality = str(quality) + 'k'
            data = spotify.premiuim
        try:
            await bot.edit_message_text(
                chat_id=update.message.chat.id,
                message_id=update.message.id,
                text=lang.QUALITY_SET_PANEL.format(provider.title(), current_quality),
                reply_markup=quality_buttons(provider, data)
            )
        except MessageNotModified:
            pass
        except Exception as e:
            await LOGGER.error(e)

#
#
# OTHER HANDLERS
#
#

# API SETTINGS FOR TIDAL-DL
@Client.on_callback_query(filters.regex(pattern=r"^apiTidal"))
async def tidal_api_cb(bot, update, refresh=False):
    if await check_id(update.from_user.id, restricted=True):
        user = await fetch_user_details(update.message)
        option = update.data.split("_")[1]
        current_api = TIDAL_SETTINGS.apiKeyIndex
        api, platform, validity, quality = await getapiInfoTidal()
        info = ""
        for number in api:
            info += f"<b>● {number} - {platform[number]}</b>\nFormats - <code>{quality[number]}</code>\nValid - <code>{validity[number]}</code>\n"
        if option == "panel" or refresh == True:
            text = lang.TIDAL_SELECT_API_KEY.format(
                    tidalAPI.getItem(current_api)['platform'],
                    tidalAPI.getItem(current_api)['formats'],
                    tidalAPI.getItem(current_api)['valid'],
                    info
            )
            await edit_message(user, update.message.id, text, tidal_api_set(api, platform))
        else:
            set_db.set_variable("TIDAL_API_KEY_INDEX", option, False, None)
            await update.answer(
                lang.TIDAL_API_KEY_CHANGED.format(
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
            text=lang.DZ_SPATIAL_PANEL,
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
            text=lang.DZ_SPATIAL_PANEL,
            reply_markup=deezer_spatial_buttons(pref_mhm1, allow_spatial)
        )


# FUNCTION TO REMOVE AUTH FOR TIDAL
@Client.on_callback_query(filters.regex(pattern=r"^RMA"))
async def rmauth_cb(bot, update):
    if await check_id(update.from_user.id, restricted=True):
        user = await fetch_user_details(update.message)
        provider = update.data.split("_")[1]
        remove = update.data.split("_")[2]
        if remove == "warn":
            text = lang.WARN_REMOVE_AUTH.format(provider.title())
            await edit_message(user, update.message.id, text, confirm_RMA_button())
        else:
            if provider == "tidal":
                set_db.set_variable("TIDAL_AUTH_TOKEN", 0, True, None)
                set_db.set_variable("TIDAL_AUTH_DONE", False, False, None)
            text = lang.RM_AUTH_SUCCESSFULL.format(provider.title())
            await edit_message(user, update.message.id, text, tidal_menu_set())


# FUNCTION TO ADD AUTH FOR TIDAL
@Client.on_callback_query(filters.regex(pattern=r"^ADA"))
async def add_auth_cb(bot, update):
    if await check_id(update.from_user.id, restricted=True):
        user = await fetch_user_details(update.message)
        provider = update.data.split("_")[1]
        option = update.data.split("_")[2]
        if option == "panel":
            if provider == "tidal":
                auth, msg = await checkLogins("tidal")
                text=lang.COMMON_AUTH_PANEL.format(provider.title(), msg)
                await edit_message(user, update.message.id, text, common_auth_set(provider))
        else:
            if provider == "tidal":
                await loginByWeb(user)
                set_db.set_variable("TIDAL_AUTH_DONE", True, False, None)
            else:
                pass

# FUCTION TO SET SPOTIFY FORMAT/REENCODE OPTIONS
@Client.on_callback_query(filters.regex(pattern=r"^encspot"))
async def enc_set_spot_cb(bot, update):
    if await check_id(update.from_user.id, restricted=True):
        data = update.data.split("_")[1]
        if data == 'format':
            cur_f = spotify.music_format
            set_f = 'mp3' if cur_f == 'ogg' else 'ogg'
            if set_f == 'mp3' and not spotify.reencode:
                await update.answer(lang.ERR_SPOT_NOT_ENCODE_MP3)
                spotify.reencode = True
                set_db.set_variable('SPOTIFY_REENCODE', True)
            set_db.set_variable('SPOTIFY_FORMAT', set_f)
            spotify.music_format = set_f
        elif data == 're':
            set_enc = False if spotify.reencode else True
            set_db.set_variable('SPOTIFY_REENCODE', set_enc)
            spotify.reencode = set_enc
        await spotify_panel_cb(bot, update)


@Client.on_callback_query(filters.regex(pattern=r"^main_menu"))
async def main_menu_cb(bot, update):
    if await check_id(update.from_user.id, restricted=True):
        try:
            await bot.edit_message_text(
                chat_id=update.message.chat.id,
                message_id=update.message.id,
                text=lang.INIT_SETTINGS_MENU,
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