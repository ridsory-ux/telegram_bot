from aiogram.fsm.state import State, StatesGroup

class ScreenState(StatesGroup):
    data = State()

class BalanceState(StatesGroup):
    data = State()

class SuccessState(StatesGroup):
    data = State()
