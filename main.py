import requests
import time
import urllib3
from datetime import datetime
from zoneinfo import ZoneInfo

urllib3.disable_warnings()

RADIO_URL = "https://80.93.61.249/api/nowplaying"
TG_TOKEN = "8022390178:AAEzVQyZThtzNg0oDyBWy155T9dSWPm3MOo"
CHAT_ID = "@sncpr"
RADIO_LINK = "https://spotandchoos.com/radiotma"

# === ВАЖНО: таймзона эфира ===
LOCAL_TZ = ZoneInfo("Asia/Novosibirsk")  # поменяй если надо

last_song_id = None
current_message_id = None
coming_up_sent = False
prev_artist = ""
prev_title = ""

def format_time(seconds):
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"

def progress_bar(elapsed, duration, length=10):
    percent = int((elapsed / duration) * 100) if duration > 0 else 0
    filled = int(length * percent / 100)
    bar = "█" * filled + "░" * (length - filled)
    return bar, percent

while True:
    try:
        data = requests.get(RADIO_URL, timeout=10, verify=False).json()
        station = data[0]

        now = station["now_playing"]
        song = now["song"]

        song_id = song["id"]
        artist = song.get("artist", "Unknown")
        title = song.get("title", "Unknown")
        elapsed = now.get("elapsed", 0)
        duration = now.get("duration", 1)

        next_song = station.get("playing_next", {}).get("song")
        next_artist = next_song.get("artist") if next_song else None
        next_title = next_song.get("title") if next_song else None

        bar, percent = progress_bar(elapsed, duration)

        # === ЕСЛИ ТРЕК СМЕНИЛСЯ → ЗАКРЫВАЕМ СТАРЫЙ ===
        if last_song_id and song_id != last_song_id and current_message_id:
            finished_local_time = datetime.now(ZoneInfo("UTC")).astimezone(LOCAL_TZ)

            finished_text = (
                f"СЕЙЧАС В ЭФИРЕ:\n"
                f"<b>{prev_artist}</b> - {prev_title}\n\n"
                f"finished at {finished_local_time.strftime('%H:%M:%S')}\n\n"
                f'<a href="{RADIO_LINK}">слушать радио</a>'
            )

            requests.post(
                f"https://api.telegram.org/bot{TG_TOKEN}/editMessageText",
                data={
                    "chat_id": CHAT_ID,
                    "message_id": current_message_id,
                    "text": finished_text,
                    "parse_mode": "HTML"
                }
            )

            coming_up_sent = False

        # === НОВЫЙ ТРЕК ===
        if song_id != last_song_id:
            text = (
                f"СЕЙЧАС В ЭФИРЕ:\n"
                f"<b>{artist}</b> - {title}\n\n"
                f"{bar} {percent}% ({format_time(elapsed)} / {format_time(duration)})\n\n"
                f'<a href="{RADIO_LINK}">слушать радио</a>'
            )

            resp = requests.post(
                f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
                data={
                    "chat_id": CHAT_ID,
                    "text": text,
                    "parse_mode": "HTML",
                    "disable_notification": False
                }
            ).json()

            current_message_id = resp["result"]["message_id"]
            last_song_id = song_id
            prev_artist = artist
            prev_title = title

        # === ОБНОВЛЕНИЕ ПРОГРЕССА ===
        else:
            text = (
                f"СЕЙЧАС В ЭФИРЕ:\n"
                f"<b>{artist}</b> - {title}\n\n"
                f"{bar} {percent}% ({format_time(elapsed)} / {format_time(duration)})\n\n"
                f'<a href="{RADIO_LINK}">слушать радио</a>'
            )

            requests.post(
                f"https://api.telegram.org/bot{TG_TOKEN}/editMessageText",
                data={
                    "chat_id": CHAT_ID,
                    "message_id": current_message_id,
                    "text": text,
                    "parse_mode": "HTML"
                }
            )

        # === COMING UP NEXT ===
        if percent >= 90 and not coming_up_sent and next_song:
            coming_text = f"NEXT\n<b>{next_artist}</b> - {next_title}"
            requests.post(
                f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
                data={
                    "chat_id": CHAT_ID,
                    "text": coming_text,
                    "parse_mode": "HTML",
                    "disable_notification": True
                }
            )
            coming_up_sent = True

    except Exception as e:
        print("error:", e)

    time.sleep(60)
