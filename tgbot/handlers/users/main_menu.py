from aiogram import types
from aiogram.dispatcher import FSMContext

from tgbot.keyboards.reply_kbs import order_type_kb, main_menu_kb
from tgbot.middlewares.throttling import rate_limit
from tgbot.misc.states import Order


@rate_limit(1, "main_menu")
async def make_order(message: types.Message, state: FSMContext):
    await state.reset_data()
    await message.answer("Выберите тип заказа:", reply_markup=order_type_kb)
    await Order.OrderType.set()


@rate_limit(1, "order")
async def get_order_type(message: types.Message, state: FSMContext):
    if message.text == "🛵 Доставка":
        #
    elif message.text == "🚶 Самовывоз":
        # dsfasd
    elif message.text == "❌ Отмена":
        await message.answer("❌ Заказ отменён.", reply_markup=main_menu_kb)
        await state.reset_data()
        await state.finish()
    else:
        await message.answer("Некорректный ввод. Используйте кнопки ниже:", reply_markup=order_type_kb)
