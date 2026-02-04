from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from src.database import db

router = Router()

SUPPORT_MENU = (
    "Support Center\n\n"
    "Need help? Create a support ticket and our team will assist you.\n\n"
    "Response time: Usually within 24 hours"
)


class TicketStates(StatesGroup):
    waiting_for_subject = State()
    waiting_for_message = State()
    waiting_for_reply = State()


def get_support_menu_keyboard(has_tickets: bool = False) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="Create Ticket", callback_data="create_ticket")],
    ]

    if has_tickets:
        buttons.append([InlineKeyboardButton(text="My Tickets", callback_data="my_tickets")])

    buttons.append([InlineKeyboardButton(text="Back", callback_data="back_main")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.callback_query(F.data == "support")
async def support_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    db.get_or_create_user(user_id, callback.from_user.username, callback.from_user.first_name)

    tickets = db.get_user_tickets(user_id)
    has_tickets = len(tickets) > 0

    keyboard = get_support_menu_keyboard(has_tickets)

    try:
        await callback.message.edit_text(SUPPORT_MENU, reply_markup=keyboard, parse_mode="Markdown")
    except Exception:
        await callback.message.delete()
        await callback.message.answer(SUPPORT_MENU, reply_markup=keyboard, parse_mode="Markdown")

    await callback.answer()


@router.callback_query(F.data == "create_ticket")
async def create_ticket_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(TicketStates.waiting_for_subject)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Cancel", callback_data="support")]
    ])

    await callback.message.answer("Enter ticket subject (brief description of your issue):", reply_markup=keyboard)
    await callback.answer()


@router.message(TicketStates.waiting_for_subject)
async def receive_subject(message: Message, state: FSMContext):
    subject = message.text.strip()

    if len(subject) < 5:
        await message.answer("Subject too short. Please provide more detail.")
        return

    await state.update_data(subject=subject)
    await state.set_state(TicketStates.waiting_for_message)

    await message.answer("Now describe your issue in detail:")


@router.message(TicketStates.waiting_for_message)
async def receive_message(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()

    ticket = db.create_ticket(user_id, data['subject'])
    db.add_ticket_message(ticket['id'], user_id, message.text, is_admin=False)

    await state.clear()

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="View Ticket", callback_data=f"view_my_ticket_{ticket['id']}")],
        [InlineKeyboardButton(text="Back to Support", callback_data="support")]
    ])

    await message.answer(
        f"Ticket #{ticket['id']} Created\n\n"
        f"Subject: {data['subject']}\n\n"
        "Our team will respond as soon as possible.",
        reply_markup=keyboard
    )


@router.callback_query(F.data == "my_tickets")
async def my_tickets(callback: CallbackQuery):
    user_id = callback.from_user.id
    tickets = db.get_user_tickets(user_id)

    if not tickets:
        await callback.answer("No tickets found", show_alert=True)
        return

    text = "Your Support Tickets\n\n"
    buttons = []

    for ticket in tickets[:10]:
        status_icon = "" if ticket['status'] == 'open' else ""
        text += f"#{ticket['id']} - {ticket['subject'][:25]}... ({ticket['status']})\n"
        buttons.append([InlineKeyboardButton(
            text=f"{status_icon} #{ticket['id']} - {ticket['subject'][:20]}",
            callback_data=f"view_my_ticket_{ticket['id']}"
        )])

    buttons.append([InlineKeyboardButton(text="Back", callback_data="support")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data.startswith("view_my_ticket_"))
async def view_my_ticket(callback: CallbackQuery):
    try:
        ticket_id = int(callback.data.split("_")[3])
    except (ValueError, IndexError):
        await callback.answer("Invalid ticket", show_alert=True)
        return

    ticket = db.get_ticket(ticket_id)

    if not ticket:
        await callback.answer("Ticket not found", show_alert=True)
        return

    text = f"Ticket #{ticket['id']}\n\nSubject: {ticket['subject']}\nStatus: {ticket['status']}\n\nMessages:\n"

    messages = ticket.get('ticket_messages', [])
    for msg in messages[-5:]:
        sender = "Support" if msg['is_admin'] else "You"
        text += f"\n[{sender}]: {msg['message'][:150]}"

    buttons = []
    if ticket['status'] != 'closed':
        buttons.append([InlineKeyboardButton(text="Reply", callback_data=f"reply_my_ticket_{ticket_id}")])

    buttons.append([InlineKeyboardButton(text="Back", callback_data="my_tickets")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data.startswith("reply_my_ticket_"))
async def reply_to_ticket_start(callback: CallbackQuery, state: FSMContext):
    try:
        ticket_id = int(callback.data.split("_")[3])
    except (ValueError, IndexError):
        await callback.answer("Invalid ticket", show_alert=True)
        return

    await state.update_data(ticket_id=ticket_id)
    await state.set_state(TicketStates.waiting_for_reply)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Cancel", callback_data=f"view_my_ticket_{ticket_id}")]
    ])

    await callback.message.answer("Enter your reply:", reply_markup=keyboard)
    await callback.answer()


@router.message(TicketStates.waiting_for_reply)
async def receive_reply(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    ticket_id = data['ticket_id']

    db.add_ticket_message(ticket_id, user_id, message.text, is_admin=False)

    await state.clear()

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="View Ticket", callback_data=f"view_my_ticket_{ticket_id}")],
        [InlineKeyboardButton(text="Back to Support", callback_data="support")]
    ])

    await message.answer("Reply sent!", reply_markup=keyboard)
