from __future__ import annotations

from collections.abc import Sequence

import discord


def _embed_text(embed: discord.Embed) -> str:
    parts: list[str] = []

    if embed.author.name:
        parts.append(embed.author.name)
    if embed.title:
        parts.append(embed.title)
    if embed.description:
        parts.append(embed.description)
    for field in embed.fields:
        parts.append(f"{field.name}\n{field.value}" if field.name else field.value)
    if embed.footer.text:
        parts.append(embed.footer.text)
    if embed.image.url:
        parts.append(f"Image: {embed.image.url}")
    if embed.thumbnail.url:
        parts.append(f"Thumbnail: {embed.thumbnail.url}")

    return "\n\n".join(parts)


def _split_message(text: str, limit: int = 2000) -> list[str]:
    chunks: list[str] = []
    while len(text) > limit:
        split_at = text.rfind("\n", 0, limit + 1)
        if split_at <= 0:
            split_at = limit
        chunks.append(text[:split_at])
        text = text[split_at:].lstrip()
    if text:
        chunks.append(text)
    return chunks


async def send_plain_dm(
    target: discord.abc.Messageable,
    content: str | None = None,
    *,
    embed: discord.Embed | None = None,
    embeds: Sequence[discord.Embed] | None = None,
    **kwargs,
) -> list[discord.Message]:
    parts = [content] if content else []
    if embed is not None:
        parts.append(_embed_text(embed))
    if embeds:
        parts.extend(_embed_text(item) for item in embeds)

    text = "\n\n".join(part for part in parts if part)
    chunks = _split_message(text) or ["\u200b"]
    messages: list[discord.Message] = []
    for index, chunk in enumerate(chunks):
        send_kwargs = kwargs if index == 0 else {}
        messages.append(await target.send(chunk, **send_kwargs))
    return messages
