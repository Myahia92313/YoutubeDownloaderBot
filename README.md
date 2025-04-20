# YouTube Download Bot for Telegram

This repository contains a feature-rich Telegram bot that allows users to download YouTube videos, subtitles, thumbnails, or all content effortlessly. Built using the `python-telegram-bot` library and `yt-dlp`, this bot provides both direct downloads and the option to generate download commands for manual execution.

## Features

- **Multi-Option Downloading**:
  - Download YouTube videos, thumbnails, subtitles (auto-generated, Arabic), or all.
- **User-Friendly Interface**:
  - Inline keyboard navigation for smooth interaction.
- **Direct Downloads or Command Sharing**:
  - Choose between downloading files directly or receiving `yt-dlp` commands for use on your system.
- **Robust Error Handling**:
  - Handles invalid inputs and unexpected errors gracefully.
- **Resource Cleanup**:
  - Ensures temporary files are cleaned up after processing.

## Requirements

- Python 3.8 or higher
- Telegram Bot API Token
- Libraries:
  - `python-telegram-bot`
  - `yt-dlp`

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/youtube-download-bot.git
   cd youtube-download-bot
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your Telegram Bot:
   - Obtain a bot token from [BotFather](https://core.telegram.org/bots#botfather) on Telegram.
   - Store the token securely in an environment variable or a configuration file.

4. Run the bot:
   ```bash
   python bot.py
   ```

## Usage

1. Start the bot on Telegram.
2. Send a valid YouTube URL to the bot.
3. Select what you want to download (video, thumbnail, subtitles, or all).
4. Follow the prompts to download the files directly or receive the download commands.

## File Structure

```
youtube-download-bot/
├── Script.py         # Main bot script
├── requirements.txt  # List of dependencies
└── README.md     # Project documentation
```

## Disclaimer

This bot is intended for educational and personal use only. Ensure you comply with YouTube's Terms of Service when using this bot.

