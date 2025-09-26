from aiogram.fsm.state import State, StatesGroup


class CategoryStates(StatesGroup):
    adding = State()


class CategoryEditStates(StatesGroup):
    renaming = State()
    deleting = State()
