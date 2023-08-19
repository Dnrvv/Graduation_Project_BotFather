from aiogram.dispatcher.filters.state import StatesGroup, State


class NotifyUsers(StatesGroup):
    GetNotifyMedia = State()
    NotifyApprove = State()


class Order(StatesGroup):
    GetOrderType = State()
    GetLocation = State()
    ApproveLocation = State()
    Menu = State()


class AdminActions(StatesGroup):
    GetFile = State()
