# APX Discord Bot

## Deploy on Render

This repository includes a Render Blueprint for a Python Web Service. On first deploy, Render will ask for the `TOKEN` environment variable; set it to the Discord bot token in Render's Environment settings. Do not put the token in a source file or commit it.

In the Discord Developer Portal, open the application's **Bot** settings and enable **Server Members Intent** and **Message Content Intent**. The bot requests these privileged intents for member join features and prefix commands; it does not request Presence Intent.

The project pins Render to Python `3.11.11` in both `.python-version` and `render.yaml`. If an existing Render service still builds with another Python version, set `PYTHON_VERSION` to `3.11.11` in the service's Environment settings; dashboard environment variables override the Blueprint.

The service exposes `/healthz` for uptime monitoring. Use that URL with UptimeRobot. On Render, other web routes are disabled so the public service only exposes the health check.

If Discord returns Cloudflare HTTP 429 / Error 1015 at login, the host's outbound IP is temporarily rate-limited. The bot waits before retrying and logs the Discord HTTP status; code cannot bypass or clear an IP-level restriction. Avoid repeated manual restarts and let Discord's cooldown expire.

Run this bot on **one host at a time**. Do not start the same bot token on both Replit and Render simultaneously: both processes use the same Discord gateway identity and can create duplicate API traffic, reconnects, and rate limits. Stop the bot on the old host before starting it on the new host.

The vanity-role checker polls Discord's invite endpoint every five minutes, reuses one HTTP session, and leaves role assignments unchanged when Discord returns an error or rate limit. Startup DM catch-up also spaces requests and stops when Discord rate-limits it.

## Command permissions

Server owners and members with the Administrator permission can use server moderation and configuration commands. Commands marked as bot-owner-only remain restricted to the bot owner, who retains the existing permission bypass. Role hierarchy checks still protect higher-ranked members and roles from moderation changes.

Optional integrations can use `GIPHY_API_KEY`, `PEXELS_API_KEY`, `SPOTIFY_CLIENT_ID`, and `SPOTIFY_CLIENT_SECRET` as Render environment variables. Set only the keys for features you use.

The bot stores command state in SQLite files under `db/`. Render's free filesystem is temporary, so that state can be lost when the service restarts or redeploys. Use a persistent disk or an external database if that state must survive.

## Deploy on Replit

Import this repository into Replit, add `TOKEN` under **Tools → Secrets**, then run the project. The included `.replit` file starts `python CodeX.py`; dependencies are listed in `requirements.txt`. Keep the Replit deployment to one running instance, and stop it before running this token on Render.

## Local run

Install dependencies with `pip install -r requirements.txt`, set `TOKEN`, then run `python CodeX.py`.
