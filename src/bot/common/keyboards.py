
import json

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.bot.common.buttons import MAIN_MENU_BUTTONS
from src.logger import logger

def _parse_menu_config(config_json: str | None) -> list[list[dict[str, str]]] | None:
    if not config_json or not config_json.strip():
        return None
    try:
        data = json.loads(config_json)
    except json.JSONDecodeError as exc:
        logger.warning("Invalid main menu JSON: %s", exc)
        return None
    if not isinstance(data, list):
        logger.warning("Main menu JSON must be a list of rows.")
        return None

    rows: list[list[dict[str, str]]] = []
    for row in data:
        if isinstance(row, dict):
            row = [row]
        if not isinstance(row, list):
            continue
        buttons: list[dict[str, str]] = []
        for item in row:
            if not isinstance(item, dict):
                continue
            text = str(item.get("text", "")).strip()
            callback_data = item.get("callback_data")
            url = item.get("url")
            if not text or (callback_data is None and url is None):
                continue
            if url is not None:
                buttons.append({"text": text, "url": str(url)})
            else:
                buttons.append({"text": text, "callback_data": str(callback_data)})
        if buttons:
            rows.append(buttons)
    return rows or None


def _build_menu(rows: list[list[dict[str, str]]]) -> InlineKeyboardMarkup:
    inline_keyboard = []
    for row in rows:
        buttons = []
        for item in row:
            if "url" in item:
                buttons.append(InlineKeyboardButton(text=item["text"], url=item["url"]))
            else:
                buttons.append(
                    InlineKeyboardButton(
                        text=item["text"],
                        callback_data=item["callback_data"],
                    )
                )
        if buttons:
            inline_keyboard.append(buttons)
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def main_menu_keyboard(config_json: str | None = None) -> InlineKeyboardMarkup:
    rows = _parse_menu_config(config_json) or MAIN_MENU_BUTTONS
    return _build_menu(rows)
