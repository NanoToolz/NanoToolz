from typing import Any, Callable, Dict, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from aiogram.enums import ChatAction
import asyncio
import random

class TypingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        
        chat_id = None
        if isinstance(event, Message):
            chat_id = event.chat.id
        elif isinstance(event, CallbackQuery) and event.message:
            chat_id = event.message.chat.id
            
        if chat_id:
            # Simulate "human" processing delay with typing indicator
            # Short delay for callbacks (0.3-0.7s), longer for messages (0.8-1.5s)
            delay = random.uniform(0.3, 0.7) if isinstance(event, CallbackQuery) else random.uniform(0.8, 1.5)
            
            try:
                # We don't await this so it runs in background/doesn't block completely? 
                # Actually for typing effect we want to wait a bit.
                if event.bot:
                    await event.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
            except Exception:
                pass
                
            await asyncio.sleep(delay)
            
        return await handler(event, data)