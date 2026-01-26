import requests
import time
import urllib3
import json

urllib3.disable_warnings()

RADIO_URL = "https://80.93.61.249/api/nowplaying"
TG_TOKEN = "8022390178:AAEzVQyZThtzNg0oDyBWy155T9dSWPm3MOo"
CHAT_ID = "@sncpr"
RADIO_LINK = "https://spotandchoos.com/radiotma"

last_mix = None
announced_next = None

while True:
    try:
        response = requests.get(RADIO_URL, timeout=10, verify=False)
        data = response.json()
        station = data[0] if isinstance(data, list) else data

        # --- текущий трек ---
        song_data = station["now_playing"]["song"]
        song_text = song_data.get("text", "Unknown")
        artist = song_data.get("artist", "")
        title = song_data.get("title", "")

        current_msg = (
            f"СЕЙЧАС В ЭФИРЕ:\n"
            f"<b>{artist}</b> - {title}\n\n"
            f'<a href="{RADIO_LINK}">слушать радио</a>'
        )

        if song_text != last_mix:
            requests.post(
                f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
                data={
                    "chat_id": CHAT_ID,
                    "text": current_msg,
                    "parse_mode": "HTML"
                }
            )
            last_mix = song_text
            announced_next = None

        # --- анонс следующего трека за 5 минут ---
        next_data = station.get("playing_next", {})
        next_song = next_data.get("song")
        next_cued_at = next_data.get("cued_at")

        if next_song and next_cued_at:
            send_time = next_cued_at - 5 * 60
            now_ts = int(time.time())
            if send_time > now_ts and announced_next != next_song.get("id"):
                next_artist = next_song.get("artist", "")
                next_title = next_song.get("title", "")

                next_msg = (
                    f"Через 5 минут в эфире:\n"
                    f"<b>{next_artist}</b> - {next_title}\n\n"
                    f'<a href="{RADIO_LINK}">слушать радио</a>'
                )

                requests.post(
                    f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
                    data={
                        "chat_id": CHAT_ID,
                        "text": next_msg,
                        "parse_mode": "HTML"
                    }
                )
                announced_next = next_song.get("id")

    except Exception as e:
        print("error:", e)

    time.sleep(60)
