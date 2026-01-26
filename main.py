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

while True:
    try:
        response = requests.get(RADIO_URL, timeout=10, verify=False)
        data = response.json()

        # Debug: посмотреть структуру JSON
        # print(json.dumps(data, indent=2))

        if isinstance(data, list):
            station = data[0]
        else:
            station = data

        song_text = station["now_playing"]["song"]["text"]

        # Разбиваем текст на artist - title
        if " - " in song_text:
            artist, title = song_text.split(" - ", 1)
        else:
            artist, title = song_text, ""

        formatted_msg = (
            f"СЕЙЧАС В ЭФИРЕ:\n"
            f"<b>{artist}</b> - {title}\n\n"
            f'<a href="{RADIO_LINK}">слушать радио</a>'
        )

        if song_text != last_mix:
            requests.post(
                f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
                data={
                    "chat_id": CHAT_ID,
                    "text": formatted_msg,
                    "parse_mode": "HTML"  # <- чтобы ссылка и жирный шрифт работали
                }
            )
            last_mix = song_text

    except Exception as e:
        print("error:", e)

    time.sleep(60)
