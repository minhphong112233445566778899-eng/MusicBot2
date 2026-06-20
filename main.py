import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

class MusicBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.guilds = True
        intents.voice_states = True
        intents.message_content = True

        super().__init__(
            command_prefix="/",
            intents=intents,
            help_command=None
        )

    async def setup_hook(self):
        try:
            await self.tree.sync()
            print("✅ Slash commands synced!")
        except Exception as e:
            print(f"❌ Sync failed: {e}")

    async def on_ready(self):
        print(f"Logged in as {self.user}")
        print(f"Connected to {len(self.guilds)} guild(s)")


bot = MusicBot()


@bot.tree.command(name="join", description="Join your voice channel")
async def join(interaction: discord.Interaction):
    if not interaction.user.voice:
        await interaction.response.send_message(
            "You must join a voice channel first.",
            ephemeral=True
        )
        return

    channel = interaction.user.voice.channel

    try:
        if interaction.guild.voice_client:
            await interaction.guild.voice_client.move_to(channel)
        else:
            await channel.connect()

        await interaction.response.send_message(
            f"Joined **{channel.name}**"
        )

    except Exception as e:
        await interaction.response.send_message(
            f"Voice connection failed: {e}",
            ephemeral=True
        )


@bot.tree.command(name="leave", description="Leave the voice channel")
async def leave(interaction: discord.Interaction):
    vc = interaction.guild.voice_client

    if not vc:
        await interaction.response.send_message(
            "I'm not in a voice channel.",
            ephemeral=True
        )
        return

    await vc.disconnect()
    await interaction.response.send_message("Disconnected.")


token = os.getenv("DISCORD_TOKEN")

if not token:
    print("❌ DISCORD_TOKEN missing")
else:
    bot.run(token)
