from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters
import subprocess
import os

TOKEN = os.getenv("BOT_TOKEN")

async def convert_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.audio:
        return

    audio = await update.message.audio.get_file()

    input_file = "input.mp3"
    output_file = "voice.ogg"

    await audio.download_to_drive(input_file)

    subprocess.run([
        "ffmpeg",
        "-i", input_file,
        "-c:a", "libopus",
        "-b:a", "64k",
        output_file
    ])

    with open(output_file, "rb") as voice:
        await update.message.reply_voice(voice=voice)

    os.remove(input_file)
    os.remove(output_file)

app = Application.builder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.AUDIO, convert_audio))
app.run_polling()
