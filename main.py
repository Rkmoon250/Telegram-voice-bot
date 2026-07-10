from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import subprocess
import os
import tempfile

TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hi! Send me an audio file and I'll convert it into a Telegram voice note."
    )

async def convert_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.audio:
        await update.message.reply_text("Please send an audio file.")
        return

    audio = await update.message.audio.get_file()

    with tempfile.TemporaryDirectory() as temp_dir:
        input_file = os.path.join(temp_dir, "input")
        output_file = os.path.join(temp_dir, "voice.ogg")

        await audio.download_to_drive(input_file)

        result = subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i", input_file,
                "-c:a", "libopus",
                "-b:a", "64k",
                output_file
            ],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            await update.message.reply_text(
                "❌ FFmpeg error:\n" + result.stderr[:500]
            )
            return

        with open(output_file, "rb") as voice:
            await update.message.reply_voice(voice=voice)

app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.AUDIO, convert_audio))

app.run_polling()
