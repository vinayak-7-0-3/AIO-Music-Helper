from unittest import result
from bot import CMD
from config import LOGGER
from pyrogram import Client, filters

from bot.helpers.translations import lang
from bot.helpers.utils.check_link import check_link
from bot.helpers.tidal_func.events import startTidal
from bot.helpers.database.postgres_impl import user_settings
from bot.helpers.utils.auth_check import check_id, checkLogins

@Client.on_message(filters.command(CMD.DOWNLOAD))
async def download_tidal(bot, update):
    if await check_id(message=update):
        try:
            if update.reply_to_message:
                link = update.reply_to_message.text
                reply_to_id = update.reply_to_message.id
            else:
                link = update.text.split(" ", maxsplit=1)[1]
                reply_to_id = update.id
        except:
            link = None

        if link:
            user_settings.set_var(update.chat.id, "ON_TASK", True)
            provider = await check_link(link)
            if provider:
                err, err_msg = await checkLogins(provider)
                if err:
                    return await bot.send_message(
                        chat_id=update.chat.id,
                        text=err_msg,
                        reply_to_message_id=update.id
                    )

            LOGGER.info(f"Download Initiated By - {update.from_user.first_name}")
            msg = await bot.send_message(
                chat_id=update.chat.id,
                text=lang.select.START_DOWNLOAD,
                reply_to_message_id=update.id
            )
            botmsg_id = msg.id
            if update.from_user.username:
                u_name = f"@{update.from_user.username}"
            else:
                u_name = f'<a href="tg://user?id={update.from_user.id}">{update.from_user.first_name}</a>'

            if provider == "tidal":
                await startTidal(link, bot, update.chat.id, reply_to_id, update.from_user.id, u_name)




            user_settings.set_var(update.chat.id, "ON_TASK", False)
            