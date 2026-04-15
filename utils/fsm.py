"""Finite state machine classes module
"""

from aiogram.fsm.state import State, StatesGroup


class NewConfig(StatesGroup):
    device = State()


class NewPayment(StatesGroup):
    payment_image = State()


# Админские состояния
class AdminObfuscation(StatesGroup):
    waiting_params = State()


class AdminBroadcast(StatesGroup):
    waiting_message = State()
    waiting_segment = State()


class AdminSupportReply(StatesGroup):
    waiting_reply = State()


class AdminPromo(StatesGroup):
    waiting_code = State()
    waiting_days = State()


# Состояния пользователя
class UserSupport(StatesGroup):
    waiting_message = State()


class UserRefillBalance(StatesGroup):
    waiting_amount = State()
