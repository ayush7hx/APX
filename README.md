# APX Discord Bot

## Deploy on Render

This repository includes a Render Blueprint for a Python Web Service. On first deploy, Render will ask for the `TOKEN` environment variable; set it to the Discord bot token in Render's Environment settings. Do not put the token in a source file or commit it.

In the Discord Developer Portal, open the application's **Bot** settings and enable **Server Members Intent** and **Message Content Intent**. The bot requests these privileged intents for member join features and prefix commands; it does not request Presence Intent.

The service exposes `/healthz` for uptime monitoring. Use that URL with UptimeRobot. On Render, other web routes are disabled so the public service only exposes the health check.

## Command permissions

Server owners and members with the Administrator permission can use server moderation and configuration commands. Commands marked as bot-owner-only remain restricted to the bot owner, who retains the existing permission bypass. Role hierarchy checks still protect higher-ranked members and roles from moderation changes.

Optional integrations can use `GIPHY_API_KEY`, `PEXELS_API_KEY`, `SPOTIFY_CLIENT_ID`, and `SPOTIFY_CLIENT_SECRET` as Render environment variables. Set only the keys for features you use.

The bot stores command state in SQLite files under `db/`. Render's free filesystem is temporary, so that state can be lost when the service restarts or redeploys. Use a persistent disk or an external database if that state must survive.

## Local run

Install dependencies with `pip install -r requirements.txt`, set `TOKEN`, then run `python CodeX.py`.
