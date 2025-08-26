@bot.message_handler(func=lambda m: True)
def handle_query(m):
    uid = m.from_user.id
    if not is_member(uid):
        chan = CHANNEL_ID
        if chan and chan.startswith('@'):
            join_link = f"https://t.me/{chan[1:]}"
        else:
            join_link = CHANNEL_ID or "لینک کانال موجود نیست"
        bot.send_message(uid, f"لطفاً ابتدا عضو کانال شوید:\n{join_link}")
        return

    query = m.text.strip()
    bot.send_message(uid, "⏳ در حال جستجو...")
    results = tmdb_search(query)
    if not results:
        bot.send_message(uid, "نتیجه‌ای در TMDb پیدا نشد. سعی کنید اسم رو دقیق‌تر وارد کنید.")
        return

    markup = types.InlineKeyboardMarkup()
    for it in results:
        label = f"{it['title']}" + (f" ({it['year']})" if it.get('year') else "")
        cb = f"select|{it['media_type']}|{it['id']}|{it['title']}"
        markup.add(types.InlineKeyboardButton(label, callback_data=cb))
    bot.send_message(uid, "نتایج پیدا شد — یکی را انتخاب کن:", reply_markup=markup)

# --- وقتی کاربر روی یکی از نتیجه ها کلیک کرد ---
@bot.callback_query_handler(func=lambda c: c.data and c.data.startswith("select|"))
def callback_select(call):
    uid = call.from_user.id
    parts = call.data.split("|",3)
    if len(parts) < 4:
        bot.send_message(uid, "خطا در دیتا.")
        return
    media_type, tmdb_id, tmdb_title = parts[1], parts[2], parts[3]

    # نمایش اطلاعات از TMDb (اختیاری)
    if TMDB_API_KEY:
        details_url = f"https://api.themoviedb.org/3/{'movie' if media_type=='movie' else 'tv'}/{tmdb_id}?api_key={TMDB_API_KEY}&language=en-US"
        r = requests.get(details_url, timeout=10)
        if r.status_code == 200:
            movie = r.json()
            title = movie.get('title') or movie.get('name') or tmdb_title
            overview = movie.get('overview','توضیحی وجود ندارد.')
            poster = movie.get('poster_path')
            poster_url = f"https://image.tmdb.org/t/p/w500{poster}" if poster else None
            if poster_url:
                bot.send_photo(uid, poster_url, caption=f"🎬 {title}\n\n{overview}")
            else:
                bot.send_message(uid, f"🎬 {title}\n\n{overview}")
        else:
            bot.send_message(uid, f"🎬 {tmdb_title}")
    else:
        bot.send_message(uid, f"🎬 {tmdb_title}")

    # حالا سرچ در Internet Archive برای لینک مستقیم قانونی
    bot.send_message(uid, "🔎 دنبال نسخه‌های رایگان قانونی در Internet Archive می‌گردم...")
    found = find_archive_mp4(tmdb_title)
    if found:
        bot.send_message(uid, f"✅ لینک دانلود قانونی:\n{found['download_url']}\n\n(از این لینک می‌تونید مستقیم دانلود کنید.)")
    else:
        bot.send_message(uid, "متأسفم — نسخه قانونی رایگان در Internet Archive پیدا نشد. می‌تونید نام دیگه‌ای امتحان کنید یا از کانال پیگیری کنید.")

# --- اجرا ---
print("Bot started...")
bot.infinity_polling()
