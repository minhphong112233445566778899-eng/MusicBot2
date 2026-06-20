import discord
from discord.ext import commands
from discord import app_commands
import wavelink
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

class MusicBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.voice_states = True
        intents.guilds = True  # ✅ ADDED - needed for guild info
        intents.members = True  # ✅ ADDED - needed for member voice states
        
        super().__init__(
            command_prefix='/',  # Changed but slash commands don't use this
            intents=intents,
            help_command=None
        )
    
    async def setup_hook(self):
        # Load music cog
        await self.load_extension('bot.cogs.music')
        
        # Sync slash commands FIRST (before Lavalink connection)
        try:
            await self.tree.sync()
            print('✅ Slash commands synced!')
        except Exception as e:
            print(f'❌ Failed to sync slash commands: {e}')
        
        # Connect to Lavalink (don't block bot if it fails)
        try:
            lavalink_uri = os.getenv('LAVALINK_URI', 'http://127.0.0.1:2333')
            
            # Ensure URI has http:// or https://
            if not lavalink_uri.startswith(('http://', 'https://')):
                lavalink_uri = f'http://{lavalink_uri}'
                print(f'⚠️  Added http:// to Lavalink URI: {lavalink_uri}')
            
            nodes = [
                wavelink.Node(
                    uri=lavalink_uri,
                    password=os.getenv('LAVALINK_PASSWORD', 'youshallnotpass'),
                    identifier='main'
                )
            ]
            
            await wavelink.Pool.connect(nodes=nodes, client=self)
            print(f'✅ Connected to Lavalink!')
        except Exception as e:
            print(f'⚠️  Failed to connect to Lavalink: {e}')
            print(f'⚠️  Bot will start but music commands won\'t work until Lavalink is configured')
    
    async def on_ready(self):
        print(f'Logged in as {self.bot.user} (ID: {self.bot.user.id})')
        print(f'Connected to {len(self.guilds)} guild(s)')
        print('------')
        
        # Set bot status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name="/help | Music"
            )
        )
    
    async def on_wavelink_node_ready(self, payload: wavelink.NodeReadyEventPayload):
        print(f'✅ Lavalink node {payload.node.identifier} is ready!')

bot = MusicBot()

if __name__ == '__main__':
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print('ERROR: DISCORD_TOKEN not found in environment variables!')
        exit(1)
    
    bot.run(token)
