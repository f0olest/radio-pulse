import requests
import time

RADIO_URL = "https://80.93.61.249/api/nowplaying"
TG_TOKEN = "8022390178:AAEzVQyZThtzNg0oDyBWy155T9dSWPm3MOo"
CHAT_ID = "@sncpr"  # канал

last_mix = None

while True:
    try:
        data = requests.get(RADIO_URL, timeout=10).json()

        current = data["now_playing"]["song"]["text"]

        if current != last_mix:
            msg = f"СЕЙЧАС В ЭФИРЕ:\n{current}"
            requests.post(
                f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
                data={
                    "chat_id": CHAT_ID,
                    "text": msg,
                    "disable_web_page_preview": True
                }
            )
            last_mix = current

    except Exception as e:
        print("error:", e)

    time.sleep(60)
