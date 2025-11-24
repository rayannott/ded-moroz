# ded-moroz
This is a Secret Santa Telegram bot app. Go here to try it out: https://t.me/secretsanta42bot (I'm pretty sure it's up).

## How to use?
Open, run /start.

## No but really
- clone repo; say, with
```bash
git clone https://github.com/rayannott/ded-moroz.git
```
- create `.env`
```env
BOT_TOKEN=...  # get it from @BotFather
DATABASE_URL=sqlite:///local.db  # or any other connection

# these are the current defaults; uncomment and change if needed
# MAX_ROOMS_MANAGED_BY_USER=3
# MIN_PLAYERS_TO_START_GAME=2

# these are optional
# ADMIN_NAME=Airat
# ADMIN_USERNAME=rayannott
# ADMIN_USER_ID=409474295
```
You can see your user id by messaging [this bot](https://t.me/userinfobot).
- `uv venv`
- `source .venv/bin/activate`
- `uv sync --all-groups`
- `uv run main.py`
