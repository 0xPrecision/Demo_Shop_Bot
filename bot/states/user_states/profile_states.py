from aiogram.fsm.state import State, StatesGroup

class ProfileStates(StatesGroup):
    create_profile = State()
    editing_field = State()
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_address = State()
    confirm = State()
    editing_name = State()
    editing_phone = State()
    editing_address = State()