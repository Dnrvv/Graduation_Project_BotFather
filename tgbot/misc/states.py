from aiogram.dispatcher.filters.state import StatesGroup, State


class NotifyUsers(StatesGroup):
    GetNotifyMedia = State()
    NotifyApprove = State()
