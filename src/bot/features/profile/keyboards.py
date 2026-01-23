from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def profile_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⚙️ Settings", callback_data="settings")],
            [InlineKeyboardButton(text="📊 Stats", callback_data="stats")],
            [InlineKeyboardButton(text="🔙 Back", callback_data="main_menu")],
        ]
    )


def settings_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🌐 Language", callback_data="language")],
            [InlineKeyboardButton(text="💱 Currency", callback_data="currency")],
            [InlineKeyboardButton(text="🔔 Notifications", callback_data="notifications")],
            [InlineKeyboardButton(text="🔙 Back", callback_data="profile")],
        ]
    )


def currency_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🇺🇸 USD", callback_data="set_currency_USD")],
            [InlineKeyboardButton(text="🇪🇺 EUR", callback_data="set_currency_EUR")],
            [InlineKeyboardButton(text="🇵🇰 PKR", callback_data="set_currency_PKR")],
            [InlineKeyboardButton(text="🔙 Back", callback_data="settings")],
        ]
    )


def language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="English", callback_data="set_language_en")],
            [InlineKeyboardButton(text="Urdu", callback_data="set_language_ur")],
            [InlineKeyboardButton(text="Hindi", callback_data="set_language_hi")],
            [InlineKeyboardButton(text="🔙 Back", callback_data="settings")],
        ]
    )
