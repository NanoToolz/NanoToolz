from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

HELP_MENU = "Help Center\n\nNeed assistance? Choose a topic:"

HELP_SHOP = (
    "How to Shop\n\n"
    "1. Browse Catalog - View all categories\n"
    "2. Select Product - Click on product to see details\n"
    "3. Add to Cart - Click 'Add to Cart' button\n"
    "4. View Cart - Check your items\n"
    "5. Checkout - Choose payment method\n"
    "6. Confirm - Complete your order\n\n"
    "Your purchased items will be delivered instantly!"
)

HELP_PAYMENT = (
    "Payment Methods\n\n"
    "We accept:\n\n"
    "Account Credits\n"
    "   - Top up your account balance\n"
    "   - Pay directly from wallet\n\n"
    "Credit/Debit Card (Mock)\n"
    "   - Secure payment processing\n"
    "   - Instant confirmation\n\n"
    "Crypto (Mock)\n"
    "   - Bitcoin, Ethereum, USDT\n"
    "   - Fast processing\n\n"
    "All payments are secure."
)

HELP_DELIVERY = (
    "Delivery Information\n\n"
    "Order Processing:\n"
    "- Instant - Most items delivered immediately\n"
    "- 24 hours - Some items within 24 hours\n\n"
    "Delivery Methods:\n"
    "- Chat - Direct message in Telegram\n"
    "- Keys displayed after purchase\n\n"
    "Check your order status in Profile > Order History"
)

HELP_TIERS = (
    "Loyalty Tiers\n\n"
    "Bronze (0+)\n"
    "   - Start your journey\n\n"
    "Silver ($50+)\n"
    "   - 5% discount on all purchases\n\n"
    "Gold ($200+)\n"
    "   - 10% discount on all purchases\n\n"
    "Platinum ($500+)\n"
    "   - 15% discount + priority support\n\n"
    "Spend more to unlock higher tiers!"
)


def get_help_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="How to Shop", callback_data="help_shop")],
        [InlineKeyboardButton(text="Payment Methods", callback_data="help_payment")],
        [InlineKeyboardButton(text="Delivery Info", callback_data="help_delivery")],
        [InlineKeyboardButton(text="Loyalty Tiers", callback_data="help_tiers")],
        [InlineKeyboardButton(text="Back", callback_data="back_main")]
    ])


def get_back_to_help_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Back", callback_data="help_main")]
    ])


@router.callback_query(F.data == "help_main")
async def help_menu(callback: CallbackQuery):
    keyboard = get_help_menu_keyboard()
    await callback.message.edit_text(HELP_MENU, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "help_shop")
async def help_shop(callback: CallbackQuery):
    keyboard = get_back_to_help_keyboard()
    await callback.message.edit_text(HELP_SHOP, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "help_payment")
async def help_payment(callback: CallbackQuery):
    keyboard = get_back_to_help_keyboard()
    await callback.message.edit_text(HELP_PAYMENT, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "help_delivery")
async def help_delivery(callback: CallbackQuery):
    keyboard = get_back_to_help_keyboard()
    await callback.message.edit_text(HELP_DELIVERY, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "help_tiers")
async def help_tiers(callback: CallbackQuery):
    keyboard = get_back_to_help_keyboard()
    await callback.message.edit_text(HELP_TIERS, reply_markup=keyboard)
    await callback.answer()
