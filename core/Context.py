from __future__ import annotations

from discord.ext import commands
import discord
import functools
from typing import Optional, Any
import asyncio

__all__ = ("Context", "has_guild_permissions")


def has_guild_permissions(**perms):
    invalid = set(perms) - set(discord.Permissions.VALID_FLAGS)
    if invalid:
        raise TypeError(f"Invalid permission(s): {', '.join(invalid)}")

    def predicate(ctx: commands.Context) -> bool:
        if not ctx.guild:
            raise commands.NoPrivateMessage

        missing = [
            permission
            for permission, value in perms.items()
            if getattr(ctx.guild_permissions, permission) != value
        ]
        if missing:
            raise commands.MissingPermissions(missing)
        return True

    return commands.check(predicate)


class Context(commands.Context):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    @property
    def is_bot_owner(self) -> bool:
        owner_id = getattr(self.bot, "owner_id", None)
        owner_ids = getattr(self.bot, "owner_ids", None) or ()
        return self.author.id == owner_id or self.author.id in owner_ids

    @property
    def is_guild_owner_or_admin(self) -> bool:
        return bool(
            self.guild
            and (
                self.author.id == self.guild.owner_id
                or self.author.guild_permissions.administrator
            )
        )

    @property
    def permissions(self) -> discord.Permissions:
        if self.is_bot_owner:
            return discord.Permissions.all()
        return super().permissions

    @property
    def guild_permissions(self) -> discord.Permissions:
        if self.is_bot_owner:
            return discord.Permissions.all()
        return super().guild_permissions

    def __repr__(self):
        return "<core.Context>"

    @property
    async def session(self):
        return self.bot.session

    @discord.utils.cached_property
    def replied_reference(self) -> Optional[discord.Message]:
        ref = self.message.reference
        if ref and isinstance(ref.resolved, discord.Message):
            return ref.resolved.to_reference()
        return None

    def with_type(func):

        @functools.wraps(func)
        async def wrapped(self, *args, **kwargs):
            context = args[0] if isinstance(args[0],
                                            commands.Context) else args[1]
            try:
                async with context.typing():
                    await func(*args, **kwargs)
            except discord.Forbidden:  
                await func(*args, **kwargs)

        return wrapped

    async def show_help(self, command: str = None) -> Any:
        cmd = self.bot.get_command('help')
        command = command or self.command.qualified_name
        await self.invoke(cmd, command=command)

    async def send(self,
                   content: Optional[str] = None,
                   **kwargs) -> Optional[discord.Message]:
        if not (self.channel.permissions_for(self.me)).send_messages:
            try:
                await self.author.send(
                    "bot dont have perms to send msg in that channel")
            except discord.Forbidden:  
                pass
            return
        return await super().send(content, **kwargs)

    async def reply(self,
                    content: Optional[str] = None,
                    **kwargs) -> Optional[discord.Message]:
        if not (self.channel.permissions_for(self.me)).send_messages:
            try:
                await self.author.send(
                    "bot dont have perms to send msg in that channel")
            except discord.Forbidden:  
                pass
            return
        return await super().reply(content, **kwargs)

    async def release(self, delay: Optional[int] = None) -> None:
        delay = delay or 0
        await asyncio.sleep(delay)
