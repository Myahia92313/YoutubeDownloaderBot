from telegram.ext import Application, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
import re
import logging
import os
import asyncio
import shutil

# Regex for validating YouTube URLs
YOUTUBE_URL_REGEX = r'(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+'

# Global dictionary to keep track of user requests
user_requests = {}

# Function to validate YouTube URLs
def is_valid_youtube_url(url):
    return re.match(YOUTUBE_URL_REGEX, url) is not None

# Function to handle user responses for download options
async def handle_download_option(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_action = query.data
    user_id = query.from_user.id
    video_link = user_requests.get(user_id)
    
    logger.info(f"User action: {user_action}, Video link: {video_link}")
    
    if not video_link:
        await query.answer("No valid YouTube link found. Please start again.")
        return

    # Step 1: Handle direct download or command choice
    if user_action in ["video", "image", "subtitles", "all"]:
        context.user_data[user_id] = user_action

        # Generate keyboard based on selected option
        if user_action == "video":
            keyboard = [
                [InlineKeyboardButton("Get Download Command", callback_data="get_command")],
                [InlineKeyboardButton("Back to Main Menu", callback_data="back_to_main_menu")]
            ]
        else:
            keyboard = [
                [InlineKeyboardButton("Download Directly", callback_data="direct_download")],
                [InlineKeyboardButton("Get Download Command", callback_data="get_command")],
                [InlineKeyboardButton("Back to Main Menu", callback_data="back_to_main_menu")]
            ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Would you like to download directly or get the command?", reply_markup=reply_markup)
        return

    # Step 2: Handle actions for download or command
    selected_option = context.user_data.get(user_id)
    if user_action == "get_command":
        command = {
            "video": f"yt-dlp --output 'downloads/{user_id}/%(id)s.%(ext)s' {video_link}",
            "image": f"yt-dlp --write-thumbnail --skip-download --output 'downloads/{user_id}/%(id)s.%(ext)s' {video_link}",
            "subtitles": f"yt-dlp --write-auto-sub --sub-lang ar --skip-download --output 'downloads/{user_id}/%(id)s.%(ext)s' {video_link}",
            "all": f"yt-dlp --write-auto-sub --sub-lang ar --write-thumbnail --output 'downloads/{user_id}/%(id)s.%(ext)s' {video_link}"
        }.get(selected_option, None)

        if command:
            await query.edit_message_text(f"Run the following command on your machine to download:\n\n`{command}`", parse_mode="Markdown")
        else:
            await query.edit_message_text("Invalid option selected.")
        return

    if user_action == "direct_download":
        await query.answer("Processing your request...")
        download_dir = f"downloads/{user_id}"
        os.makedirs(download_dir, exist_ok=True)

        try:
            commands = {
                "video": ['yt-dlp', '--output', f'{download_dir}/%(id)s.%(ext)s', video_link],
                "image": ['yt-dlp', '--write-thumbnail', '--skip-download', '--output', f'{download_dir}/%(id)s.%(ext)s', video_link],
                "subtitles": ['yt-dlp', '--write-auto-sub', '--sub-lang', 'ar', '--skip-download', '--output', f'{download_dir}/%(id)s.%(ext)s', video_link],
                "all": ['yt-dlp', '--write-auto-sub', '--sub-lang', 'ar', '--write-thumbnail', '--output', f'{download_dir}/%(id)s.%(ext)s', video_link]
            }.get(selected_option, None)

            if commands:
                process = await asyncio.create_subprocess_exec(*commands, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
                stdout, stderr = await process.communicate()
                if process.returncode != 0:
                    raise Exception(stderr.decode().strip())
                await query.edit_message_text("Download successful. Sending files...")
                for file_name in os.listdir(download_dir):
                    file_path = os.path.join(download_dir, file_name)
                    with open(file_path, 'rb') as f:
                        await context.bot.send_document(chat_id=query.message.chat_id, document=f)
            else:
                await query.edit_message_text("Invalid option selected.")
        except Exception as e:
            logger.exception("An error occurred during processing.")
            await query.edit_message_text(f"An unexpected error occurred: {e}")
        finally:
            shutil.rmtree(download_dir, ignore_errors=True)
        return

    if user_action == "back_to_main_menu":
        context.user_data[user_id] = None
        keyboard = [
            [InlineKeyboardButton("Download Video", callback_data="video")],
            [InlineKeyboardButton("Download Subtitles", callback_data="subtitles")],
            [InlineKeyboardButton("Download Thumbnail", callback_data="image")],
            [InlineKeyboardButton("Download All", callback_data="all")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("What would you like to download?", reply_markup=reply_markup)
        return

# Function to prompt the user for download options
async def fetch_thumbnail_and_subtitle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text.strip()
    if is_valid_youtube_url(user_message):
        user_requests[update.message.from_user.id] = user_message
        keyboard = [
            [InlineKeyboardButton("Download Video", callback_data="video")],
            [InlineKeyboardButton("Download Subtitles", callback_data="subtitles")],
            [InlineKeyboardButton("Download Thumbnail", callback_data="image")],
            [InlineKeyboardButton("Download All", callback_data="all")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("What would you like to download?", reply_markup=reply_markup)
    else:
        await update.message.reply_text("Please send a valid YouTube link.")

# Main function to set up the bot
def main() -> None:
    token = 'YOUR_API_TOCKEN'
    logging.basicConfig(level=logging.INFO)
    global logger
    logger = logging.getLogger(__name__)
    logger.info("Bot is starting...")

    application = Application.builder().token(token).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fetch_thumbnail_and_subtitle))
    application.add_handler(CallbackQueryHandler(handle_download_option))
    application.run_polling()

if __name__ == '__main__':
    main()
