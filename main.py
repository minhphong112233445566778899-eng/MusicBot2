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
        
        super().__init__(
            command_prefix='/',  # Changed but slash commands don't use this
            intents=intents,
            help_command=None
        )
    
    async def setup_hook(self):
        # Load music cog
        await self.load_extension('bot.cogs.music')
        
        # Connect to Lavalink
        nodes = [
            wavelink.Node(
                uri=os.getenv('LAVALINK_URI', 'http://127.0.0.1:2333'),
                password=os.getenv('LAVALINK_PASSWORD', 'youshallnotpass'),
                identifier='main'
            )
        ]
        
        await wavelink.Pool.connect(nodes=nodes, client=self)
        print(f'Connected to Lavalink node(s)')
    
    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
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
        print(f'Lavalink node {payload.node.identifier} is ready!')

bot = MusicBot()

if __name__ == '__main__':
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print('ERROR: DISCORD_TOKEN not found in environment variables!')
        exit(1)
    
    bot.run(token)     print('ERROR: DISCORD_TOKEN not found in environment variables!')
        exit(1)
    
    bot.run(token)