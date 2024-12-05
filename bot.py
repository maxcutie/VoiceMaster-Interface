import os
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
VOICE_MASTER_CHANNEL_ID = 1314167695914041435

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

class VoiceControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def get_voice_channel(self, interaction: discord.Interaction):
        if not interaction.user.voice:
            await interaction.response.send_message("You must be in a voice channel to use this!", ephemeral=True)
            return None
        return interaction.user.voice.channel

    @discord.ui.button(emoji="🔒", style=discord.ButtonStyle.grey)
    async def lock_channel(self, interaction: discord.Interaction, button: discord.ui.Button):
        voice_channel = await self.get_voice_channel(interaction)
        if not voice_channel:
            return
        overwrites = voice_channel.overwrites
        overwrites[interaction.guild.default_role] = discord.PermissionOverwrite(connect=False)
        await voice_channel.edit(overwrites=overwrites)
        await interaction.response.send_message("Voice channel locked! 🔒", ephemeral=True)

    @discord.ui.button(emoji="🔓", style=discord.ButtonStyle.grey)
    async def unlock_channel(self, interaction: discord.Interaction, button: discord.ui.Button):
        voice_channel = await self.get_voice_channel(interaction)
        if not voice_channel:
            return
        overwrites = voice_channel.overwrites
        overwrites[interaction.guild.default_role] = discord.PermissionOverwrite(connect=True)
        await voice_channel.edit(overwrites=overwrites)
        await interaction.response.send_message("Voice channel unlocked! 🔓", ephemeral=True)

    @discord.ui.button(emoji="👻", style=discord.ButtonStyle.grey)
    async def ghost_channel(self, interaction: discord.Interaction, button: discord.ui.Button):
        voice_channel = await self.get_voice_channel(interaction)
        if not voice_channel:
            return
        overwrites = voice_channel.overwrites
        overwrites[interaction.guild.default_role] = discord.PermissionOverwrite(view_channel=False)
        await voice_channel.edit(overwrites=overwrites)
        await interaction.response.send_message("Voice channel hidden! 👻", ephemeral=True)

    @discord.ui.button(emoji="👁️", style=discord.ButtonStyle.grey)
    async def reveal_channel(self, interaction: discord.Interaction, button: discord.ui.Button):
        voice_channel = await self.get_voice_channel(interaction)
        if not voice_channel:
            return
        overwrites = voice_channel.overwrites
        overwrites[interaction.guild.default_role] = discord.PermissionOverwrite(view_channel=True)
        await voice_channel.edit(overwrites=overwrites)
        await interaction.response.send_message("Voice channel revealed! 👁️", ephemeral=True)

    @discord.ui.button(emoji="🎤", style=discord.ButtonStyle.grey)
    async def claim_channel(self, interaction: discord.Interaction, button: discord.ui.Button):
        voice_channel = await self.get_voice_channel(interaction)
        if not voice_channel:
            return
        
        # Get the user's display name (nickname if set, otherwise username)
        display_name = interaction.user.display_name
        
        try:
            # Update channel name and permissions
            await voice_channel.edit(
                name=f"{display_name}'s Channel",
                overwrites={
                    interaction.guild.default_role: discord.PermissionOverwrite(connect=True, view_channel=True),
                    interaction.user: discord.PermissionOverwrite(manage_channels=True, manage_permissions=True)
                }
            )
            await interaction.response.send_message(f"You now own this voice channel! 🎤\nChannel renamed to: {display_name}'s Channel", ephemeral=True)
        except discord.HTTPException as e:
            await interaction.response.send_message("Failed to claim the channel. Please try again.", ephemeral=True)
            print(f"Error claiming channel: {e}")

    @discord.ui.button(emoji="🔨", style=discord.ButtonStyle.grey)
    async def disconnect_member(self, interaction: discord.Interaction, button: discord.ui.Button):
        voice_channel = await self.get_voice_channel(interaction)
        if not voice_channel:
            return
        modal = DisconnectModal(voice_channel)
        await interaction.response.send_modal(modal)

    @discord.ui.button(emoji="🖥️", style=discord.ButtonStyle.grey)
    async def start_activity(self, interaction: discord.Interaction, button: discord.ui.Button):
        voice_channel = await self.get_voice_channel(interaction)
        if not voice_channel:
            return
        try:
            # Watch Together application ID
            WATCH_TOGETHER_ID = 880218394199220334
            
            invite = await voice_channel.create_invite(
                target_type=discord.InviteTarget.embedded_application,
                target_application_id=WATCH_TOGETHER_ID,
                max_age=3600  # 1 hour
            )
            await interaction.response.send_message(f"Click to start Watch Together: {invite.url}", ephemeral=True)
        except discord.HTTPException:
            await interaction.response.send_message("Failed to create activity. Please try again.", ephemeral=True)

    @discord.ui.button(emoji="ℹ️", style=discord.ButtonStyle.grey)
    async def channel_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        voice_channel = await self.get_voice_channel(interaction)
        if not voice_channel:
            return
        embed = discord.Embed(title="Channel Information", color=discord.Color.blue())
        embed.add_field(name="Channel Name", value=voice_channel.name)
        embed.add_field(name="User Limit", value=str(voice_channel.user_limit) if voice_channel.user_limit else "No limit")
        embed.add_field(name="Current Users", value=str(len(voice_channel.members)))
        embed.add_field(name="Bitrate", value=f"{voice_channel.bitrate//1000}kbps")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(emoji="➕", style=discord.ButtonStyle.grey)
    async def increase_limit(self, interaction: discord.Interaction, button: discord.ui.Button):
        voice_channel = await self.get_voice_channel(interaction)
        if not voice_channel:
            return
        current_limit = voice_channel.user_limit
        new_limit = min(99, (current_limit or 0) + 1)
        await voice_channel.edit(user_limit=new_limit)
        await interaction.response.send_message(f"User limit increased to {new_limit}! ➕", ephemeral=True)

    @discord.ui.button(emoji="➖", style=discord.ButtonStyle.grey)
    async def decrease_limit(self, interaction: discord.Interaction, button: discord.ui.Button):
        voice_channel = await self.get_voice_channel(interaction)
        if not voice_channel:
            return
        current_limit = voice_channel.user_limit
        if current_limit is None or current_limit <= 0:
            await interaction.response.send_message("User limit is already at minimum!", ephemeral=True)
            return
        new_limit = max(0, current_limit - 1)
        await voice_channel.edit(user_limit=new_limit)
        await interaction.response.send_message(f"User limit decreased to {new_limit}! ➖", ephemeral=True)

