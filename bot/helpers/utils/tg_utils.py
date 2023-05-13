import os
import aigpy
from bot import aio
from config import Config

from bot.helpers.translations import lang
from bot.helpers.database.postgres_impl import users_db, admins_db, chats_db,\
    user_settings, set_db

from bot.helpers.utils.metadata import format_string

admins = []
allowed_chats = []
allowed_users = []

user_details = {
    'user_id': None,
    'name': None, # Name of the user 
    'user_name': None, # Username of the user
    'user_quality': None, # Quality requested for the track in the specific platform
    'r_id': None, # Reply to message id
    'chat_id': None,
    'provider': None,
    'bot_msg': None,
    'link': None,
    'override' : None # To skip checking media exist
}

#=================================
# MESSAGES
#=================================

# to_send - The thing to send
# details - Details of the user/chat where to send the message (Dict)
async def send_message(details, to_send, type='text', extra=None, markup=None, chat_id=None):
    chat_id = chat_id if chat_id else details['chat_id']
    if type == 'text':
        msg = await aio.send_message(
            chat_id=chat_id,
            text=to_send,
            reply_to_message_id=details['r_id'],
            reply_markup=markup,
            disable_web_page_preview=True
        )
        
    elif type == 'doc':
        pass

    elif type == 'audio':
        # Downloading thumb cuz pyrogram needs thumb as a file
        thumb = extra['thumbnail']
        if thumb and thumb.startswith('http'):
            path = Config.DOWNLOAD_BASE_DIR + f"/{extra['provider']}/{details['r_id']}/{extra['title']}_thumb.jpg"
            aigpy.net.downloadFile(extra['thumbnail'], path)
            thumb = path
        
        try:
            caption = await format_string(lang.TRACK_TEMPLATE, extra, details)
        except Exception as e:
            caption = None
        msg = await aio.send_audio(
            chat_id=chat_id,
            audio=to_send,
            caption=caption,
            duration=int(extra['duration']),
            performer=extra['artist'],
            title=extra['title'],
            thumb=thumb,
            reply_to_message_id=details['r_id']
        )
        os.remove(thumb)

    elif type == 'pic':
        msg = await aio.send_photo(
            chat_id=chat_id,
            photo=to_send,
            caption=extra,
            reply_to_message_id=details['r_id']
        )

    
    return msg

async def edit_message(details, msg_id, text, markup=None):
    msg_id = details['bot_msg'] if not msg_id else msg_id
    msg = await aio.edit_message_text(
        chat_id=details['chat_id'],
        message_id=msg_id,
        text=text,
        reply_markup=markup,
        disable_web_page_preview=True
    )
    return msg

async def copy_message(from_chat, to_chat, msg_id):
    msg = await aio.copy_message(
        chat_id=int(to_chat),
        from_chat_id=int(from_chat),
        message_id=int(msg_id)
    )
    return msg


async def fetch_user_details(msg, reply=False, provider=None, cb=False):
    details = user_details.copy()

    details['user_id'] = msg.from_user.id
    details['name'] = msg.from_user.first_name
    details['user_name'] = msg.from_user.username
    details['r_id'] = msg.reply_to_message.id if reply else msg.id
    details['chat_id'] = msg.chat.id
    if provider:
        details['provider'] = provider
        details['user_quality'] = user_settings.get_var(msg.from_user.id, f"{provider.upper()}_QUALITY") 
    try:
        details['bot_msg'] = msg.id
    except:
        pass
    return details

async def fetch_tg_link(msg_id: int, user: dict, provider):
    if provider == 'tidal':
        chat = Config.TIDAL_CHAT
    elif provider == 'qobuz':
        chat = Config.QOBUZ_CHAT
    elif provider == 'deezer':
        chat = Config.DEEZER_CHAT
    elif provider == 'spotify':
        chat = Config.SPOTIFY_CHAT
    elif provider == 'kkbox':
        chat = Config.KKBOX_CHAT
    msg = await aio.get_messages(
        int(chat),
        msg_id
    )
    return msg.link

#=================================
# AUTHENTICATIONS
#=================================
async def get_chats():
    # CHATS 
    database_chats = chats_db.get_chats()
    if not Config.AUTH_USERS == "":
        for chat in Config.AUTH_CHAT:
            if chat not in allowed_chats: allowed_chats.append(chat)
    for chat in database_chats:
        if chat != None:
            if chat[0] not in allowed_chats and chat[0] != None:
                allowed_chats.append(chat[0])
    # ADMINS
    database_admins = admins_db.get_admins()
    for admin in Config.ADMINS:
        if admin not in admins: admins.append(admin)
    for admin in database_admins:
        if admin != None:
            if admin[0] not in admins and admin[0] != None:
                admins.append(admin[0])
    # USERS
    if not Config.IS_BOT_PUBLIC == "True":
        database_users = users_db.get_users()
        if Config.AUTH_USERS == "":
            pass
        else:
            for user in Config.AUTH_USERS:
                if user not in allowed_users:
                    allowed_users.append(user)
            for user in database_users:
                if user != None:
                    if user[0] not in allowed_users and user[0] != None:
                        allowed_users.append(user[0])

async def check_id(id=None, message=None, restricted=False):
    all_list = allowed_chats + allowed_users + admins
    if restricted:
        if id in admins:
            return True
        else:
            return False
    else:
        # Seperating Group and PM
        if message.from_user.id != message.chat.id:
            id = message.chat.id
        else:
            id = message.from_user.id

        if Config.ANIT_SPAM_MODE == "True":
            check = user_settings.get_var(id, "ON_TASK")      
            if check:
                await message.reply_text(lang.ANTI_SPAM_WAIT)
                return False          

        if Config.IS_BOT_PUBLIC == "True":
            return True
        elif id in all_list:
            return True
        else:
            return False