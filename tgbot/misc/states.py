from aiogram.dispatcher.filters.state import StatesGroup, State


class NotifyUsers(StatesGroup):
    GetNotifyMedia = State()
    NotifyApprove = State()


class ReplenishBalance(StatesGroup):
    GetPaymentMethod = State()
    GetReplenishAmount = State()
    Checkout = State()


class Feedback(StatesGroup):
    GetFeedbackText = State()


class Order(StatesGroup):
    GetLocation = State()
    ApproveLocation = State()
    Menu = State()
    GetContact = State()
    OrderApprove = State()


class AdminActions(StatesGroup):
    GetTOUFile = State()


class ModerationActions(StatesGroup):
    GetAction = State()
    ProductsMenu = State()

    GetProductPhoto = State()
    GetProductPhotoWebLink = State()
    GetProductCategoryCode = State()
    GetProductCategoryName = State()
    GetProductName = State()
    GetProductCaption = State()
    GetProductPrice = State()
    NewProductApprove = State()

    EditProduct = State()
    EditProductApprove = State()

    GetProductId = State()
    HideProductApprove = State()
    RevealProductApprove = State()
