from aiogram.fsm.state import StatesGroup, State


class CategoryStates(StatesGroup):
    adding = State()

class CategoryEditStates(StatesGroup):
    renaming = State()
    deleting = State()