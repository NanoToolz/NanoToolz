# NanoToolz Telegram Store Bot

## Quick start
1) Copy `.env.example` to `.env` and set `BOT_TOKEN`
2) `pip install -r requirements.txt`
3) `python main.py`

## Admin panel
1) `uvicorn web.admin:app --reload`
2) Open `http://localhost:8000`
3) Login with `ADMIN_USERNAME` and `ADMIN_PASSWORD` from `.env`

## Structure
- `main.py` - entry point
- `src/bot/app.py` - dispatcher setup
- `src/bot/commands.py` - command list
- `src/bot/routers.py` - router registry
- `src/bot/features/<feature>/` - feature folders
  - `handlers.py` - handlers and logic
  - `keyboards.py` - buttons/UI
  - `messages.py` - text/messages
- `src/database/models.py` - database schema
- `src/seed.py` - optional seed data (skips if data already exists)
- `web/admin.py` - admin panel (optional)

## Add a new feature
1) Create a folder: `src/bot/features/<feature>/`
2) Add `handlers.py`, `keyboards.py`, `messages.py`
3) Register the router in `src/bot/routers.py`
4) Add a command in `src/bot/commands.py` (if needed)
5) Add DB tables in `src/database/models.py` (if needed)

## Products
- Stored in the database.
- Use `src/seed.py` for initial categories/products.
- To reseed from scratch, delete the DB file and run the bot again.

## Settings
- Store settings are stored in the database (`settings` table).
- Update them from the admin panel (Store Settings page).
