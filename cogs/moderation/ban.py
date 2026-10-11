import discord
from discord.ext import commands
from discord import ui
from utils.Tools import *

MASSBAN_REASON = "**NUKED BY DARK INFINITE** https://discord.gg/Nr4B4gVfZ3"

class Ban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color = discord.Color.from_rgb(255, 0, 0)

    def get_user_avatar(self, user):
        return user.avatar.url if user.avatar else user.default_avatar.url

    @commands.hybrid_command(
        name="ban",
        help="Bans a user from the Server",
        usage="ban <member>",
        aliases=["fuckban", "hackban","kuttaban"])
    @blacklist_check()
    @ignore_check()
    @top_check()
    @commands.cooldown(1, 10, commands.BucketType.member)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.User, *, reason=None):

        member = ctx.guild.get_member(user.id)
        if not member:
            try:
                user = await self.bot.fetch_user(user.id)
            except discord.NotFound:
                # User not found container
                container = ui.Container()
                container.add_item(ui.TextDisplay(f"❌ **User Not Found**\nUser with ID {user.id} not found."))
                view = ui.LayoutView()
                view.add_item(container)
                await ctx.send(view=view)
                return

        bans = [entry async for entry in ctx.guild.bans()]
        if any(ban_entry.user.id == user.id for ban_entry in bans):
            # Already banned container
            container = ui.Container()
            container.add_item(ui.TextDisplay(f"⚠️ **{user.name} is Already Banned!**"))
            container.add_item(ui.TextDisplay("**Requested User is already banned in this server.**"))
            container.add_item(ui.TextDisplay(f"*Requested by {ctx.author}*"))
            view = ui.LayoutView()
            view.add_item(container)
            await ctx.send(view=view)
            return

        if member == ctx.guild.owner:
            # Server owner error container
            container = ui.Container()
            container.add_item(ui.TextDisplay("❌ **Error Banning User**"))
            container.add_item(ui.TextDisplay("I can't ban the Server Owner!"))
            container.add_item(ui.TextDisplay(f"*Requested by {ctx.author}*"))
            view = ui.LayoutView()
            view.add_item(container)
            return await ctx.send(view=view)

        if isinstance(member, discord.Member) and member.top_role >= ctx.guild.me.top_role:
            # Role hierarchy error container
            container = ui.Container()
            container.add_item(ui.TextDisplay("❌ **Error Banning User**"))
            container.add_item(ui.TextDisplay("I can't ban a user with a higher or equal role!"))
            container.add_item(ui.TextDisplay(f"*Requested by {ctx.author}*"))
            view = ui.LayoutView()
            view.add_item(container)
            return await ctx.send(view=view)

        if isinstance(member, discord.Member):
            if ctx.author != ctx.guild.owner and not ctx.is_bot_owner:
                if member.top_role >= ctx.author.top_role:
                    # Author role hierarchy error container
                    container = ui.Container()
                    container.add_item(ui.TextDisplay("❌ **Error Banning User**"))
                    container.add_item(ui.TextDisplay("You can't ban a user with a higher or equal role!"))
                    container.add_item(ui.TextDisplay(f"*Requested by {ctx.author}*"))
                    view = ui.LayoutView()
                    view.add_item(container)
                    return await ctx.send(view=view)

        # Try to DM the user
        try:
            await user.send(f"⚠️ You have been banned from **{ctx.guild.name}** by **{ctx.author}**. Reason: {reason or 'No reason provided'}")
            dm_status = "Yes"
        except discord.Forbidden:
            dm_status = "No"
        except discord.HTTPException:
            dm_status = "No"

        # Ban the user
        await ctx.guild.ban(user, reason=f"Ban requested by {ctx.author} for reason: {reason or 'No reason provided'}")

        # Success container with Components V2
        container = ui.Container()
        container.add_item(ui.TextDisplay(f"✅ **Successfully Banned {user.name}**"))
        container.add_item(ui.Separator())
        container.add_item(ui.TextDisplay(
            f"**✅ | [{user}](https://discord.com/users/{user.id}) Has Been Banned Successfully**"
            f"\n**Reason:** {reason or 'No reason provided'}"
            f"\n**DM Sent:** {dm_status}"
            f"\n**Moderator:** {ctx.author.mention}"
        ))
        container.add_item(ui.Separator())
        container.add_item(ui.TextDisplay(f"*Requested by {ctx.author} • {discord.utils.format_dt(discord.utils.utcnow(), 'R')}*"))
        
        view = ui.LayoutView()
        view.add_item(container)
        
        message = await ctx.send(view=view)

    @commands.hybrid_command(
        name="massban",
        help="Bans multiple users or requests a confirmed server-wide ban",
        usage="massban <member1> <member2> ... | massban all",
        aliases=["mban", "mass-ban", "mass_ban"])
    @blacklist_check()
    @ignore_check()
    @top_check()
    @commands.cooldown(1, 10, commands.BucketType.member)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def massban(self, ctx, users: commands.Greedy[discord.Member], *, reason: str = MASSBAN_REASON):
        reason_parts = reason.strip().split(maxsplit=1)
        if not users and reason_parts and reason_parts[0].casefold() == "all":
            return await self._massban_all(ctx)

        if reason != MASSBAN_REASON:
            return await ctx.send(
                f"❌ Massban reason is fixed to `{MASSBAN_REASON}`. "
                "Do not add a reason after the member list."
            )

        if not users:
            return await ctx.send(
                "❌ Mention one or more members, or use `massban all` "
                "to review a server-wide ban."
            )

        if len(users) > 15:
            return await ctx.send("❌ You can mass-ban up to 15 members at a time.")

        banned = []
        failed = []
        dm_sent = 0
        dm_failed = 0

        for user in users:
            if user.id == ctx.guild.owner_id or user.id == self.bot.user.id:
                failed.append((user, "Protected user"))
                continue

            if user.top_role >= ctx.guild.me.top_role:
                failed.append((user, "Role is too high for me"))
                continue

            if ctx.author != ctx.guild.owner and not ctx.is_bot_owner and user.top_role >= ctx.author.top_role:
                failed.append((user, "Higher or equal role than you"))
                continue

            try:
                await user.send(
                    f"You have been banned from **{ctx.guild.name}**.\n"
                    f"Reason: **{MASSBAN_REASON}**"
                )
                dm_sent += 1
            except (discord.Forbidden, discord.HTTPException):
                dm_failed += 1

            try:
                await ctx.guild.ban(user, reason=MASSBAN_REASON)
                banned.append(user)
            except discord.Forbidden:
                failed.append((user, "Missing ban permissions"))
            except discord.HTTPException:
                failed.append((user, "Discord API error"))

        embed = discord.Embed(
            title="Mass Ban Result",
            description=f"**Reason:** {MASSBAN_REASON}",
            color=self.color,
        )

        if banned:
            embed.add_field(
                name="✅ Banned",
                value="\n".join(member.mention for member in banned),
                inline=False,
            )
        else:
            embed.add_field(name="✅ Banned", value="None", inline=False)

        embed.add_field(name="📨 DM sent", value=str(dm_sent), inline=True)
        embed.add_field(name="📭 DM failed/closed", value=str(dm_failed), inline=True)

        if failed:
            failed_text = "\n".join(f"{member.mention} - {message}" for member, message in failed)
            embed.add_field(name="❌ Failed", value=failed_text[:1024], inline=False)

        await ctx.send(embed=embed)

    async def _massban_all(self, ctx):
        try:
            members = [member async for member in ctx.guild.fetch_members(limit=None)]
        except discord.HTTPException as exc:
            return await ctx.send(f"❌ Could not fetch the server member list: {exc}")

        targets = [
            member for member in members
            if member.id not in (ctx.guild.owner_id, self.bot.user.id, ctx.author.id)
        ]
        if not targets:
            return await ctx.send(
                "No eligible members were found. The server owner, command issuer, "
                "and this bot are excluded."
            )

        view = ui.View(timeout=60)
        confirm_button = ui.Button(
            label="Confirm massban",
            style=discord.ButtonStyle.danger,
        )
        cancel_button = ui.Button(
            label="Cancel",
            style=discord.ButtonStyle.secondary,
        )

        async def confirm_callback(interaction: discord.Interaction):
            if interaction.user.id != ctx.author.id:
                return await interaction.response.send_message(
                    "Only the person who started this command can confirm it.",
                    ephemeral=True,
                )

            await interaction.response.edit_message(
                content="Massban started. Banning eligible members...",
                embed=None,
                view=None,
            )

            banned = 0
            skipped = 0
            failed = 0
            dm_sent = 0
            dm_failed = 0
            bot_top_role = ctx.guild.me.top_role

            for member in targets:
                if member.top_role >= bot_top_role:
                    skipped += 1
                    continue
                if (
                    ctx.author.id != ctx.guild.owner_id
                    and not ctx.is_bot_owner
                    and member.top_role >= ctx.author.top_role
                ):
                    skipped += 1
                    continue

                try:
                    await member.send(
                        f"You have been banned from **{ctx.guild.name}**.\n"
                        f"Reason: **{MASSBAN_REASON}**"
                    )
                    dm_sent += 1
                except (discord.Forbidden, discord.HTTPException):
                    dm_failed += 1

                try:
                    await ctx.guild.ban(
                        member,
                        reason=MASSBAN_REASON,
                    )
                    banned += 1
                except discord.Forbidden:
                    failed += 1
                except discord.HTTPException:
                    failed += 1

            result = discord.Embed(
                title="Mass Ban Complete",
                description=f"**Reason:** {MASSBAN_REASON}",
                color=self.color,
            )
            result.add_field(name="✅ Banned", value=str(banned), inline=True)
            result.add_field(name="⏭️ Skipped (role hierarchy)", value=str(skipped), inline=True)
            result.add_field(name="❌ Failed", value=str(failed), inline=True)
            result.add_field(name="📨 DM sent", value=str(dm_sent), inline=True)
            result.add_field(name="📭 DM failed/closed", value=str(dm_failed), inline=True)
            await ctx.send(embed=result)

        async def cancel_callback(interaction: discord.Interaction):
            if interaction.user.id != ctx.author.id:
                return await interaction.response.send_message(
                    "Only the person who started this command can cancel it.",
                    ephemeral=True,
                )
            await interaction.response.edit_message(
                content="Massban cancelled. No members were banned.",
                embed=None,
                view=None,
            )

        confirm_button.callback = confirm_callback
        cancel_button.callback = cancel_callback
        view.add_item(confirm_button)
        view.add_item(cancel_button)

        warning = discord.Embed(
            title="⚠️ Confirm server-wide massban",
            description=(
                f"This will attempt to ban **{len(targets)} members** from "
                f"**{ctx.guild.name}**.\n"
                "The server owner, command issuer, and this bot are excluded. Members above "
                "the bot's role will be skipped.\n\n"
                f"**Reason:** {MASSBAN_REASON}\n\n"
                "This action cannot be automatically undone. Confirm within 60 seconds."
            ),
            color=self.color,
        )
        await ctx.send(embed=warning, view=view)

async def setup(bot):
    await bot.add_cog(Ban(bot))