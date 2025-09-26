from aiogram.fsm.state import State, StatesGroup


class OrderStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_address = State()
    waiting_for_comment = State()
    choosing_payment = State()
    choosing_delivery = State()
    use_profile_choice = State()
    choose_address_option = State()
    confirm = State()
    editing_field = State()
    editing_name = State()
    editing_phone = State()
    editing_address = State()
    editing_payment = State()
    editing_delivery = State()
    editing_comment = State()
