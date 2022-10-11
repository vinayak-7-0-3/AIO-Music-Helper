tidal = ["https://tidal.com", "https://listen.tidal.com", "tidal.com", "listen.tidal.com"]
deezer = []
qobuz = ["https://play.qobuz.com", "https://open.qobuz.com", "https://www.qobuz.com"]
sc = []

async def check_link(link):
    if link.startswith(tuple(tidal)):
        return "tidal"
    elif link.startswith(tuple(deezer)):
        return "deezer"
    elif link.startswith(tuple(qobuz)):
        return "qobuz"
    elif link.startswith(tuple(sc)):
        return "sc"
    else:
        return None