from config import Config
from pyrogram import Client

bot = Config.BOT_USERNAME

plugins = dict(
    root="bot/modules"
)

class CMD(object):
    START = ["start", f"start@{bot}"]
    HELP = ["help", f"help@{bot}"]
    # Open Settings Panel
    SETTINGS = ["settings", f"settings@{bot}"]
    DOWNLOAD = ["download", f"download@{bot}"]
    # Auth user or chat to use the bot
    # TODO Add cmd to remove auth
    AUTH = ["auth", f"auth@{bot}"]
    # Add user as admin user
    ADD_ADMIN = ["add_sudo", f"add_sudo@{bot}"]
    # To execute shell cmds
    SHELL = ["shell", f"shell@{bot}"]

aio = Client(
    "AIO-Music-Bot",
    api_id=Config.APP_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.TG_BOT_TOKEN,
    plugins=plugins,
    workdir=Config.WORK_DIR
)

cmd = CMD()