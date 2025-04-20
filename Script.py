import os
import logging
from pytube import YouTube
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)
from urllib.parse import urlparse, parse_qs

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot configuration
TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
DOWNLOAD_FOLDER = "./downloads"

# Validate YouTube URL (same as before)
def validate_youtube_url(url):
    try:
        parsed = urlparse(url)
        if parsed.netloc in ['www.youtube.com', 'youtube.com', 'youtu.be']:
            if 'v=' in parsed.query:
                return True
            elif parsed.path.startswith('/watch'):
                return True
            elif parsed.netloc == 'youtu.be':
                return True
        return False
    except:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_text(
        f"Hi {user.first_name}!\n\n"
        "I'm a YouTube downloader bot. Send me a YouTube URL and I'll download it for you.\n\n"
        "Commands:\n"
        "/start - Show this message\n"
        "/help - Show help information\n\n"
        "Just send me a YouTube link to get started!"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    await update.message.reply_text(
        "How to use this bot:\n\n"
        "1. Send me a YouTube URL (e.g., https://youtube.com/watch?v=...)\n"
        "2. I'll show you the video info\n"
        "3. Choose the format you want to download\n\n"
        "Supported formats:\n"
        "- Video (various qualities)\n"
        "- Audio only (MP3)"
    )

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle YouTube URL sent by user."""
    url = update.message.text.strip()
    
    if not validate_youtube_url(url):
        await update.message.reply_text("❌ That doesn't look like a valid YouTube URL. Please try again.")
        return
    
    try:
        yt = YouTube(url)
        context.user_data['current_url'] = url
        
        # Create download options keyboard
        keyboard = [
            [
                InlineKeyboardButton("🎥 Best Video", callback_data="best_video"),
                InlineKeyboardButton("🎵 Audio Only", callback_data="audio"),
            ],
            [
                InlineKeyboardButton("720p", callback_data="720p"),
                InlineKeyboardButton("480p", callback_data="480p"),
                InlineKeyboardButton("360p", callback_data="360p"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"📹 <b>{yt.title}</b>\n"
            f"👤 {yt.author}\n"
            f"⏱ {yt.length//60}:{yt.length%60:02d}\n"
            f"👀 {yt.views:,} views\n\n"
            "Choose download option:",
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"Error processing URL: {e}")
        await update.message.reply_text("❌ Sorry, I couldn't process that video. Please try another one.")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button presses from the inline keyboard."""
    query = update.callback_query
    await query.answer()
    
    url = context.user_data.get('current_url')
    if not url:
        await query.edit_message_text("⚠️ Session expired. Please send the URL again.")
        return
    
    try:
        yt = YouTube(url)
        chat_id = query.message.chat_id
        
        # Create downloads directory if it doesn't exist
        if not os.path.exists(DOWNLOAD_FOLDER):
            os.makedirs(DOWNLOAD_FOLDER)
        
        await query.edit_message_text("⏳ Downloading your file... Please wait.")
        
        if query.data == "audio":
            # Download audio
            stream = yt.streams.get_audio_only()
            file_path = stream.download(output_path=DOWNLOAD_FOLDER)
            await context.bot.send_audio(
                chat_id=chat_id,
                audio=open(file_path, 'rb'),
                title=yt.title,
                performer=yt.author,
                caption=f"🎵 {yt.title}"
            )
        else:
            # Download video
            if query.data == "best_video":
                stream = yt.streams.get_highest_resolution()
            else:
                stream = yt.streams.filter(res=query.data, progressive=True).first()
                if not stream:
                    stream = yt.streams.get_highest_resolution()
            
            file_path = stream.download(output_path=DOWNLOAD_FOLDER)
            await context.bot.send_video(
                chat_id=chat_id,
                video=open(file_path, 'rb'),
                caption=f"📹 {yt.title} ({stream.resolution})"
            )
        
        # Clean up the downloaded file
        os.remove(file_path)
        await query.edit_message_text("✅ Download complete!")
        
    except Exception as e:
        logger.error(f"Error downloading video: {e}")
        await query.edit_message_text("❌ Sorry, something went wrong during download. Please try again.")

def main():
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Run the bot
    application.run_polling()

if __name__ == "__main__":
    main()
