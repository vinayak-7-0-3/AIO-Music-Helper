from config import Config
from bot.helpers.translations.tr_en import EN

lang = None
if Config.BOT_LANGUAGE == "en":
    lang = EN()
else:
    lang = EN()
