import discord
from discord.ext import commands
from discord import app_commands, Interaction
from difflib import get_close_matches
from core import Context
from core.zyrox import zyrox
from core.Cog import Cog
from utils.Tools import getConfig
from itertools import chain
import json
import os
from utils import help as vhelp
from utils import Paginator, DescriptionEmbedPaginator, FieldPagePaginator, TextPaginator
from utils.config import serverLink
from utils.Tools import *

color = 0xFF0000
client = zyrox()

EMOJI_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "emojis.json")

FALLBACK_EMOJIS = {
    "ArrowRed":      "•",
    "zArrow":        "➡️",
    "zCloud":        "☁️",
    "zSafe":         "🛡️",
    "zbot":          "🤖",
    "zwrench":       "🔧",
    "zmusic":        "🎵",
    "zwifi":         "📶",
    "zsowrd":        "•",
    "zpeople":       "👤",
    "zrocket":       "•",
    "games":         "•",
    "zban":          "🚫",
    "zunmute":       "•",
    "zseed":         "👋",
    "ztada":         "•",
    "zticket":       "🎟️",
    "New":           "•",
    "zmodule":       "🔹",
    "zcast":         "📜",
    "starr":         "⭐",
    "zcounting":     "•",
    "zyrox_system":  "⚙️",
    "zai":           "•",
    "boost":         "💎",
    "zlevelup":      "•",
    "zpin":          "📌",
    "zyroxthunder":  "•",
    "lock":          "•",
    "zmc":           "⛏️",
    "zmsg":          "•",
    "zcircle":       "•",
    "loadingred":    "⏳",
}

EMOJI_ALIASES = {
    "zrocket":    ["zrocket", "zrocke"],
    "ztada":      ["ztada", "ztad", "TADAA"],
    "New":        ["New", "New_1", "New_2"],
    "lock":       ["lock", "lock1"],
    "zmsg":       ["zmsg", "zms"],
    "zwrench":    ["zwrench", "wrench1"],
    "zcircle":    ["zcircle", "zcircle1"],
    "loadingred": ["loadingred", "loading"],
    "zmodule":    ["zmodule", "zsettings"],
    "zai":        ["zai"],
    "boost":      ["boost"],
}

def get_emoji(name: str) -> str:
    """Return a built-in Unicode emoji or symbol, never a server custom emoji."""
    return FALLBACK_EMOJIS.get(name, "🔹")

