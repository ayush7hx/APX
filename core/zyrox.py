from __future__ import annotations
from discord.ext import commands
import discord
import aiohttp
import json
import jishaku
import asyncio
import typing
import time
from typing import List
import aiosqlite
from utils.config import OWNER_IDS
from utils import getConfig, updateConfig
from .Context import Context
from colorama import Fore, Style, init
import importlib
import inspect

init(autoreset=True)

# Corrected the extensions list
extensions: List[str] = [
    "cogs"
]

class zyrox(commands.AutoShardedBot):
    def __init__(self, *arg, **kwargs):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        super().__init__(command_prefix=self.get_prefix,
                         help_command=None,
                         case_insensitive=True,
                         intents=intents,
                         status=discord.Status.do_not_disturb,
                         strip_after_prefix=True,
                         owner_ids=OWNER_IDS,
                         allowed_mentions=discord.AllowedMentions(
                             everyone=False, replied_user=False, roles=False),
                         sync_commands_debug=True,
                         sync_commands=True,
                         shard_count=1)
        self._prefix_cache: dict[int, tuple[float, str]] = {}
        self._no_prefix_cache: dict[int, tuple[float, bool]] = {}

    async def setup_hook(self):
        async with aiosqlite.connect("db/np.db") as db:
            await db.execute(
                "CREATE TABLE IF NOT EXISTS np (id INTEGER PRIMARY KEY)"
            )
            await db.commit()
        await self.load_extensions()

    async def get_context(self, origin, *, cls=Context):
        return await super().get_context(origin, cls=cls)

    async def load_extensions(self):
        for extension in extensions:
            try:
                await self.load_extension(extension)
                print(Fore.GREEN + Style.BRIGHT + f"Loaded extension: {extension}")
            except Exception as e:
                print(f"{Fore.RED}{Style.BRIGHT}Failed to load extension {extension}. {e}")
                raise
        print(Fore.GREEN + Style.BRIGHT + "*" * 20)

    async def send_raw(self, channel_id: int, content: str, **kwargs) -> typing.Optional[discord.Message]:
        await self.http.send_message(channel_id, content, **kwargs)

    async def invoke_help_command(self, ctx: Context) -> None:
        return await ctx.send_help(ctx.command)

    async def fetch_message_by_channel(self, channel: discord.TextChannel, messageID: int) -> typing.Optional[discord.Message]:
        async for msg in channel.history(limit=1, before=discord.Object(messageID + 1), after=discord.Object(messageID - 1)):
            return msg

    async def get_prefix(self, message: discord.Message):
        now = time.monotonic()
        author_id = message.author.id
        no_prefix_entry = self._no_prefix_cache.get(author_id)
        if no_prefix_entry is not None and no_prefix_entry[0] > now:
            has_no_prefix = no_prefix_entry[1]
        else:
            async with aiosqlite.connect('db/np.db') as db:
                async with db.execute(
                    "SELECT 1 FROM np WHERE id = ?",
                    (author_id,)
                ) as cursor:
                    has_no_prefix = await cursor.fetchone() is not None
            if len(self._no_prefix_cache) >= 4096:
                self._no_prefix_cache = {
                    key: entry for key, entry in self._no_prefix_cache.items()
                    if entry[0] > now
                }
            self._no_prefix_cache[author_id] = (now + 5, has_no_prefix)

        if message.guild:
            guild_id = message.guild.id
            prefix_entry = self._prefix_cache.get(guild_id)
            if prefix_entry is not None and prefix_entry[0] > now:
                prefix = prefix_entry[1]
            else:
                data = await getConfig(guild_id)
                prefix = data["prefix"]
                if len(self._prefix_cache) >= 4096:
                    self._prefix_cache = {
                        key: entry for key, entry in self._prefix_cache.items()
                        if entry[0] > now
                    }
                self._prefix_cache[guild_id] = (now + 5, prefix)

            if has_no_prefix:
                return commands.when_mentioned_or(prefix, '')(self, message)
            return commands.when_mentioned_or(prefix)(self, message)
        else:
            if has_no_prefix:
                return commands.when_mentioned_or('?', '')(self, message)
            return commands.when_mentioned_or('')(self, message)

    async def on_message_edit(self, before, after):
        if not before.content or before.content == after.content:
            return
        if after.guild is None or after.author.bot:
            return
        ctx: Context = await self.get_context(after, cls=Context)
        if ctx.command is None:
            return
        if type(ctx.channel) == "public_thread":
            return
        await self.invoke(ctx)

def setup_bot():
    intents = discord.Intents.all()
    bot = zyrox(intents=intents)
    return bot
