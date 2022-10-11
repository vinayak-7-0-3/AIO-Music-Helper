import asyncio
from bot import CMD
from pyrogram import Client, filters
from bot.helpers.translations import lang
from bot.helpers.utils.auth_check import get_chats
from bot.helpers.utils.auth_check import check_id, get_chats
from bot.helpers.database.postgres_impl import users_db, admins_db, chats_db

@Client.on_message(filters.command(CMD.START))
async def start(bot, update):
    msg = await bot.send_message(
        chat_id=update.chat.id,
        text=lang.select.WELCOME_MSG.format(
            update.from_user.first_name
        ),
        reply_to_message_id=update.id
    )

@Client.on_message(filters.command(CMD.AUTH))
async def auth_chat(bot, update):
    if await check_id(update.from_user.id, restricted=True):
        if update.reply_to_message:
            chat_id = update.reply_to_message.from_user.id
        else:
            try:
                chat_id = int(update.text.split()[1])
            except:
                chat_id = update.chat.id
        
        if str(chat_id).startswith("-100"):
            type = "chat"
            chats_db.set_chats(int(chat_id))
        else:
            type = "user"
            users_db.set_users(int(chat_id))
        # For refreshing the global auth list
        await get_chats()

        await bot.send_message(
            chat_id=update.chat.id,
            text=lang.select.CHAT_AUTH_SUCCESS.format(
                type,
                chat_id
            ),
            reply_to_message_id=update.id
        )

@Client.on_message(filters.command(CMD.ADD_ADMIN))
async def add_admin(bot, update):
    if await check_id(update.from_user.id, restricted=True):
        if update.reply_to_message:
            admin_id = update.reply_to_message.from_user.id
        else:
            try:
                admin_id = update.text.split()[1]
                if admin_id.isnumeric():
                    pass
                else:
                    admin_id = None
            except:
                admin_id = None
        if admin_id:
            admins_db.set_admins(int(admin_id))
        else:
            await bot.send_message(
                chat_id=update.chat.id,
                text=lang.select.NO_ID_TO_AUTH,
                reply_to_message_id=update.id
            )
            return
        # For refreshing the global admin list
        await get_chats()

        await bot.send_message(
            chat_id=update.chat.id,
            text=lang.select.ADD_ADMIN_SUCCESS.format(
                admin_id
            ),
            reply_to_message_id=update.id
        )