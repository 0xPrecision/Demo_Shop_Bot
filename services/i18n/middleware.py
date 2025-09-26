# ## i18n/middleware.py
# from __future__ import annotations
# from typing import Any, Awaitable, Callable, Dict, Optional
# from aiogram import BaseMiddleware
# from aiogram.types import Update
# from .translations import Translator
#
# def _extract_lang_from_update(update: Update) -> Optional[str]:
#     u = update
#     if u.message and u.message.from_user: return u.message.from_user.language_code
#     if u.callback_query and u.callback_query.from_user: return u.callback_query.from_user.language_code
#     if u.inline_query and u.inline_query.from_user: return u.inline_query.from_user.language_code
#     if u.my_chat_member and u.my_chat_member.from_user: return u.my_chat_member.from_user.language_code
#     if u.chat_member and u.chat_member.from_user: return u.chat_member.from_user.language_code
#     return None

# class LocaleMiddleware(BaseMiddleware):
#     def __init__(self, translator: Translator, get_user_locale: Callable[[int], Optional[str]] | None = None):
#         self.tr = translator
#         self.get_user_locale = get_user_locale
#
#     async def __call__(self, handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
#                        event: Update, data: Dict[str, Any]) -> Any:
#         tg_lang = _extract_lang_from_update(event)
#         user_id = (
#             event.message.from_user.id if event.message and event.message.from_user else
#             event.callback_query.from_user.id if event.callback_query and event.callback_query.from_user else
#             None
#         )
#         saved = None
#         if self.get_user_locale and user_id:
#             try: saved = self.get_user_locale(int(user_id))
#             except Exception: saved = None
#
#         loc = self.tr.pick_locale(saved, tg_lang)
#         data["locale"] = loc
#         data["tr"] = self.tr.for_locale(loc)
#         data["trn"] = self.tr.for_locale_plural(loc)
#         return await handler(event, data)


from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict, Optional

from aiogram import BaseMiddleware
from aiogram.types import Update

from services.i18n.translations import Translator


def _tg_lang(update: Update) -> Optional[str]:
    if update.message and update.message.from_user:
        return update.message.from_user.language_code
    if update.callback_query and update.callback_query.from_user:
        return update.callback_query.from_user.language_code
    if update.inline_query and update.inline_query.from_user:
        return update.inline_query.from_user.language_code
    if update.my_chat_member and update.my_chat_member.from_user:
        return update.my_chat_member.from_user.language_code
    if update.chat_member and update.chat_member.from_user:
        return update.chat_member.from_user.language_code
    return None


class LocaleMiddleware(BaseMiddleware):
    def __init__(self, translator: Translator, locale_repo):
        self.tr = translator
        self.repo = locale_repo  # services.LocaleRepo

    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:
        tg = _tg_lang(event)
        uid = None
        if event.message and event.message.from_user:
            uid = event.message.from_user.id
        elif event.callback_query and event.callback_query.from_user:
            uid = event.callback_query.from_user.id

        saved = None
        if uid:
            try:
                saved = await self.repo.get(int(uid))
            except Exception:
                saved = None

        loc = self.tr.pick_locale(saved, tg)

        # кладём в data
        data["loc"] = loc
        data["t"] = self.tr.for_locale(loc)
        data["tn"] = self.tr.for_locale_plural(loc)
        data["translator"] = self.tr
        data["locale_repo"] = self.repo
        return await handler(event, data)
