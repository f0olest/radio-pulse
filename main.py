import requests
import time
import urllib3
from datetime import datetime

urllib3.disable_warnings()

RADIO_URL = "https://80.93.61.249/api/nowplaying"
TG_TOKEN = "8022390178:AAEzVQyZThtzNg0oDyBWy155T9dSWPm3MOo"
CHAT_ID = "@sncpr"
RADIO_LINK = "https://spotandchoos.com/radiotma"

last_mix_id = None
message_id = None
coming_up_sent = False  # флаг, чтобы не спамить coming up

def format_time(seconds):
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    else:
        return f"{m:02d}:{s:02d}"

def build_progress_bar(elapsed, duration, length=10):
    percent = int((elapsed / duration) * 100) if duration > 0 else 0
    filled = int(length * percent / 100)
    empty = length - filled
    bar = "#" * filled + "~" * empty
    return bar, percent

while True:
    try:
        data = requests.get(RADIO_URL, timeout=10, verify=False).json()
        station = data[0] if isinstance(data, list) else data

        # текущий трек
        song = station["now_playing"]["song"]
        song_id = song.get("id")
        artist = song.get("artist", "Unknown")
        title = song.get("title", "Unknown")
        elapsed = station["now_playing"].get("elapsed", 0)
        duration = station["now_playing"].get("duration", 1)  # защита от деления на 0

        # следующий трек
        next_song_data = station.get("playing_next", {}).get("song")
        next_artist = next_song_data.get("artist", "скоро новый микс") if next_song_data else "скоро новый микс"
        next_title = next_song_data.get("title", "") if next_song_data else ""

        bar, percent = build_progress_bar(elapsed, duration, length=10)

        # формируем текст текущего трека
        text = f"СЕЙЧАС В ЭФИРЕ:\n<b>{artist}</b> - {title}\n\n"

        if elapsed < duration:
            # обычный прогресс
            text += f"progress:\n{bar} {percent}% ({format_time(elapsed)} / {format_time(duration)})\n\n"
        else:
            # трек закончился → finished at <time>
            now_time = datetime.utcnow().strftime("%H:%M:%S")
            text += f"finished at {now_time}\n\n"

        text += f'<a href="{RADIO_LINK}">слушать радио</a>'

        # новый трек
        if song_id != last_mix_id:
            # если предыдущее сообщение есть — убираем прогресс
            if message_id:
                old_text = f"СЕЙЧАС В ЭФИРЕ:\n<b>{song.get('artist','Unknown')}</b> - {song.get('title','Unknown')}\n\n<a href='{RADIO_LINK}'>слушать радио</a>"
                requests.post(
                    f"https://api.telegram.org/bot{TG_TOKEN}/editMessageText",
                    data={
                        "chat_id": CHAT_ID,
                        "message_id": message_id,
                        "text": old_text,
                        "parse_mode": "HTML"
                    }
                )

            resp = requests.post(
                f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
                data={
                    "chat_id": CHAT_ID,
                    "text": text,
                    "parse_mode": "HTML"
                }
            ).json()
            message_id = resp["result"]["message_id"]
            last_mix_id = song_id
            coming_up_sent = False  # сброс флага на новый трек

        # обновление прогресса текущего трека
        else:
            if message_id:
                requests.post(
                    f"https://api.telegram.org/bot{TG_TOKEN}/editMessageText",
                    data={
                        "chat_id": CHAT_ID,
                        "message_id": message_id,
                        "text": text,
                        "parse_mode": "HTML"
                    }
                )

        # отправка отдельного сообщения "coming up next", если прогресс >= 90% и ещё не отправляли
        if percent >= 90 and not coming_up_sent and next_song_data and elapsed < duration:
            coming_text = f"coming up next:\n<b>{next_artist}</b> - {next_title}"
            requests.post(
                f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
                data={
                    "chat_id": CHAT_ID,
                    "text": coming_text,
                    "parse_mode": "HTML"
                }
            )
            coming_up_sent = True

    except Exception as e:
        print("error:", e)

    time.sleep(15)  # обновляем каждые 15 секунд