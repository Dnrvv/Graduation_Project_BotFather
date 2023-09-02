from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.infrastructure.database.db_functions import product_functions
from tgbot.keyboards.reply_kbs import reply_approve_kb, main_menu_kb
from tgbot.misc.dependences import PRODUCT_NAME_LENGTH, PRODUCT_CAPTION_LENGTH, CATEGORY_CODE_LENGTH, \
    CATEGORY_NAME_LENGTH
from tgbot.misc.states import ModerationActions
from tgbot.services.service_functions import format_number_with_spaces


async def get_product_photo(message: types.Message, state: FSMContext):
    photo_file_id = message.photo[-1].file_id
    await state.update_data(photo_file_id=photo_file_id)
    await message.answer("Отправьте category_code:")
    await ModerationActions.GetProductCategoryCode.set()


async def get_category_code(message: types.Message, state: FSMContext):
    if len(message.text) > CATEGORY_CODE_LENGTH:
        await message.answer(f"❗️ Длина category_code должна составлять не более {CATEGORY_CODE_LENGTH} символов!")
        return

    await state.update_data(category_code=message.text)
    await message.answer("Отправьте category_name:")
    await ModerationActions.GetProductCategoryName.set()


async def get_category_name(message: types.Message, state: FSMContext):
    if len(message.text) > CATEGORY_NAME_LENGTH:
        await message.answer(f"❗️ Длина category_name должна составлять не более {CATEGORY_NAME_LENGTH} символов!")
        return

    await state.update_data(category_name=message.text)
    await message.answer(f"Отправьте название продукта (максимум {PRODUCT_NAME_LENGTH} символов):")
    await ModerationActions.GetProductName.set()


async def get_product_name(message: types.Message, state: FSMContext):
    if len(message.text) > PRODUCT_NAME_LENGTH:
        await message.answer(f"❗️ Длина названия продукта должна составлять не более {PRODUCT_NAME_LENGTH} символов!")
        return

    await state.update_data(product_name=message.text)
    await message.answer(f"Отправьте описание продукта (максимум {PRODUCT_CAPTION_LENGTH} символов):")
    await ModerationActions.GetProductCaption.set()


async def get_product_caption(message: types.Message, state: FSMContext):
    if len(message.text) > PRODUCT_CAPTION_LENGTH:
        await message.answer(f"❗️ Длина описания продукта должна составлять не более {PRODUCT_CAPTION_LENGTH} символов!")
        return

    await state.update_data(product_caption=message.text)
    await message.answer("Отправьте цену продукта (целочисленное значение, например: 24000 или 24500):")
    await ModerationActions.GetProductPrice.set()


async def get_product_price(message: types.Message, state: FSMContext):
    if not message.text.isdigit() or isinstance(message.text, float):
        await message.answer("❗️ Введите целочисленное значение!")
        return

    await state.update_data(product_price=message.text)
    async with state.proxy() as data:
        photo_file_id = data.get("photo_file_id")
        category_code = data.get("category_code")
        category_name = data.get("category_name")
        product_name = data.get("product_name")
        product_caption = data.get("product_caption")
    product_price = int(message.text)
    caption = (f"<b>category_code:</b> {category_code}\n"
               f"<b>category_name:</b> {category_name}\n"
               f"<b>Название:</b> {product_name}\n"
               f"<b>Описание:</b> {product_caption}\n"
               f"<b>Цена:</b> {format_number_with_spaces(product_price)} сум\n\n"
               f"❗️ Добавить товар в базу данных?")

    await message.answer_photo(photo=photo_file_id, caption=caption, reply_markup=reply_approve_kb)
    await ModerationActions.NewProductApprove.set()


async def new_product_approve(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.text == "✅ Да":
        async with state.proxy() as data:
            photo_file_id = data.get("photo_file_id")
            category_code = data.get("category_code")
            category_name = data.get("category_name")
            product_name = data.get("product_name")
            product_caption = data.get("product_caption")
            product_price = data.get("product_price")

        await product_functions.add_product(session, photo_file_id=photo_file_id,
                                            category_code=category_code, category_name=category_name,
                                            product_name=product_name, product_caption=product_caption,
                                            product_price=int(product_price))
        await session.commit()
        await message.answer("✅ Продукт добавлен.", reply_markup=main_menu_kb)
    elif message.text == "❌ Нет":
        await message.answer("Действие отменено.", reply_markup=main_menu_kb)
    else:
        await message.answer("Используйте кнопки ниже:", reply_markup=reply_approve_kb)
        return
    await state.reset_data()
    await state.finish()


async def cancel_adding_product(message: types.Message, state: FSMContext):
    await state.reset_data()
    await state.finish()
    await message.answer("Действие отменено.", reply_markup=main_menu_kb)


def register_add_product(dp: Dispatcher):
    dp.register_message_handler(cancel_adding_product, text="❌ Отмена", is_admin=True, state=ModerationActions)

    dp.register_message_handler(get_product_photo, content_types=types.ContentType.PHOTO,
                                state=ModerationActions.GetProductPhoto)
    dp.register_message_handler(get_category_code, content_types=types.ContentType.TEXT,
                                state=ModerationActions.GetProductCategoryCode)
    dp.register_message_handler(get_category_name, content_types=types.ContentType.TEXT,
                                state=ModerationActions.GetProductCategoryName)
    dp.register_message_handler(get_product_name, content_types=types.ContentType.TEXT,
                                state=ModerationActions.GetProductName)
    dp.register_message_handler(get_product_caption, content_types=types.ContentType.TEXT,
                                state=ModerationActions.GetProductCaption)
    dp.register_message_handler(get_product_price, content_types=types.ContentType.TEXT,
                                state=ModerationActions.GetProductPrice)
    dp.register_message_handler(new_product_approve, content_types=types.ContentType.TEXT, is_admin=True,
                                state=ModerationActions.NewProductApprove)
