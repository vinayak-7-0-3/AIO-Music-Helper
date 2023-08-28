from bot import CMD
from pyrogram import Client, filters

from bot.logger import LOGGER
from bot.helpers.translations import lang
from bot.helpers.utils.common import clean_up
from bot.helpers.database.postgres_impl import user_settings
from bot.helpers.utils.providers import checkLogins, check_link
from bot.helpers.utils.tg_utils import check_id, send_message, fetch_user_details

from bot.helpers.qobuz.handler import qobuz
from bot.helpers.deezer.handler import deezerdl
from bot.helpers.kkbox.kkbox_helper import kkbox
from bot.helpers.spotify.handler import spotify_dl
from bot.helpers.tidal_func.events import startTidal

@Client.on_message(filters.command(CMD.DOWNLOAD))
async def download_track(bot, update):
    if await check_id(message=update):
        try:
            if update.reply_to_message:
                link = update.reply_to_message.text
                reply = True
            else:
                link = update.text.split(" ", maxsplit=1)[1]
                reply = False
        except:
            return await bot.send_message(
                chat_id=update.chat.id,
                text=lang.ERR_NO_LINK,
                reply_to_message_id=update.id
            )
            
        if link:
            provider = await check_link(link)
            user = await fetch_user_details(update, reply, provider)
            user['link'] = link
            if provider:
                err, err_msg = await checkLogins(provider)
                if err:
                    return await send_message(user, err_msg)
            else:
                return await send_message(user, lang.ERR_LINK_RECOGNITION)
            
            await LOGGER.info(f"Download Initiated By - {user['name']} - {provider.upper()}")

            msg = await send_message(user, lang.START_DOWNLOAD)
            user['bot_msg'] = msg.id

            user_settings.set_var(update.chat.id, "ON_TASK", True)
            try:
                if provider == "tidal":
                    await startTidal(link, user)
                elif provider == "kkbox":
                    # TODO Fix KKBOX Metadata
                    await kkbox.start(link, user)
                elif provider == 'qobuz':
                    await qobuz.start(link, user)
                elif provider == 'deezer':
                    await deezerdl.start(link, user)
                elif provider == 'spotify':
                    await spotify_dl.start(link, user)
                await bot.delete_messages(update.chat.id, user['bot_msg'])
                await send_message(user, lang.TASK_COMPLETED)
            except Exception as e:
                await LOGGER.error(e, user)
                """await bot.send_message(
                    chat_id=update.chat.id,
                    text=e,
                    reply_to_message_id=update.id
                )"""
            user_settings.set_var(update.chat.id, "ON_TASK", False)

            await clean_up(user['r_id'], provider)
            