class DisconnectModal(discord.ui.Modal, title="Disconnect Member"):
    member_name = discord.ui.TextInput(
        label="Member Name",
        placeholder="Enter the member's name",
        required=True
    )

    def __init__(self, voice_channel: discord.VoiceChannel):
        super().__init__()
        self.voice_channel = voice_channel

    async def on_submit(self, interaction: discord.Interaction):
        member_to_disconnect = discord.utils.get(
            self.voice_channel.members,
            name=self.member_name.value
        )
        if member_to_disconnect:
            await member_to_disconnect.move_to(None)
            await interaction.response.send_message(f"Disconnected {member_to_disconnect.name}! 🔨", ephemeral=True)
        else:
            await interaction.response.send_message("Member not found in the voice channel!", ephemeral=True)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    try:
        # Get the voice master channel
        channel = bot.get_channel(VOICE_MASTER_CHANNEL_ID)
        if channel:
            # Clear existing messages in the channel
            async for message in channel.history(limit=100):
                await message.delete()
            
            # Create and send the new interface
            embed = discord.Embed(
                title="VoiceMaster Interface",
                description="Click the buttons below to control your voice channel",
                color=discord.Color.blue()
            )
            
            embed.add_field(name="Button Usage", value="""
            🔒 — Lock the voice channel
            🔓 — Unlock the voice channel
            👻 — Ghost the voice channel
            👁️ — Reveal the voice channel
            🎤 — Claim the voice channel
            🔨 — Disconnect a member
            🖥️ — Start an activity
            ℹ️ — View channel information
            ➕ — Increase the user limit
            ➖ — Decrease the user limit
            """)
            
            view = VoiceControlView()
            await channel.send(embed=embed, view=view)
            print("Voice master interface has been set up!")
    except Exception as e:
        print(f"Error setting up voice master interface: {e}")

# Remove the slash command since we're using automatic channel setup
# Run the bot
bot.run(TOKEN) 