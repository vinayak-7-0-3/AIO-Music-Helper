
# AIO Music Helper

An all-in-one bot to handle all your musomaniac needs
## Features

- Supports Spotify, Deezer, Tidal, Qobuz, KKBOX
## Installation
**Pre-req :** Docker & Git installed  

Clone the github repo
```
git clone https://github.com/vinayak-7-0-3/AIO-Music-Helper
```  
Get into the directory AIO-Music-Helper
```
cd AIO-Music-Helper
```
Fill in the sample.env file  
Use nano or any editor as you like
```
nano sample.env
```
Build the docker image
```
sudo docker build . -t aiomusic
```
Run the image
```
sudo docker run -d --name aiom aiomusic
```
To check the logs
```
sudo docker container logs aiom
```

## Environment Variables

**REQUIRED**  

`TG_BOT_TOKEN` - Your Telegram Bot Token (From BotFather)

`APP_ID` - Your Telegram Account App ID (From my.telegram.org)

`API_HASH` - Your Telegram Api Hash (From my.telegram.org)

`ADMINS` - List of ID of admin users (int, seperated by space)

`BOT_USERNAME` - Telegram username of your bot (str)

`DATABASE_URL` - PostgresDB Connection URL (str)

**OPTIONAL**  

`AUTH_CHAT` - List of chats where the bot will work (int, seperated by space)

`IS_BOT_PUBLIC` - Is your bot Public (True or False)

`LOG_CHAT` - Chat for logging (int, ID)

`LOG_ALL_INFO` - Wheather to log all the info's to chat specified in LOG_CHAT (True or False)

`AUTH_USERS` - List of ID of users who are allowed to use the bot (int, seperated by space)

`BOT_LANGUAGE` - Language for Bot Interface/Interaction (In International Country Code)

`ANTI_SPAM_MODE` - Only allows one task per user. For groups one task at a time (True or False)

`KKBOX_KEY` - Key for KKBOX Api (Get from [OrpheusDL](https://t.me/orpheusdl))

`KKBOX_EMAIL` - Your KKBOX account email

`KKBOX_PASSWORD` - Your KKBOX account password

`QOBUZ_EMAIL` - Your Qobuz account email (Not needed if using Qobuz USER ID)

`QOBUZ_PASSWORD` - Your Qobuz account password (Not needed if using Qobuz TOKEN)

`QOBUZ_USER` - Your Qobuz User ID (Not needed if using Email-Pass)

`QOBUZ_TOKEN` - Your Qobuz User TOKEN (Not needed if using Email-Pass)

`DEEZER_EMAIL` - Your Deezer account email (Not needed if using Deezer ARL)

`DEEZER_PASSWORD` - Your Deezer account password (Not needed if using Deezer ARL)

`DEEZER_BF_SECRET` - Deezer BF Secret for API (Get from [OrpheusDL](https://t.me/orpheusdl))

`DEEZER_TRACK_URL_KEY` - Deezer URL Key for API (Get from [OrpheusDL](https://t.me/orpheusdl))

`DEEZER_ARL` - Your Deezer ARL Key (Not needed if using Email-Pass)

`SPOTIFY_EMAIL` - Your Spotify Email

`SPOTIFY_PASS` - Your Spotify Password 

`COPY_AUDIO_FILES` - If to copy the songs downloaded to a specific chat (True or False)

`DUPLICATE_CHECK` - Check if the song was already downloaded (True or False) (This feature is not fully stable and needs a larger database)

`SPOTIFY_CHAT` - Chat where to copy Spotify songs (int)

`QOBUZ_CHAT` - Chat where to copy Qobuz songs (int)

`TIDAL_CHAT` - Chat where to copy Tidal songs (int)

`DEEZER_CHAT` - Chat where to copy Deezer songs (int)

`KKBOX_CHAT` - Chat where to copy KKBOX songs (int)
## Some notes to consider

- Required variables are must and without these bot won't start.
- AUTH_USERS variable is only needed if you have set IS_BOT_PUBLIC to False
- Qobuz has two login methods. Either you can use ID-TOKEN or EMAIL-PASS. Any one method is only needed. If you fill both then the email-pass will be used.
- Similarly Deezer has two methods. Either you can use Deezer ARL or EMAIL-PASS combo. Any one is ony required.
- For the above mentioned cases, please use your own creds. Please don't steal someone else's
- Even if you fill Deezer Creds, it needs Key and Secret to work.
- Similarly the case for KKBOX. It also needs a key
- LOG_CHAT is the chat where the bot will send all the bot logs as message.
- Spotify can do magic with free account but others can't.
- Bot commands are editable ([Here](https://github.com/vinayak-7-0-3/AIO-Music-Helper/blob/main/bot/__init__.py#L10))
- You can edit the format of uploaded message for Track/Album/Playlist ([Here](https://github.com/vinayak-7-0-3/AIO-Music-Helper/blob/main/bot/helpers/translations/tr_en.py#L52)). The values supported are shown in the dict [here](https://github.com/vinayak-7-0-3/AIO-Music-Helper/blob/main/bot/helpers/utils/metadata.py#L17). In simpler terms you can edit the captions.
- Do consider to set quality settings for each platform from the settings panel for the better.



## Credits
- **Yaronzz** - For [Tidal-Media-Downloader](https://github.com/yaronzz/Tidal-Media-Downloader)
- [**Orpheus-DL Community**](https://github.com/yarrm80s/orpheusdl) - For KKBOX and Deezer 
- **vitiko98** - For [qobuz-dl](https://github.com/vitiko98/qobuz-dl)
- **ZSpotify** - For Spotify