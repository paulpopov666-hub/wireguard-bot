"""Finite state machine classes module
"""

from aiogram.fsm.state import State, StatesGroup


class NewConfig(StatesGroup):
    device = State()


class NewPayment(StatesGroup):
    payment_image = State()


# Админские состояния
class AdminBroadcast(StatesGroup):
    waiting_message = State()
    waiting_segment = State()


# Состояния пользователя
class UserSupport(StatesGroup):
    waiting_message = State()


class UserRefillBalance(StatesGroup):
    waiting_amount = State()
