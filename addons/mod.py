import discord
import json
import re
from inspect import cleandoc
from random import randint, choice
from discord.ext import commands
from subprocess import call
from sys import argv
import time

class Mod:
    """
    Staff commands.
    """
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))

    async def add_restriction(self, member, rst):
        with open("data/restrictions.json", "r") as f:
            rsts = json.load(f)
        if member.id not in rsts:
            rsts[member.id] = []
        if rst not in rsts[member.id]:
            rsts[member.id].append(rst)
        with open("data/restrictions.json", "w") as f:
            json.dump(rsts, f)

    async def remove_restriction(self, member, rst):
        with open("data/restrictions.json", "r") as f:
            rsts = json.load(f)
        if member.id not in rsts:
            rsts[member.id] = []
        if rst in rsts[member.id]:
            rsts[member.id].remove(rst)
        with open("data/restrictions.json", "w") as f:
            json.dump(rsts, f)

    @commands.command(pass_context=True, hidden=True)
    async def quit(self, ctx):
        """Stops the bot."""
        issuer = ctx.message.author
        if (self.bot.bot_management_role not in issuer.roles) and ((self.bot.owner_role not in issuer.roles)):
            msg = "{} This command is limited to wizards.".format(issuer.mention)
            await self.bot.say(msg)
            return
        await self.bot.say("👋 Bye bye!")
        await self.bot.close()

    @commands.command(pass_context=True, hidden=True)
    async def pull(self, ctx):
        """Pull new changes from GitHub and restart."""
        issuer = ctx.message.author
        if (self.bot.bot_management_role not in issuer.roles) and ((self.bot.owner_role not in issuer.roles)):
            msg = "{} This command is limited to wizards.".format(issuer.mention)
            await self.bot.say(msg)
            return
        await self.bot.say("Pulling changes...")
        call(['git', 'pull'])
        await self.bot.say("👋 Restarting bot!")
        await self.bot.close()

    @commands.has_permissions(kick_members=True)
    @commands.command(pass_context=True, hidden=True)
    async def userinfo(self, ctx, user):
        """Gets user info. SuperOP+."""
        u = ctx.message.mentions[0]
        role = u.top_role.name
        if role == "@everyone":
            role = "@ everyone"
        await self.bot.say("name = {}\nid = {}\ndiscriminator = {}\navatar = {}\nbot = {}\navatar_url = {}\ndefault_avatar = {}\ndefault_avatar_url = <{}>\ncreated_at = {}\ndisplay_name = {}\njoined_at = {}\nstatus = {}\ngame = {}\ncolour = {}\ntop_role = {}\n".format(u.name, u.id, u.discriminator, u.avatar, u.bot, u.avatar_url, u.default_avatar, u.default_avatar_url, u.created_at, u.display_name, u.joined_at, u.status, u.game, u.colour, role))

    @commands.has_permissions(ban_members=True)
    @commands.command(pass_context=True, name="clear")
    async def purge(self, ctx, limit: int):
        """Clears a given number of messages. Staff only."""
        try:
            await self.bot.purge_from(ctx.message.channel, limit=limit)
            msg = "🗑 **Cleared**: {} cleared {} messages in {}".format(ctx.message.author.mention, limit, ctx.message.channel.mention)
            await self.bot.send_message(self.bot.modlogs_channel, msg)
        except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

    @commands.has_permissions(manage_nicknames=True)
    @commands.command(pass_context=True, name="mute")
    async def mute(self, ctx, user, *, reason=""):
        """Mutes a user so they can't speak. Staff only."""
        try:
            member = ctx.message.mentions[0]
            await self.add_restriction(member, "Muted")
            await self.bot.add_roles(member, self.bot.muted_role)
            msg_user = "You were muted!"
            if reason != "":
                msg_user += " The given reason is: " + reason
            try:
                await self.bot.send_message(member, msg_user)
            except discord.errors.Forbidden:
                pass  # don't fail in case user has DMs disabled for this server, or blocked the bot
            await self.bot.say("{} can no longer speak.".format(member.mention))
            msg = "🔇 **Muted**: {} muted {} | {}#{}".format(ctx.message.author.mention, member.mention, self.bot.escape_name(member.name), self.bot.escape_name(member.discriminator))
            if reason != "":
                msg += "\n✏️ __Reason__: " + reason
            else:
                msg += "\nPlease add an explanation below. In the future, it is recommended to use `.mute <user> [reason]` as the reason is automatically sent to the user."
            await self.bot.send_message(self.bot.modlogs_channel, msg)
        except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

    @commands.has_permissions(manage_nicknames=True)
    @commands.command(pass_context=True, name="unmute")
    async def unmute(self, ctx, user):
        """Unmutes a user so they can speak. Staff only."""
        try:
            member = ctx.message.mentions[0]
            await self.remove_restriction(member, "Muted")
            await self.bot.remove_roles(member, self.bot.muted_role)
            await self.bot.say("{} can now speak again.".format(member.mention))
            msg = "🔈 **Unmuted**: {} unmuted {} | {}#{}".format(ctx.message.author.mention, member.mention, self.bot.escape_name(member.name), self.bot.escape_name(member.discriminator))
            await self.bot.send_message(self.bot.modlogs_channel, msg)
        except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

    @commands.command(pass_context=True, name="secure")
    async def secure(self, ctx, user, *, reason=""):
        """Give access to the hacker role"""
        author = ctx.message.author
        if (self.bot.owner_role not in author.roles):
            msg = "{} You cannot used this command.".format(author.mention)
            await self.bot.say(msg)
            return
        try:
            member = ctx.message.mentions[0]
            await self.bot.add_roles(member, self.bot.nohelp_role)
            msg = "⭕️ **Secure channel access**: {} gave access to secure channels to {} | {}#{}".format(ctx.message.author.mention, member.mention, self.bot.escape_name(member.name), self.bot.escape_name(member.discriminator))
            await self.bot.send_message(self.bot.modlogs_channel, msg)
        except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

    @commands.command(pass_context=True, name="insecure")
    async def insecure(self, ctx, user):
        """take away the probation role"""
        author = ctx.message.author
        if (self.bot.owner_role not in author.roles):
            msg = "{} You cannot used this command.".format(author.mention)
            await self.bot.say(msg)
            return
        try:
            member = ctx.message.mentions[0]
            await self.bot.add_roles(member, self.bot.unprobated_role)
            msg = "🚫 **Unprobated**: {} unprobated {} | {}#{}".format(ctx.message.author.mention, member.mention, self.bot.escape_name(member.name), self.bot.escape_name(member.discriminator))
            await self.bot.send_message(self.bot.modlogs_channel, msg)
        except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

    @commands.has_permissions(kick_members=True)
    @commands.command(pass_context=True, name="approve")
    async def approve(self, ctx, *users):
        """Approve a user, giving them the community role."""
        members = []
        for member in ctx.message.mentions:
            await self.bot.add_roles(member, self.bot.community_role)
            members.append(member.mention)
        await self.bot.say("Approved {} member(s).".format(len(members)))
        msg = "✅ **Approved**: {} approved {} members\n".format(ctx.message.author.mention, len(members))
        msg += ', '.join(members)
        await self.bot.send_message(self.bot.modlogs_channel, msg)

    @commands.has_permissions(kick_members=True)
    @commands.command(pass_context=True, name="revoke")
    async def revoke(self, ctx, *users):
        """Un-approve a user, removing the community role."""
        members = []
        for member in ctx.message.mentions:
            await self.bot.remove_roles(member, self.bot.community_role)
            members.append(member.mention)
        await self.bot.say("Un-approved {} member(s).".format(len(members)))
        msg = "❌ **Un-approved**: {} approved {} members\n".format(ctx.message.author.mention, len(members))
        msg += ', '.join(members)
        await self.bot.send_message(self.bot.modlogs_channel, msg)

    @commands.command(pass_context=True, name="addhacker")
    async def addhacker(self, ctx, user):
        """Add the hacker role to a user."""
        issuer = ctx.message.author
        if (self.bot.private_role not in issuer.roles) and (self.bot.staff_role not in issuer.roles):
            await self.bot.say("{} This command is limited to private and mod.".format(issuer.mention))
            return
        try:
            member = ctx.message.mentions[0]
        except IndexError:
            await self.bot.say("Please mention a user.")
            return
        await self.bot.add_roles(member, self.bot.hacker_role)
        await self.bot.say("{} is now a hacker.".format(member.mention))
        msg = "💻 **Hacker**: {} added hacker to {} | {}#{}".format(issuer.mention, member.mention, self.bot.escape_name(member.name), self.bot.escape_name(member.discriminator))
        await self.bot.send_message(self.bot.modlogs_channel, msg)

    @commands.has_permissions(kick_members=True)
    @commands.command(pass_context=True, name="probate")
    async def probate(self, ctx, user, *, reason=""):
        """Probate a user. Staff only."""
        try:
            member = ctx.message.mentions[0]
            await self.bot.remove_roles(member, self.bot.unprobated_role)
            msg_user = "You are under probation!"
            if reason != "":
                msg_user += " The given reason is: " + reason
            try:
                await self.bot.send_message(member, msg_user)
            except discord.errors.Forbidden:
                pass  # don't fail in case user has DMs disabled for this server, or blocked the bot
            await self.bot.say("{} is now in probation.".format(member.mention))
            msg = "🚫 **Probated**: {} probated {} | {}#{}".format(ctx.message.author.mention, member.mention, self.bot.escape_name(member.name), self.bot.escape_name(member.discriminator))
            if reason != "":
                msg += "\n✏️ __Reason__: " + reason
            else:
                msg += "\nPlease add an explanation below. In the future, it is recommended to use `.probate <user> [reason]` as the reason is automatically sent to the user."
            await self.bot.send_message(self.bot.modlogs_channel, msg)
        except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

    @commands.has_permissions(kick_members=True)
    @commands.command(pass_context=True, name="unprobate")
    async def unprobate(self, ctx, user):
        """Unprobate a user. Staff only."""
        try:
            for member in ctx.message.mentions:
                await self.bot.add_roles(member, self.bot.unprobated_role)
                await self.bot.say("{} is out of probation.".format(member.mention))
                msg = "⭕️ **Un-probated**: {} un-probated {} | {}#{}".format(ctx.message.author.mention, member.mention, self.bot.escape_name(member.name), self.bot.escape_name(member.discriminator))
                await self.bot.send_message(self.bot.modlogs_channel, msg)
        except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

    @commands.has_permissions(ban_members=True)
    @commands.command(pass_context=True)
    async def playing(self, ctx, *gamename):
        """Sets playing message. Staff only."""
        try:
            await self.bot.change_presence(game=discord.Game(name='{}'.format(" ".join(gamename))))
        except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

    @commands.has_permissions(ban_members=True)
    @commands.command(pass_context=True)
    async def status(self, ctx, status):
        """Sets status. Staff only."""
        try:
            if status == "online":
                await self.bot.change_presence(status=discord.Status.online)
            elif status == "offline":
                await self.bot.change_presence(status=discord.Status.offline)
            elif status == "idle":
                await self.bot.change_presence(status=discord.Status.idle)
            elif status == "dnd":
                await self.bot.change_presence(status=discord.Status.dnd)
            elif status == "invisible":
                await self.bot.change_presence(status=discord.Status.invisible)
        except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

    @commands.has_permissions(ban_members=True)
    @commands.command(pass_context=True, hidden=True)
    async def username(self, ctx, *, username):
        """Sets bot name. Staff only."""
        try:
            await self.bot.edit_profile(username=('{}'.format(username)))
        except discord.errors.Forbidden:
            await self.bot.say("💢 I don't have permission to do this.")

def setup(bot):
    bot.add_cog(Mod(bot))
