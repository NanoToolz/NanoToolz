from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from src.database import SessionLocal
from src.database.models import SupportTicket
from src.services.settings import get_setting

from .keyboards import support_keyboard
from .messages import support_message

router = Router()


class SupportStates(StatesGroup):
    waiting_subject = State()
    waiting_message = State()


@router.callback_query(F.data == "support")
async def support_callback(query: CallbackQuery) -> None:
    """Support tickets"""
    db = SessionLocal()
    try:
        contact = get_setting(db, "support_contact", "@YourSupport") or "@YourSupport"
    finally:
        db.close()
    await query.message.edit_text(
        support_message(contact),
        parse_mode="HTML",
        reply_markup=support_keyboard(),
    )
    await query.answer()


@router.callback_query(F.data.startswith("support_"))
async def support_category(query: CallbackQuery, state: FSMContext) -> None:
    category = query.data.split("_", 1)[1]
    await state.update_data(category=category)
    await state.set_state(SupportStates.waiting_subject)
    await query.message.edit_text(
        "📝 <b>Support Ticket</b>\\n\\nSend a short subject for your issue.",
        parse_mode="HTML",
    )
    await query.answer()


@router.message(SupportStates.waiting_subject)
async def support_subject(message: Message, state: FSMContext) -> None:
    if message.text and message.text.lower() in {"/cancel", "cancel"}:
        await state.clear()
        await message.answer("❌ Support request cancelled.")
        return
    await state.update_data(subject=message.text or "")
    await state.set_state(SupportStates.waiting_message)
    await message.answer("✍️ Please describe your issue in detail.")


@router.message(SupportStates.waiting_message)
async def support_message_handler(message: Message, state: FSMContext) -> None:
    if message.text and message.text.lower() in {"/cancel", "cancel"}:
        await state.clear()
        await message.answer("❌ Support request cancelled.")
        return

    data = await state.get_data()
    db = SessionLocal()
    try:
        ticket = SupportTicket(
            user_id=message.from_user.id,
            category=data.get("category", "general"),
            subject=data.get("subject", "Support Request"),
            message=message.text or "",
            status="open",
            priority="normal",
        )
        db.add(ticket)
        db.commit()
    finally:
        db.close()

    await state.clear()
    await message.answer("✅ Your ticket has been created. Our team will reply soon.")
