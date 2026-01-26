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

        if isinstance(data, list):
            station = data[0]
        else:
            station = data

        song_text = station["now_playing"]["song"]["text"]
        cover_url = station["now_playing"]["song"].get("art")  # обложка, если есть

        # Разбиваем текст на artist - title
        if " - " in song_text:
            artist, title = song_text.split(" - ", 1)
        else:
            artist, title = song_text, ""

        formatted_caption = (
            f"<b>{artist}</b> - {title}\n\n"
            f'<a href="{RADIO_LINK}">слушать радио</a>'
        )

        if song_text != last_mix:
            if cover_url:  # если есть обложка, отправляем фото
                requests.post(
                    f"https://api.telegram.org/bot{TG_TOKEN}/sendPhoto",
                    data={
                        "chat_id": CHAT_ID,
                        "photo": cover_url,
                        "caption": formatted_caption,
                        "parse_mode": "HTML"
                    }
                )
            else:  # если нет обложки, просто отправляем текст
                requests.post(
                    f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
                    data={
                        "chat_id": CHAT_ID,
                        "text": formatted_caption,
                        "parse_mode": "HTML"
                    }
                )
            last_mix = song_text

    except Exception as e:
        print("error:", e)

    time.sleep(60)
