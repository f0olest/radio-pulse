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
            art_url = song.get("art")

            caption = (
                f"СЕЙЧАС В ЭФИРЕ:\n"
                f"<b>{artist}</b> - {title}\n\n"
                f"{bar} {percent}% ({format_time(elapsed)} / {format_time(duration)})\n\n"
                f'<a href="{RADIO_LINK}">слушать радио</a>'
            )

            if art_url:
                resp = requests.post(
                    f"https://api.telegram.org/bot{TG_TOKEN}/sendPhoto",
                    data={
                        "chat_id": CHAT_ID,
                        "caption": caption,
                        "parse_mode": "HTML",
                        "disable_notification": False
                    },
                    files={"photo": requests.get(art_url).content}
                ).json()
            else:
                resp = requests.post(
                    f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
                    data={
                        "chat_id": CHAT_ID,
                        "text": caption,
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
            caption = (
                f"СЕЙЧАС В ЭФИРЕ:\n"
                f"<b>{artist}</b> - {title}\n\n"
                f"{bar} {percent}% ({format_time(elapsed)} / {format_time(duration)})\n\n"
                f'<a href="{RADIO_LINK}">слушать радио</a>'
            )

            # Обновляем подпись у фото
            try:
                requests.post(
                    f"https://api.telegram.org/bot{TG_TOKEN}/editMessageCaption",
                    data={
                        "chat_id": CHAT_ID,
                        "message_id": current_message_id,
                        "caption": caption,
                        "parse_mode": "HTML"
                    }
                )
            except Exception as e:
                # fallback, если нет фото, редактируем текст
                requests.post(
                    f"https://api.telegram.org/bot{TG_TOKEN}/editMessageText",
                    data={
                        "chat_id": CHAT_ID,
                        "message_id": current_message_id,
                        "text": caption,
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
