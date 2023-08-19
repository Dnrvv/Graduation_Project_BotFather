from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from tgbot.keyboards.reply_kbs import order_type_kb
from tgbot.middlewares.throttling import rate_limit
from tgbot.misc.states import Order


@rate_limit(1, "main_menu")
async def make_order(message: types.Message, state: FSMContext):
    await state.reset_data()
    await message.answer("Выберите тип заказа:", reply_markup=order_type_kb)
    await Order.GetOrderType.set()


def register_main_menu(dp: Dispatcher):
    dp.register_message_handler(make_order, text="🛒 Сделать заказ", state="*")
