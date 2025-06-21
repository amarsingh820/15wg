import logging
import asyncio
import json
import os
from telegram import Update, Document
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = "7858798129:AAFseoFMYGt9kW5VpzMzMw4aM59hI4AJXL4"
CHANNEL_ID = -1002328429536
GROUP_ID = -1002597420310
MOVIE_DB_FILE = "movies.json"

logging.basicConfig(level=logging.INFO)

if os.path.exists(MOVIE_DB_FILE):
    with open(MOVIE_DB_FILE, "r") as f:
        movie_db = json.load(f)
else:
    movie_db = []

def save_movies():
    with open(MOVIE_DB_FILE, "w") as f:
        json.dump(movie_db, f)

async def handle_group_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != GROUP_ID:
        return
    if not update.message or not update.message.document:
        return
    file: Document = update.message.document
    caption = update.message.caption or "No caption"
    title = caption.split("\n")[0].lower()
    movie_entry = {
        "title": title,
        "file_id": file.file_id,
        "caption": caption
    }
    if not any(m["file_id"] == file.file_id for m in movie_db):
        movie_db.append(movie_entry)
        save_movies()
        logging.info(f"✅ Saved movie: {title}")

async def handle_user_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    query = update.message.text.lower()
    found = False
    for movie in movie_db:
        if query in movie["title"]:
            msg = await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=movie["file_id"],
                caption=f"{movie['caption']}\n\n⚠️ यह फ़ाइल 2 मिनट में ऑटो डिलीट हो जाएगी, इसे फ़ॉरवर्ड कर लें।"
            )
            await asyncio.sleep(120)
            await msg.delete()
            found = True
    if not found:
        await update.message.reply_text("❌ कोई मूवी नहीं मिली।")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.Chat(GROUP_ID) & filters.Document.ALL, handle_group_message))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_query))

if __name__ == "__main__":
    print("🎬 Bot is running (Railway)...")
    app.run_polling()
