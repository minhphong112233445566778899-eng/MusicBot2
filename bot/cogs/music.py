import discord
from discord.ext import commands
from discord import app_commands
import wavelink
from typing import cast
import asyncio

class CustomPlayer(wavelink.Player):
    """Custom player with autoplay support"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.autoplay_enabled = False
        self.queue = wavelink.Queue()

class Music(commands.Cog):
    """Music cog with Lavalink and Spotify support - Slash Commands"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEndEventPayload):
        """Handle track end and autoplay"""
        player = cast(CustomPlayer, payload.player)
        
        if player.autoplay_enabled and not player.queue:
            # Get recommended tracks based on current track
            try:
                recommended = await wavelink.Playable.search(
                    f"ytmsearch:{payload.track.title} {payload.track.author}"
                )
                if recommended:
                    track = recommended[0]
                    await player.play(track)
                    
                    # Send message to channel
                    channel = player.channel
                    if channel:
                        embed = discord.Embed(
                            title="🎵 Autoplay",
                            description=f"Now playing: **{track.title}**\nBy: {track.author}",
                            color=discord.Color.green()
                        )
                        await channel.send(embed=embed)
            except Exception as e:
                print(f"Autoplay error: {e}")
        
        elif player.queue:
            # Play next track from queue
            next_track = player.queue.get()
            await player.play(next_track)
    
    @app_commands.command(name="play", description="Play a song from YouTube or Spotify")
    @app_commands.describe(query="Song name or URL (YouTube/Spotify)")
    async def play(self, interaction: discord.Interaction, query: str):
        """Play a song from YouTube or Spotify URL/search"""
        # Check if user is in voice channel
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message(
                "❌ You need to be in a voice channel!",
                ephemeral=True
            )
            return
        
        # Check if Lavalink is connected
        if not wavelink.Pool.nodes:
            await interaction.response.send_message(
                "❌ Music system is not ready! Lavalink is not connected.\n"
                "Please contact the bot owner to configure Lavalink.",
                ephemeral=True
            )
            return
        
        # Defer response as search may take time
        await interaction.response.defer()
        
        try:
            # Use direct Discord voice connection
            print(f"🔗 Attempting to connect to {interaction.user.voice.channel.name}...")
            
            if not interaction.guild.voice_client:
                # Connect using Discord's built-in method
                try:
                    player = await interaction.user.voice.channel.connect(
    cls=CustomPlayer,
    self_deaf=True
)
                except asyncio.TimeoutError:
                    print("❌ Connection timed out")
                    await interaction.followup.send(
                        "❌ **Connection Timeout**: Discord voice servers not responding.\n"
                        "Try again in a few seconds."
                    )
                    return
                except discord.Forbidden:
                    print("❌ Permission denied")
                    await interaction.followup.send(
                        "❌ **Permission Denied**: Missing **Connect** or **Speak** permission"
                    )
                    return
                except Exception as e:
                    print(f"❌ Connection error: {type(e).__name__}: {e}")
                    await interaction.followup.send(
                        f"❌ **Connection Failed**: {type(e).__name__}"
                    )
                    return
            else:
                player = cast(CustomPlayer, interaction.guild.voice_client)
                print(f"ℹ️ Already connected")
            
            # Search for tracks
            print(f"🔍 Searching for: {query}")
            tracks = await wavelink.Playable.search(query)
            if not tracks:
                await interaction.followup.send("❌ No tracks found!")
                return
            
            track = tracks[0]
            print(f"📀 Found: {track.title}")
            
            if player.playing:
                # Add to queue
                player.queue.put(track)
                embed = discord.Embed(
                    title="📋 Added to Queue",
                    description=f"**{track.title}**\nBy: {track.author}",
                    color=discord.Color.blue()
                )
                embed.set_thumbnail(url=track.artwork)
                await interaction.followup.send(embed=embed)
            else:
                # Play immediately
                print(f"▶️ Playing: {track.title}")
                await player.play(track)
                embed = discord.Embed(
                    title="🎵 Now Playing",
                    description=f"**{track.title}**\nBy: {track.author}",
                    color=discord.Color.green()
                )
                embed.set_thumbnail(url=track.artwork)
                embed.add_field(name="Duration", value=f"{track.length // 60000}:{(track.length // 1000) % 60:02d}")
                await interaction.followup.send(embed=embed)
        
        except wavelink.LavalinkException as e:
            print(f"❌ Lavalink error: {e}")
            await interaction.followup.send(f"❌ **Lavalink Error**: {str(e)[:80]}")
        except Exception as e:
            print(f"❌ Error: {type(e).__name__}: {e}")
            await interaction.followup.send(f"❌ **Error**: {type(e).__name__}")
    
    @app_commands.command(name="pause", description="Pause the current track")
    async def pause(self, interaction: discord.Interaction):
        """Pause the current track"""
        player: CustomPlayer = cast(CustomPlayer, interaction.guild.voice_client)
        
        if not player:
            await interaction.response.send_message("❌ Not connected!", ephemeral=True)
            return
        
        if player.paused:
            await interaction.response.send_message("⏸️ Already paused!", ephemeral=True)
            return
        
        await player.pause(True)
        await interaction.response.send_message("⏸️ Paused!")
    
    @app_commands.command(name="resume", description="Resume the current track")
    async def resume(self, interaction: discord.Interaction):
        """Resume the current track"""
        player: CustomPlayer = cast(CustomPlayer, interaction.guild.voice_client)
        
        if not player:
            await interaction.response.send_message("❌ Not connected!", ephemeral=True)
            return
        
        if not player.paused:
            await interaction.response.send_message("▶️ Already playing!", ephemeral=True)
            return
        
        await player.pause(False)
        await interaction.response.send_message("▶️ Resumed!")
    
    @app_commands.command(name="skip", description="Skip the current track")
    async def skip(self, interaction: discord.Interaction):
        """Skip the current track"""
        player: CustomPlayer = cast(CustomPlayer, interaction.guild.voice_client)
        
        if not player:
            await interaction.response.send_message("❌ Not connected!", ephemeral=True)
            return
        
        if not player.playing:
            await interaction.response.send_message("❌ Nothing playing!", ephemeral=True)
            return
        
        await player.skip()
        await interaction.response.send_message("⏭️ Skipped!")
    
    @app_commands.command(name="stop", description="Stop playback and clear queue")
    async def stop(self, interaction: discord.Interaction):
        """Stop playback and clear the queue"""
        player: CustomPlayer = cast(CustomPlayer, interaction.guild.voice_client)
        
        if not player:
            await interaction.response.send_message("❌ Not connected!", ephemeral=True)
            return
        
        player.queue.clear()
        await player.stop()
        await interaction.response.send_message("⏹️ Stopped!")
    
    @app_commands.command(name="queue", description="Show the current queue")
    async def queue(self, interaction: discord.Interaction):
        """Show the current queue"""
        player: CustomPlayer = cast(CustomPlayer, interaction.guild.voice_client)
        
        if not player:
            await interaction.response.send_message("❌ Not connected!", ephemeral=True)
            return
        
        if not player.playing and not player.queue:
            await interaction.response.send_message("📋 Queue is empty!")
            return
        
        embed = discord.Embed(
            title="📋 Queue",
            color=discord.Color.blue()
        )
        
        if player.current:
            embed.add_field(
                name="Now Playing",
                value=f"**{player.current.title}**\nBy: {player.current.author}",
                inline=False
            )
        
        if player.queue:
            queue_list = "\n".join([
                f"{idx + 1}. **{track.title}** - {track.author}"
                for idx, track in enumerate(list(player.queue)[:10])
            ])
            embed.add_field(
                name=f"Up Next ({len(player.queue)} tracks)",
                value=queue_list,
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="nowplaying", description="Show currently playing track")
    async def nowplaying(self, interaction: discord.Interaction):
        """Show the currently playing track"""
        player: CustomPlayer = cast(CustomPlayer, interaction.guild.voice_client)
        
        if not player or not player.current:
            await interaction.response.send_message("❌ Nothing playing!", ephemeral=True)
            return
        
        track = player.current
        position = player.position
        duration = track.length
        
        # Create progress bar
        progress = int((position / duration) * 20) if duration > 0 else 0
        progress_bar = "▬" * progress + "🔘" + "▬" * (20 - progress)
        
        embed = discord.Embed(
            title="🎵 Now Playing",
            description=f"**{track.title}**",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=track.artwork)
        embed.add_field(name="Artist", value=track.author, inline=True)
        embed.add_field(
            name="Duration",
            value=f"{position // 60000}:{(position // 1000) % 60:02d} / {duration // 60000}:{(duration // 1000) % 60:02d}",
            inline=True
        )
        embed.add_field(name="Progress", value=progress_bar, inline=False)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="autoplay", description="Toggle autoplay on/off")
    async def autoplay(self, interaction: discord.Interaction):
        """Toggle autoplay on/off"""
        player: CustomPlayer = cast(CustomPlayer, interaction.guild.voice_client)
        
        if not player:
            await interaction.response.send_message("❌ Not connected!", ephemeral=True)
            return
        
        player.autoplay_enabled = not player.autoplay_enabled
        status = "enabled" if player.autoplay_enabled else "disabled"
        emoji = "✅" if player.autoplay_enabled else "❌"
        
        await interaction.response.send_message(f"{emoji} Autoplay {status}!")
    
    @app_commands.command(name="disconnect", description="Disconnect from voice channel")
    async def disconnect(self, interaction: discord.Interaction):
        """Disconnect from voice channel"""
        player: CustomPlayer = cast(CustomPlayer, interaction.guild.voice_client)
        
        if not player:
            await interaction.response.send_message("❌ Not connected!", ephemeral=True)
            return
        
        await player.disconnect()
        await interaction.response.send_message("👋 Disconnected!")
    
    @app_commands.command(name="help", description="Show bot commands")
    async def help_command(self, interaction: discord.Interaction):
        """Show bot commands"""
        embed = discord.Embed(
            title="🎵 Music Bot Commands",
            description="Discord music bot with Spotify & Lavalink",
            color=discord.Color.blue()
        )
        
        commands_list = [
            ("</play:0>", "Play a song"),
            ("</pause:0>", "Pause"),
            ("</resume:0>", "Resume"),
            ("</skip:0>", "Skip"),
            ("</stop:0>", "Stop"),
            ("</queue:0>", "Show queue"),
            ("</nowplaying:0>", "Now playing"),
            ("</autoplay:0>", "Toggle autoplay"),
            ("</disconnect:0>", "Disconnect"),
            ("</status:0>", "Bot status"),
        ]
        
        for cmd, desc in commands_list:
            embed.add_field(name=cmd, value=desc, inline=False)
        
        embed.set_footer(text="💡 Use /status to check permissions!")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="status", description="Check bot and Lavalink status")
    async def status(self, interaction: discord.Interaction):
        """Check bot and Lavalink status"""
        embed = discord.Embed(
            title="🤖 Bot Status",
            color=discord.Color.blue()
        )
        
        # Lavalink status
        if wavelink.Pool.nodes:
            node = wavelink.Pool.nodes[0]
            embed.add_field(
                name="🎵 Lavalink",
                value=f"✅ Connected\nPlayers: {len(node.players)}",
                inline=True
            )
        else:
            embed.add_field(
                name="🎵 Lavalink",
                value="❌ Not connected",
                inline=True
            )
        
        # Voice connection
        if interaction.guild.voice_client:
            player = cast(CustomPlayer, interaction.guild.voice_client)
            embed.add_field(
                name="🔊 Voice",
                value=f"✅ Connected to {player.channel.name}",
                inline=True
            )
        else:
            embed.add_field(
                name="🔊 Voice",
                value="❌ Not connected",
                inline=True
            )
        
        # Bot info
        embed.add_field(
            name="📊 Bot Info",
            value=f"Servers: {len(self.bot.guilds)}\nPing: {round(self.bot.latency * 1000)}ms",
            inline=True
        )
        
        # Permissions check
        if interaction.user.voice and interaction.user.voice.channel:
            voice_channel = interaction.user.voice.channel
            bot_member = interaction.guild.me
            permissions = voice_channel.permissions_for(bot_member)
            
            perm_check = f"Connect: {'✅' if permissions.connect else '❌'}\nSpeak: {'✅' if permissions.speak else '❌'}"
            
            embed.add_field(
                name="🔐 Permissions",
                value=perm_check,
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))
