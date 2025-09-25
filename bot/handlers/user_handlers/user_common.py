from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.keyboards.user.user_main_menu import main_menu
router = Router()

@router.message(F.text == '/start')
async def start_cmd(message: Message, t, state: FSMContext, **_):
    """
    Handler for the /start command — displays the inline main menu.
	"""
    await state.clear()
    await message.answer(t('user_common.messages.b-dobro-pozhalovat-v-magazin-b'), reply_markup=main_menu(t))