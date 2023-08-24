from aiogram.dispatcher.filters.state import StatesGroup, State


class NotifyUsers(StatesGroup):
    GetNotifyMedia = State()
    NotifyApprove = State()


class Feedback(StatesGroup):
    GetFeedbackText = State()


class Order(StatesGroup):
    GetOrderType = State()
    GetLocation = State()
    ApproveLocation = State()
    Menu = State()
    GetContact = State()
    GetPaymentType = State()
    ApproveOrder = State()


class AdminActions(StatesGroup):
    GetTOUFile = State()


class AddProduct(StatesGroup):
    GetProductPhoto = State()

    GetProductCategoryCode = State()
    GetProductCategoryName = State()

    GetProductName = State()
    GetProductCaption = State()
    GetProductPrice = State()

    ApproveNewProduct = State()
