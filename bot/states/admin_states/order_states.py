from aiogram.fsm.state import StatesGroup, State

class OrderSearchStates(StatesGroup):
    waiting_query = State()