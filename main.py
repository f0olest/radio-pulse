import requests
import time
import urllib3
import json

urllib3.disable_warnings()

RADIO_URL = "https://80.93.61.249/api/nowplaying"
TG_TOKEN = "8022390178:AAEzVQyZThtzNg0oDyBWy155T9dSWPm3MOo"
CHAT_ID = "@sncpr"
RADIO_LINK = "https://spotandchoos.com/radiotma"
DEFAULT_COVER = "https://spotandchoos.com/assets/default_radio_cover.jpg"  # fallback

last_mix = None
announced_next = None

while True:
    try:
        response = requests.get(RADIO_URL, timeout=10, verify=False)
        data = response.json()

        if isinstance(data, list):
            station = data[0]
        else:
            station = data

        # --- текущий трек ---
        song_data = station["now_playing"]["song"]
        song_text = song_data.get("text", "Unknown")
        cover_url = song_data.get("art") or DEFAULT_COVER

        if " - " in song_text:
            artist, title = song_text.split(" - ", 1)
        else:
            artist, title = song_text, ""

        formatted_msg = (
            f"<b>{artist}</b> - {title}\n\n"
            f'<a href="{RADIO_LINK}">слушать радио</a>'
        )

        if song_text != last_mix:
            # Отправка текущего трека
            requests.post(
                f"https://api.telegram.org/bot{TG_TOKEN}/sendPhoto",
                data={
                    "chat_id": CHAT_ID,
                    "photo": cover_url,
                    "caption": formatted_msg,
                    "parse_mode": "HTML"
                }
            )
            last_mix = song_text
            announced_next = None  # сброс анонса при смене трека

        # --- анонс следующего трека за 5 минут ---
        next_song_data = station["now_playing"].get("next_song")
        if next_song_data and next_song_data.get("text") and next_song_data.get("start_time"):
            next_text = next_song_data["text"]
            start_time = next_song_data["start_time"]  # timestamp
            send_time = start_time - 5 * 60
            now_ts = int(time.time())

            if now_ts >= send_time and announced_next != next_text:
                if " - " in next_text:
                    next_artist, next_title = next_text.split(" - ", 1)
                else:
                    next_artist, next_title = next_text, ""

                next_cover = next_song_data.get("art") or DEFAULT_COVER

                next_msg = (
                    f"Через 5 минут в эфире:\n"
                    f"<b>{next_artist}</b> - {next_title}\n\n"
                    f'<a href="{RADIO_LINK}">слушать радио</a>'
                )

                requests.post(
                    f"https://api.telegram.org/bot{TG_TOKEN}/sendPhoto",
                    data={
                        "chat_id": CHAT_ID,
                        "photo": next_cover,
                        "caption": next_msg,
                        "parse_mode": "HTML"
                    }
                )
                announced_next = next_text

    except Exception as e:
        print("error:", e)

    # --- ожидание перед следующим циклом ---
    time.sleep(60)
