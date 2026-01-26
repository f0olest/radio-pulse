import requests
import time
import urllib3

urllib3.disable_warnings()

RADIO_URL = "https://80.93.61.249/api/nowplaying"
TG_TOKEN = "8022390178:AAEzVQyZThtzNg0oDyBWy155T9dSWPm3MOo"
CHAT_ID = "@sncpr"
RADIO_LINK = "https://spotandchoos.com/radiotma"

last_mix_id = None
message_id = None

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
    return f"{bar} {percent}% ({format_time(elapsed)} / {format_time(duration)})"

while True:
    try:
        data = requests.get(RADIO_URL, timeout=10, verify=False).json()
        station = data[0] if isinstance(data, list) else data
        song = station["now_playing"]["song"]
        song_id = song.get("id")
        artist = song.get("artist", "Unknown")
        title = song.get("title", "Unknown")
        elapsed = station["now_playing"].get("elapsed", 0)
        duration = station["now_playing"].get("duration", 1)  # избегаем деления на 0

        # --- проверяем, новый трек или тот же ---
        if song_id != last_mix_id:
            # новое сообщение
            msg_text = (
                f"СЕЙЧАС В ЭФИРЕ:\n"
                f"<b>{artist}</b> - {title}\n\n"
                f"progress:\n{build_progress_bar(elapsed, duration)}\n\n"
                f'<a href="{RADIO_LINK}">слушать радио</a>'
            )

            resp = requests.post(
                f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
                data={
                    "chat_id": CHAT_ID,
                    "text": msg_text,
                    "parse_mode": "HTML"
                }
            ).json()

            message_id = resp["result"]["message_id"]
            last_mix_id = song_id

        else:
            # обновляем прогресс
            if message_id:
                # если трек уже закончился
                if elapsed >= duration:
                    text = (
                        f"СЕЙЧАС В ЭФИРЕ:\n"
                        f"<b>{artist}</b> - {title}\n\n"
                        f'<a href="{RADIO_LINK}">слушать радио</a>'
                    )
                else:
                    text = (
                        f"СЕЙЧАС В ЭФИРЕ:\n"
                        f"<b>{artist}</b> - {title}\n\n"
                        f"progress:\n{build_progress_bar(elapsed, duration)}\n\n"
                        f'<a href="{RADIO_LINK}">слушать радио</a>'
                    )

                requests.post(
                    f"https://api.telegram.org/bot{TG_TOKEN}/editMessageText",
                    data={
                        "chat_id": CHAT_ID,
                        "message_id": message_id,
                        "text": text,
                        "parse_mode": "HTML"
                    }
                )

    except Exception as e:
        print("error:", e)

    time.sleep(300)  # каждые 5 минут