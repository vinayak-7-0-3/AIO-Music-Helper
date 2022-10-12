# AIO-Music-Helper-Bot
Telegram bot to manage all your music needs.

## ⚠️ WORK IN PROGRESS ⚠️


```

sudo apt install python3-virtualenv

virtualenv -p python3 VENV

. ./VENV/bin/activate

pip install -r requirements.txt

pip install psycopg2-binary 

python -m bot

```
- For Database URL use Heroku Postgres (if on Heroku) or ElephantSQL

## Deploy VPS METHOD-2 (STABIL) AND BASIC

- Start Docker daemon (skip if already running), if installed by snap then use 2nd command:
    
        sudo dockerd
        sudo snap start docker

     Note: If not started or not starting, run the command below then try to start.

        sudo apt install docker.io

- Build Docker image:

        sudo docker build . -t aiomusic-dl-bot

- Run the image:

        sudo docker run aiomusic-dl-bot

- To stop the image:

        sudo docker ps
        sudo docker stop id

- To clear the container:

        sudo docker container prune

- To delete the images:

        sudo docker image prune -a
