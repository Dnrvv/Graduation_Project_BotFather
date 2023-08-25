from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from tgbot.keyboards.reply_kbs import main_menu_kb, order_type_kb, reply_approve_kb, get_contact_kb, payment_type_kb, \
    reply_cancel_kb
from tgbot.middlewares.throttling import rate_limit


@rate_limit(1, text="Пожалуйста, не используйте команды слишком часто.")
async def bot_echo_all(message: types.Message, state: FSMContext):
    state_name = await state.get_state()
    if not state_name:
        await state.reset_data()
        await message.answer("Некорректный ввод. Используйте меню:", reply_markup=main_menu_kb)
        return

    if "Order" in state_name:
        if "GetOrderType" in state_name:
            await message.answer("Используйте кнопки ниже:", reply_markup=order_type_kb)
        elif "GetLocation" in state_name:
            await message.answer("Используйте кнопки ниже, либо отправьте геопозицию.")
        elif "ApproveLocation" in state_name:
            await message.answer("Используйте кнопки ниже:", reply_markup=reply_approve_kb)
        elif "Menu" in state_name:
            await message.answer("Используйте меню для заказа.", reply_markup=reply_cancel_kb)
        elif "GetContact" in state_name:
            await message.answer("Используйте кнопки ниже, либо отправьте номер телефона в формате "
                                 "<b>+998 ** *** ** **</b>.", reply_markup=get_contact_kb)
        elif "GetPaymentType" in state_name:
            await message.answer("Используйте кнопки ниже:", reply_markup=payment_type_kb)
        elif "ApproveOrder" in state_name:
            await message.answer("Используйте кнопки ниже:", reply_markup=payment_type_kb)
    elif "Feedback" in state_name:
        await message.answer("Пожалуйста, отправьте текст.", reply_markup=reply_cancel_kb)


def register_echo(dp: Dispatcher):
    dp.register_message_handler(bot_echo_all, content_types=types.ContentTypes.ANY, state="*")