class HelpCommand(commands.HelpCommand):

  async def send_ignore_message(self, ctx, ignore_type: str):
    if ignore_type == "channel":
      await ctx.reply(f"This channel is ignored.", mention_author=False)
    elif ignore_type == "command":
      await ctx.reply(f"{ctx.author.mention} This Command, Channel, or You have been ignored here.", delete_after=6)
    elif ignore_type == "user":
      await ctx.reply(f"You are ignored.", mention_author=False)

  async def on_help_command_error(self, ctx, error):
    errors = [
      commands.CommandOnCooldown, commands.CommandNotFound,
      discord.HTTPException, commands.CommandInvokeError
    ]
    if not type(error) in errors:
      await self.context.reply(f"Unknown Error Occurred\n{error.original}",
                               mention_author=False)
    else:
      if type(error) == commands.CommandOnCooldown:
        return
    return await super().on_help_command_error(ctx, error)

  async def command_not_found(self, string: str) -> None:
    ctx = self.context
    check_ignore = await ignore_check().predicate(ctx)
    check_blacklist = await blacklist_check().predicate(ctx)

    if not check_blacklist:
        return

    if not check_ignore:
        await self.send_ignore_message(ctx, "command")
        return

    cmds = (str(cmd) for cmd in self.context.bot.walk_commands())
    matches = get_close_matches(string, cmds)

    embed = discord.Embed(
        title="INF Helper",
        description=f">>> **Ops! Command not found with the name** `{string}`.",
        color=0xFF0000
    )
                          
    #if matches:
        #match_list = "\n".join([f"{index}. `{match}`" for index, match in enumerate(matches, start=1)])
        #embed.add_field(name="Did you mean:", value=match_list, inline=True)

    await ctx.reply(embed=embed, mention_author=True)

  async def send_bot_help(self, mapping):
    ctx = self.context
    check_ignore = await ignore_check().predicate(ctx)
    check_blacklist = await blacklist_check().predicate(ctx)

    if not check_blacklist:
      return

    if not check_ignore:
      await self.send_ignore_message(ctx, "command")
      return

    loading_embed = discord.Embed(
      description=f"{get_emoji('loadingred')} Loading help Menu...",
      color=0xFF0000
    )
    loading_msg = await ctx.reply(embed=loading_embed, mention_author=False)

    if ctx.guild:
      data = await getConfig(ctx.guild.id)
      prefix = data["prefix"]
    else:
      prefix = ctx.prefix or "?"

    e = get_emoji  # shortcut

    embed = discord.Embed(
        description=(
         f"**{e('ArrowRed')} __Start INF Today__**\n"
         f"**{e('zArrow')} Type {prefix}antinuke enable**\n"
         f"**{e('zArrow')} Server Prefix:** `{prefix}`\n"
         f"**{e('zArrow')} Total Commands:** `{len(set(self.context.bot.walk_commands()))}`\n"),
        color=0xFF0000)
    embed.set_author(name=f"{ctx.author}",
                     icon_url=ctx.author.display_avatar.url)
    embed.set_thumbnail(url=ctx.author.display_avatar.url)

    N = e('New')
    embed.add_field(
        name=f"{e('zCloud')} __**Main Features**__",
        value=f">>> \n {e('zSafe')} `»` Security\n"
              f" {e('zbot')} `»` Automoderation\n"
              f" {e('zwrench')} `»` Utility\n"
              f" {e('zmusic')} `»` Music\n"
              f" {e('zwifi')} `»` Autoreact & responder\n"
              f" {e('zsowrd')} `»` Moderation\n"
              f" {e('zpeople')} `»` Autorole & Invc\n"
              f" {e('zrocket')} `»` Fun\n"
              f" {e('games')} `»` Games\n"
              f" {e('zban')} `»` Ignore Channels\n"
              f" {e('zwifi')} `»` Server\n"
              f" {e('zunmute')} `»` Voice\n"
              f" {e('zseed')} `»` Welcomer\n"
              f" {e('ztada')} `»` Giveaway\n"
              f" {e('zticket')} `»` Ticket {N}\n"
              f" {e('zpeople')} `»` Invite Tracker {N}\n"
    )

    embed.add_field(
        name=f" {e('zmodule')} __**Extra Features**__",
        value=f">>> \n {e('zcast')} `»` Advance Logging\n"
              f" {e('starr')} `»` Vanityroles\n"
              f" {e('zcounting')} `»` Counting {N}\n"
              f" {e('zyrox_system')} `»` J2C {N}\n"
              f" {e('zai')} `»` AI {N}\n"
              f" {e('boost')} `»` Boost {N}\n"
              f" {e('zlevelup')} `»` Leveling {N}\n"
              f" {e('zpin')} `»` Sticky {N}\n"
              f" {e('zyroxthunder')} `»` Verification {N}\n"
              f" {e('lock')} `»` Encryption {N}\n"
              f" {e('zmc')} `»` Minecraft {N}\n"
              f" {e('zmsg')} `»` Joindm {N}\n"
              f" {e('zcircle')} `»` Birthday {N}\n"
              f" {e('zcircle')} `»` Customrole\n"
    )

    embed.set_footer(
      text=f"Requested By {self.context.author} | [Support](https://discord.gg/4NHmRUn9HJ)",
    )
    
    view = vhelp.View(mapping=mapping, ctx=self.context, homeembed=embed, ui=2)
    await loading_msg.edit(embed=embed, view=view)

  async def send_command_help(self, command):
    ctx = self.context
    check_ignore = await ignore_check().predicate(ctx)
    check_blacklist = await blacklist_check().predicate(ctx)

    if not check_blacklist:
      return

    if not check_ignore:
      await self.send_ignore_message(ctx, "command")
      return

    zyrox = f">>> {command.help}" if command.help else '>>> No Help Provided...'
    embed = discord.Embed(
        description=f"""{zyrox}""",
        color=color)
    alias = ' & '.join(command.aliases)

    embed.add_field(name="**Alt cmd**",
                      value=f"```{alias}```" if command.aliases else "No Alt cmd",
                      inline=False)
    embed.add_field(name="**Usage**",
                      value=f"```{self.context.prefix}{command.signature}```\n")
    embed.set_author(name=f"{command.qualified_name.title()} Command")
    embed.set_footer(text="<[] = optional | < > = required • Use Prefix Before Commands.")
    await self.context.reply(embed=embed, mention_author=False)

  def get_command_signature(self, command: commands.Command) -> str:
    parent = command.full_parent_name
    if len(command.aliases) > 0:
      aliases = ' | '.join(command.aliases)
      fmt = f'[{command.name} | {aliases}]'
      if parent:
        fmt = f'{parent}'
      alias = f'[{command.name} | {aliases}]'
    else:
      alias = command.name if not parent else f'{parent} {command.name}'
    return f'{alias} {command.signature}'

  def common_command_formatting(self, embed_like, command):
    embed_like.title = self.get_command_signature(command)
    if command.description:
      embed_like.description = f'{command.description}\n\n{command.help}'
    else:
      embed_like.description = command.help or 'No help found...'

  async def send_group_help(self, group):
    ctx = self.context
    check_ignore = await ignore_check().predicate(ctx)
    check_blacklist = await blacklist_check().predicate(ctx)

    if not check_blacklist:
      return

    if not check_ignore:
      await self.send_ignore_message(ctx, "command")
      return

    entries = [
        (
            f"`{self.context.prefix}{cmd.qualified_name}`\n",
            f"{cmd.short_doc if cmd.short_doc else ''}\n\u200b"
        )
        for cmd in group.commands
      ]

    count = len(group.commands)

    embeds = FieldPagePaginator(
      entries=entries,
      title=f"{group.qualified_name.title()} [{count}]",
      description="< > Duty | [ ] Optional\n",
      per_page=4
    ).get_pages()   
    
    paginator = Paginator(ctx, embeds)
    await paginator.paginate()

  async def send_cog_help(self, cog):
    ctx = self.context
    check_ignore = await ignore_check().predicate(ctx)
    check_blacklist = await blacklist_check().predicate(ctx)

    if not check_blacklist:
      return

    if not check_ignore:
      await self.send_ignore_message(ctx, "command")
      return

    entries = [(
      f"> `{self.context.prefix}{cmd.qualified_name}`",
      f"-# Description : {cmd.short_doc if cmd.short_doc else ''}"
      f"\n\u200b",
    ) for cmd in cog.get_commands()]
    paginator = Paginator(source=FieldPagePaginator(
      entries=entries,
      title=f"INF's {cog.qualified_name.title()} ({len(cog.get_commands())})",
      description="`<..> Required | [..] Optional`\n\n",
      color=0xFF0000,
      per_page=4),
                          ctx=self.context)
    await paginator.paginate()


class Help(Cog, name="help"):

  def __init__(self, client: zyrox):
    self._original_help_command = client.help_command
    attributes = {
      'name': "help",
      'aliases': ['h'],
      'cooldown': commands.CooldownMapping.from_cooldown(1, 5, commands.BucketType.user),
      'help': 'Shows help about bot, a command, or a category'
    }
    client.help_command = HelpCommand(command_attrs=attributes)
    client.help_command.cog = self

  async def cog_unload(self):
    self.help_command = self._original_help_command