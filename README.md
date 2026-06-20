# Discord Music Bot

A feature-rich Discord music bot with Spotify support powered by Lavalink and discord.py.

## Features

- 🎵 Play music from YouTube and Spotify
- 📋 Queue management
- ⏯️ Playback controls (play, pause, resume, skip, stop)
- 🔄 Autoplay functionality
- 🎨 Rich embeds with track information
- 💎 High-quality audio with Lavalink

## Commands

| Command | Description |
|---------|-------------|
| `!play <song/url>` | Play a song from YouTube or Spotify |
| `!pause` | Pause the current track |
| `!resume` | Resume the current track |
| `!skip` | Skip the current track |
| `!stop` | Stop playback and clear queue |
| `!queue` | Show the current queue |
| `!nowplaying` or `!np` | Show currently playing track |
| `!autoplay` | Toggle autoplay on/off |
| `!disconnect` or `!dc` | Disconnect from voice channel |
| `!help` | Show all commands |

## Setup

### Prerequisites

1. **Discord Bot Token**
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Create a new application
   - Go to "Bot" section and create a bot
   - Copy the bot token
   - Enable "Message Content Intent" and "Server Members Intent" under Privileged Gateway Intents

2. **Lavalink Server**
   - You need a running Lavalink server
   - Option 1: Use a public Lavalink server (search for "public lavalink servers")
   - Option 2: Host your own Lavalink server (see [Lavalink Setup](#lavalink-setup))

3. **Spotify API (Optional)**
   - Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - Create an app
   - Copy Client ID and Client Secret
   - Add these to `application.yml` in your Lavalink server

### Installation

1. Clone the repository:
```bash
git clone https://github.com/minhphong112233445566778899-eng/MusicBot2.git
cd MusicBot2
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file:
```bash
cp .env.example .env
```

4. Edit `.env` and add your credentials:
```env
DISCORD_TOKEN=your_discord_bot_token
LAVALINK_URI=http://127.0.0.1:2333
LAVALINK_PASSWORD=youshallnotpass
```

5. Run the bot:
```bash
python main.py
```

## Lavalink Setup

### Local Setup

1. Download Lavalink.jar from [Lavalink releases](https://github.com/lavalink-devs/Lavalink/releases)

2. Copy `application.yml` to the same directory as Lavalink.jar

3. If using Spotify, edit `application.yml` and add your Spotify credentials:
```yaml
plugins:
  lavasrc:
    spotify:
      clientId: "your_spotify_client_id"
      clientSecret: "your_spotify_client_secret"
```

4. Run Lavalink:
```bash
java -jar Lavalink.jar
```

### Using Docker

```bash
docker run -d \
  --name lavalink \
  -p 2333:2333 \
  -v $(pwd)/application.yml:/opt/Lavalink/application.yml \
  ghcr.io/lavalink-devs/lavalink:latest
```

## Railway Deployment

1. Fork this repository to your GitHub account

2. Go to [Railway](https://railway.app/) and create a new project

3. Connect your GitHub repository

4. Add environment variables in Railway dashboard:
   - `DISCORD_TOKEN`: Your Discord bot token
   - `LAVALINK_URI`: Your Lavalink server URI (use a public one or host your own)
   - `LAVALINK_PASSWORD`: Your Lavalink server password

5. Deploy!

### Railway with Self-Hosted Lavalink

For the best experience, deploy Lavalink on Railway as well:

1. Create a new Railway service from the Lavalink Docker image
2. Upload your `application.yml` with Spotify credentials
3. Use the internal Railway URL for `LAVALINK_URI` in your bot

## Troubleshooting

### Bot not responding
- Make sure the bot has proper permissions in your Discord server
- Check that "Message Content Intent" is enabled in Discord Developer Portal
- Verify the bot token is correct

### Music not playing
- Ensure Lavalink server is running and accessible
- Check Lavalink credentials in `.env` match your server
- Verify you're in a voice channel when using commands

### Spotify links not working
- Make sure LavaSrc plugin is installed in Lavalink
- Verify Spotify credentials in `application.yml`
- Check Lavalink logs for Spotify-related errors

## Tech Stack

- **discord.py 2.3.2** - Discord bot framework
- **Wavelink 3.4.1** - Lavalink client for Python
- **Lavalink v4+** - Audio delivery system
- **LavaSrc Plugin** - Spotify, Apple Music support

## Contributing

Feel free to open issues or submit pull requests!

## License

MIT License - feel free to use this project however you like!