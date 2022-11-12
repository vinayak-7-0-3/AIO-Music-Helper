import shutil

from bot import LOGGER
from config import Config

async def clean_up(r_id, provider):
    path = Config.DOWNLOAD_BASE_DIR + f"/{provider}/{r_id}"
    try:
        shutil.rmtree(path)
    except OSError as e:
        LOGGER.warning(e)

