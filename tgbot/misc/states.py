from aiogram.dispatcher.filters.state import StatesGroup, State


class NotifyUsers(StatesGroup):
    GetNotifyMedia = State()
    NotifyApprove = State()


class Order(StatesGroup):
    OrderType = State()


class AdminActions(StatesGroup):
    GetFile = State()
