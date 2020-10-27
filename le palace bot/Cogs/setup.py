import discord
import asyncio
import json

from discord.ext import commands
from discord.utils import get
from discord.ext.commands import has_permissions

# ------------------------ COGS ------------------------ #  

class SetupCog(commands.Cog, name="setup command"):
    def __init__(self, bot):
        self.bot = bot

# ------------------------------------------------------ #  

    @commands.command(name = 'setup')
    @has_permissions(administrator = True)
    async def setup (self, ctx, onOrOff):

        onOrOff = onOrOff.lower()

        if onOrOff == "on":
            embed = discord.Embed(title = f"**ARE YOU SURE DO YOU WANT TO SET UP THE CAPTCHA PROTECTION ?**", description = f"**Set up the captcha protection includes the creation of :**\n\n- captcha verification channel\n- log channel\n- temporary role (before that the captcha was passed)\n\n**If you want to set up the captcha protection write \"__yes__\" else write \"__no__\".**", color = 0xff0000)
            await ctx.channel.send(embed = embed)
            # Ask if user are sure
            def check(message):
                if message.author == ctx.author:
                    if ((message.content == "yes") or (message.content == "no")):
                        return message.content

            try:
                msg = await self.bot.wait_for('message', timeout=30.0, check=check)
                if msg.content == "no":
                    await ctx.channel.send("The set up of the captcha protection was abandoned.")
                else:
                    loading = await ctx.channel.send("Creation of captcha protection...")
                    # Create role
                    temporaryRole = await ctx.guild.create_role(name="untested")
                    # Hide all channels
                    for channel in ctx.guild.channels:
                        if isinstance(channel, discord.TextChannel):
                            await channel.set_permissions(temporaryRole, read_messages=False)
                        elif isinstance(channel, discord.VoiceChannel):
                            await channel.set_permissions(temporaryRole, read_messages=False, connect=False)
                    # Create captcha channel
                    captchaChannel = await ctx.guild.create_text_channel('verification')
                    await captchaChannel.set_permissions(temporaryRole, read_messages=True, send_messages=True)
                    await captchaChannel.set_permissions(ctx.guild.default_role, read_messages=False)
                    await captchaChannel.edit(slowmode_delay= 5)
                    # Create log channel
                    logChannel = await ctx.guild.create_text_channel('captcha-logs')
                    await logChannel.set_permissions(ctx.guild.default_role, read_messages=False)

                    # Edit configuration.json
                    with open("configuration.json", "r") as config:
                        data = json.load(config)
                        # Add modifications
                        data["captcha"] = True
                        data["temporaryRole"] = temporaryRole.id
                        data["captchaChannel"] = captchaChannel.id
                        data["logChannel"] = logChannel.id
                        newdata = json.dumps(data, indent=4, ensure_ascii=False)

                    with open("configuration.json", "w") as config:
                        config.write(newdata)
                    
                    await loading.delete()
                    embed = discord.Embed(title = f"**CAPTCHA WAS SET UP WITH SUCCESS**", description = f"The captcha was set up with success.", color = 0x2fa737) # Green
                    await ctx.channel.send(embed = embed)

            
            except (asyncio.TimeoutError):
                embed = discord.Embed(title = f"**TIME IS OUT**", description = f"{ctx.author.mention} has exceeded the response time (30s).", color = 0xff0000)
                await ctx.channel.send(embed = embed)

        elif onOrOff == "off":
            loading = await ctx.channel.send("Deletion of captcha protection...")
            with open("configuration.json", "r") as config:
                data = json.load(config)
                # Add modifications
                data["captcha"] = False
                newdata = json.dumps(data, indent=4, ensure_ascii=False)
            
            # Delete all
            temporaryRole = get(ctx.guild.roles, id= data["temporaryRole"])
            await temporaryRole.delete()
            captchaChannel = self.bot.get_channel(data["captchaChannel"])
            await captchaChannel.delete()
            logChannel = self.bot.get_channel(data["logChannel"])
            await logChannel.delete()

            # Edit configuration.json
            with open("configuration.json", "w") as config:
                config.write(newdata)
            
            await loading.delete()
            embed = discord.Embed(title = f"**CAPTCHA WAS DELETED WITH SUCCESS**", description = f"The captcha was deleted with success.", color = 0x2fa737) # Green
            await ctx.channel.send(embed = embed)

        else:
            embed = discord.Embed(title=f"**ERROR**", description=f"The setup argument must be on or off\nFollow the example : ``{self.bot.command_prefix}setup <on/off>``", color=0xe00000) # Red
            embed.set_footer(text="Bot Created by Darkempire#8245")
            return await ctx.channel.send(embed=embed)

# ------------------------ BOT ------------------------ #  

def setup(bot):
    bot.add_cog(SetupCog(bot))