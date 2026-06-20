import discord
from discord.ext import commands
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
    """Music cog with Lavalink and Spotify support"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    async def get_player(self, interaction: discord.Interaction) -> CustomPlayer:
        """Get or create a player for the guild"""
        if not interaction.guild.voice_client:
            player = await interaction.user.voice.channel.connect(cls=CustomPlayer)
        else:
            player = cast(CustomPlayer, interaction.guild.voice_client)
        return player
    
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
    
    @commands.hybrid_command(name="play", description="Play a song from YouTube or Spotify")
    async def play(self, ctx: commands.Context, *, query: str):
        """Play a song from YouTube or Spotify URL/search"""
        if not ctx.author.voice:
            await ctx.send("❌ You need to be in a voice channel!")
            return
        
        # Defer response as search may take time
        await ctx.defer()
        
        # Get or create player
        if not ctx.guild.voice_client:
            player: CustomPlayer = await ctx.author.voice.channel.connect(cls=CustomPlayer)
        else:
            player = cast(CustomPlayer, ctx.guild.voice_client)
        
        # Search for tracks
        try:
            tracks = await wavelink.Playable.search(query)
            if not tracks:
                await ctx.send("❌ No tracks found!")
                return
            
            track = tracks[0]
            
            if player.playing:
                # Add to queue
                player.queue.put(track)
                embed = discord.Embed(
                    title="📋 Added to Queue",
                    description=f"**{track.title}**\nBy: {track.author}",
                    color=discord.Color.blue()
                )
                embed.set_thumbnail(url=track.artwork)
                await ctx.send(embed=embed)
            else:
                # Play immediately
                await player.play(track)
                embed = discord.Embed(
                    title="🎵 Now Playing",
                    description=f"**{track.title}**\nBy: {track.author}",
                    color=discord.Color.green()
                )
                embed.set_thumbnail(url=track.artwork)
                embed.add_field(name="Duration", value=f"{track.length // 60000}:{(track.length // 1000) % 60:02d}")
                await ctx.send(embed=embed)
        
        except Exception as e:
            await ctx.send(f"❌ Error playing track: {str(e)}")
    
    @commands.hybrid_command(name="pause", description="Pause the current track")
    async def pause(self, ctx: commands.Context):
        """Pause the current track"""
        player: CustomPlayer = cast(CustomPlayer, ctx.guild.voice_client)
        
        if not player:
            await ctx.send("❌ Not connected to a voice channel!")
            return
        
        if player.paused:
            await ctx.send("⏸️ Already paused!")
            return
        
        await player.pause(True)
        await ctx.send("⏸️ Paused!")
    
    @commands.hybrid_command(name="resume", description="Resume the current track")
    async def resume(self, ctx: commands.Context):
        """Resume the current track"""
        player: CustomPlayer = cast(CustomPlayer, ctx.guild.voice_client)
        
        if not player:
            await ctx.send("❌ Not connected to a voice channel!")
            return
        
        if not player.paused:
            await ctx.send("▶️ Already playing!")
            return
        
        await player.pause(False)
        await ctx.send("▶️ Resumed!")
    
    @commands.hybrid_command(name="skip", description="Skip the current track")
    async def skip(self, ctx: commands.Context):
        """Skip the current track"""
        player: CustomPlayer = cast(CustomPlayer, ctx.guild.voice_client)
        
        if not player:
            await ctx.send("❌ Not connected to a voice channel!")
            return
        
        if not player.playing:
            await ctx.send("❌ Nothing is playing!")
            return
        
        await player.skip()
        await ctx.send("⏭️ Skipped!")
    
    @commands.hybrid_command(name="stop", description="Stop playback and clear the queue")
    async def stop(self, ctx: commands.Context):
        """Stop playback and clear the queue"""
        player: CustomPlayer = cast(CustomPlayer, ctx.guild.voice_client)
        
        if not player:
            await ctx.send("❌ Not connected to a voice channel!")
            return
        
        player.queue.clear()
        await player.stop()
        await ctx.send("⏹️ Stopped and cleared queue!")
    
    @commands.hybrid_command(name="queue", description="Show the current queue")
    async def queue(self, ctx: commands.Context):
        """Show the current queue"""
        player: CustomPlayer = cast(CustomPlayer, ctx.guild.voice_client)
        
        if not player:
            await ctx.send("❌ Not connected to a voice channel!")
            return
        
        if not player.playing and not player.queue:
            await ctx.send("📋 Queue is empty!")
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
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="nowplaying", aliases=["np"], description="Show the currently playing track")
    async def nowplaying(self, ctx: commands.Context):
        """Show the currently playing track"""
        player: CustomPlayer = cast(CustomPlayer, ctx.guild.voice_client)
        
        if not player or not player.current:
            await ctx.send("❌ Nothing is playing!")
            return
        
        track = player.current
        position = player.position
        duration = track.length
        
        # Create progress bar
        progress = int((position / duration) * 20)
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
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="autoplay", description="Toggle autoplay on/off")
    async def autoplay(self, ctx: commands.Context):
        """Toggle autoplay on/off"""
        player: CustomPlayer = cast(CustomPlayer, ctx.guild.voice_client)
        
        if not player:
            await ctx.send("❌ Not connected to a voice channel!")
            return
        
        player.autoplay_enabled = not player.autoplay_enabled
        status = "enabled" if player.autoplay_enabled else "disabled"
        emoji = "✅" if player.autoplay_enabled else "❌"
        
        await ctx.send(f"{emoji} Autoplay {status}!")
    
    @commands.hybrid_command(name="disconnect", aliases=["dc", "leave"], description="Disconnect from voice channel")
    async def disconnect(self, ctx: commands.Context):
        """Disconnect from voice channel"""
        player: CustomPlayer = cast(CustomPlayer, ctx.guild.voice_client)
        
        if not player:
            await ctx.send("❌ Not connected to a voice channel!")
            return
        
        await player.disconnect()
        await ctx.send("👋 Disconnected!")
    
    @commands.hybrid_command(name="help", description="Show bot commands")
    async def help_command(self, ctx: commands.Context):
        """Show bot commands"""
        embed = discord.Embed(
            title="🎵 Music Bot Commands",
            description="A Discord music bot with Spotify and Lavalink support",
            color=discord.Color.blue()
        )
        
        commands_list = [
            ("!play <song/url>", "Play a song from YouTube or Spotify"),
            ("!pause", "Pause the current track"),
            ("!resume", "Resume the current track"),
            ("!skip", "Skip the current track"),
            ("!stop", "Stop playback and clear queue"),
            ("!queue", "Show the current queue"),
            ("!nowplaying", "Show currently playing track"),
            ("!autoplay", "Toggle autoplay on/off"),
            ("!disconnect", "Disconnect from voice channel"),
        ]
        
        for cmd, desc in commands_list:
            embed.add_field(name=cmd, value=desc, inline=False)
        
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))