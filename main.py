import requests
import time
import urllib3
import json

urllib3.disable_warnings()

RADIO_URL = "https://80.93.61.249/api/nowplaying"
TG_TOKEN = "8022390178:AAEzVQyZThtzNg0oDyBWy155T9dSWPm3MOo"
CHAT_ID = "@sncpr"
RADIO_LINK = "https://spotandchoos.com/radiotma"
DEFAULT_COVER = "https://spotandchoos.com/assets/default_radio_cover.jpg"  # стандартная обложка

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

        song_data = station["now_playing"]["song"]
        song_text = song_data.get("text", "Unknown")
        cover_url = song_data.get("art") or DEFAULT_COVER  # fallback на баннер

        if " - " in song_text:
            artist, title = song_text.split(" - ", 1)
        else:
            artist, title = song_text, ""

        formatted_msg = (
            f"<b>{artist}</b> - {title}\n\n"
            f'<a href="{RADIO_LINK}">слушать радио</a>'
        )

        if song_text != last_mix:
            # Всегда отправляем фото (текущий или стандартный)
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

    except Exception as e:
        print("error:", e)

    time.sleep(60)import requests
import time
import urllib3
import json

urllib3.disable_warnings()

RADIO_URL = "https://80.93.61.249/api/nowplaying"
TG_TOKEN = "8022390178:AAEzVQyZThtzNg0oDyBWy155T9dSWPm3MOo"
CHAT_ID = "@sncpr"
RADIO_LINK = "https://spotandchoos.com/radiotma"
DEFAULT_COVER = "https://spotandchoos.com/assets/default_radio_cover.jpg"  # стандартная обложка

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

        song_data = station["now_playing"]["song"]
        song_text = song_data.get("text", "Unknown")
        cover_url = song_data.get("art") or DEFAULT_COVER  # fallback на баннер

        if " - " in song_text:
            artist, title = song_text.split(" - ", 1)
        else:
            artist, title = song_text, ""

        formatted_msg = (
            f"<b>{artist}</b> - {title}\n\n"
            f'<a href="{RADIO_LINK}">слушать радио</a>'
        )

        if song_text != last_mix:
            # Всегда отправляем фото (текущий или стандартный)
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

    except Exception as e:
        print("error:", e)

    time.sleep(60)
