import requests
import time
import urllib3
import json

urllib3.disable_warnings()

RADIO_URL = "https://80.93.61.249/api/nowplaying"
TG_TOKEN = "8022390178:AAEzVQyZThtzNg0oDyBWy155T9dSWPm3MOo"
CHAT_ID = "@sncpr"

last_mix = None

while True:
    try:
        response = requests.get(RADIO_URL, timeout=10, verify=False)
        data = response.json()

        # Debug: раскомментировать для просмотра структуры JSON
        # print(json.dumps(data, indent=2))

        # Подстраиваемся под то, что приходит: массив или объект
        if isinstance(data, list):
            station = data[0]
        else:
            station = data

        # Достаём текущий трек
        current = station["now_playing"]["song"]["text"]

        # Проверяем, поменялся ли трек
        if current != last_mix:
            msg = f"СЕЙЧАС В ЭФИРЕ:\n{current}"
            requests.post(
                f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
                data={"chat_id": CHAT_ID, "text": msg}
            )
            last_mix = current

    except Exception as e:
        print("error:", e)

    # Пауза перед следующим запросом
    time.sleep(60)
