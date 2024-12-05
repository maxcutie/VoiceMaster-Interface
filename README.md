# Discord Voice Master Bot

A Discord bot that provides a comprehensive interface for managing voice channels with various controls and features.

## Features

- 🔒 Lock/Unlock voice channels
- 👻 Hide/Reveal voice channels
- 🎤 Claim ownership of voice channels
- 🔨 Disconnect members
- 🖥️ Start voice channel activities
- ℹ️ View channel information
- ➕➖ Adjust user limits

## Setup Instructions

1. Create a Discord Application and Bot:
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Create a new application
   - Go to the "Bot" section and create a bot
   - Copy the bot token

2. Configure the bot:
   - Rename `.env.example` to `.env`
   - Replace `your_bot_token_here` with your actual bot token

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the bot:
   ```bash
   python bot.py
   ```

5. Invite the bot to your server:
   - Go to OAuth2 > URL Generator in the Discord Developer Portal
   - Select the following scopes:
     - `bot`
     - `applications.commands`
   - Select the following permissions:
     - `Manage Channels`
     - `Move Members`
     - `View Channels`
     - `Send Messages`
   - Use the generated URL to invite the bot to your server

## Usage

1. Join a voice channel
2. Type `/voicemaster` to bring up the control interface
3. Use the buttons to control various aspects of your voice channel

## Required Bot Permissions

- Manage Channels
- Move Members
- View Channels
- Send Messages
- Use Slash Commands 