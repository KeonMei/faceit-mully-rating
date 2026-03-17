import os
from dotenv import load_dotenv

from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

from src.analyzer import analyze_player
from src.player import get_player_info
from src.trend import get_match_scores, build_trend_chart
from src.maps import get_map_stats


load_dotenv()

FACEIT_API_KEY = os.getenv("FACEIT_API_KEY")
BOT_TOKEN = os.getenv("TG_BOT_TOKEN")

headers = {
    "Authorization": f"Bearer {FACEIT_API_KEY}"
}

user_requests = {}

# -------------START FUNCTION -------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "Send FACEIT nickname"
    )

# ------------HANDLE NICKNAME-----------
async def handle_nickname(update: Update, context: ContextTypes.DEFAULT_TYPE):

    nickname = update.message.text.strip()

    user_id = update.message.from_user.id

    user_requests[user_id] = nickname

    keyboard = [
        [
            InlineKeyboardButton("10", callback_data="m10"),
            InlineKeyboardButton("30", callback_data="m30"),
            InlineKeyboardButton("50", callback_data="m50"),
            InlineKeyboardButton("100", callback_data="m100"),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"Player: {nickname}\nChoose number of matches:",
        reply_markup=reply_markup
    )

# ---------------mATCH CALLBACK------------------------------------------
async def matches_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    data = query.data

    if not data.startswith("m"):
        return

    user_id = query.from_user.id

    nickname = user_requests[user_id]

    match_limit = int(data[1:])

    context.user_data["match_limit"] = match_limit

    score, rank, bar, matches, avatar, elo, level, flag, match_scores, match_maps = analyze_player(
        nickname,
        headers,
        match_limit
    )   

    text = (
        f"👤 {nickname}\n"
        f"{flag} | Level {level} | {elo} ELO\n\n"
        f"Matches analyzed: {matches}\n\n"
        f"Mully Rating: {score}\n"
        f"{bar}\n\n"
        f"Rank: {rank}"
    )

    keyboard = [
        [
            InlineKeyboardButton("Trend 📈", callback_data="trend"),
            InlineKeyboardButton("Maps 🗺", callback_data="maps")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.reply_photo(
        photo=avatar,
        caption=text,
        reply_markup=reply_markup
    )

# ---------------------TREND CALLBACK----------------------------------------------
async def trend_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    nickname = user_requests[user_id]

    match_limit = context.user_data.get("match_limit", 30)

    player_id, avatar, elo, level, country = get_player_info(nickname, headers)

    scores = get_match_scores(player_id, headers, match_limit)

    chart = build_trend_chart(scores)

    await query.message.reply_photo(chart)

# -------------------------MAPS CALLBACK-----------------------------
async def maps_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    nickname = user_requests.get(user_id)

    if not nickname:
        await query.message.reply_text("Send FACEIT nickname again.")
        return

    player_id, avatar, elo, level, country = get_player_info(nickname, headers)

    stats = get_map_stats(player_id, headers)

    BAR_LEN = 10

    tier_color = {
        "S": "🟣",
        "A": "🔵",
        "B": "🟢",
        "C": "🟡",
        "D": "🔴"
    }

    match_limit = context.user_data.get("match_limit", 30)

    player_id, avatar, elo, level, country = get_player_info(nickname, headers)

    stats = get_map_stats(player_id, headers, match_limit)

    text = f"🗺 Map Mully Rating (last {match_limit} matches)\n\n"
    text += "<pre>"

    for m, score, tier, games in stats[:8]:

        filled = int((score / 100) * BAR_LEN)

        bar = "█" * filled + "░" * (BAR_LEN - filled)

        circle = tier_color.get(tier, "⚪")

        map_name = m.ljust(13)

        score_txt = f"{score:.1f}".rjust(5)

        text += f"{circle} {map_name} | {score_txt} | {bar}\n"

    text += "</pre>"

    await query.message.reply_text(text, parse_mode="HTML")

# --------------------------BOT RUN------------------------------------------
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_nickname))

app.add_handler(CallbackQueryHandler(matches_callback, pattern="^m[0-9]+$"))
app.add_handler(CallbackQueryHandler(trend_callback, pattern="trend"))
app.add_handler(CallbackQueryHandler(maps_callback, pattern="maps"))

print("Bot started")

app.run_polling()