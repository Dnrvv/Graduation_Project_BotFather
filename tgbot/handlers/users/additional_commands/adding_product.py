from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.infrastructure.database.db_functions import product_functions
from tgbot.keyboards.reply_kbs import reply_approve_kb, main_menu_kb, reply_cancel_kb
from tgbot.middlewares.throttling import rate_limit
from tgbot.misc.states import AddProduct


@rate_limit(1)
async def add_product(message: types.Message, state: FSMContext):
    await state.reset_data()
    await message.answer("Отправьте фото продукта:", reply_markup=reply_cancel_kb)
    await AddProduct.GetProductPhoto.set()


async def get_product_photo(message: types.Message, state: FSMContext):
    photo_file_id = message.photo[-1].file_id
    await state.update_data(photo_file_id=photo_file_id)
    await message.answer("Отправьте category_code:")
    await AddProduct.GetProductCategoryCode.set()


async def get_category_code(message: types.Message, state: FSMContext):
    if len(message.text) > 20:
        await message.answer("Длина category_code должна составлять не более 20 символов!")
        return

    await state.update_data(category_code=message.text)
    await message.answer("Отправьте category_name:")
    await AddProduct.GetProductCategoryName.set()


async def get_category_name(message: types.Message, state: FSMContext):
    if len(message.text) > 20:
        await message.answer("Длина category_name должна составлять не более 25 символов!")
        return

    await state.update_data(category_name=message.text)
    await message.answer("Отправьте название продукта:")
    await AddProduct.GetProductName.set()


async def get_product_name(message: types.Message, state: FSMContext):
    if len(message.text) > 150:
        await message.answer("Длина названия продукта должна составлять не более 150 символов!")
        return

    await state.update_data(product_name=message.text)
    await message.answer("Отправьте описание продукта (максимум 250 символов):")
    await AddProduct.GetProductCaption.set()


async def get_product_caption(message: types.Message, state: FSMContext):
    if len(message.text) > 250:
        await message.answer("Длина описания продукта должна составлять не более 250 символов!")
        return

    await state.update_data(product_caption=message.text)
    await message.answer("Отправьте цену продукта (целочисленное значение, например: 24000 или 24500):")
    await AddProduct.GetProductPrice.set()


async def get_product_price(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Введите целочисленное значение!")
        return

    await state.update_data(product_price=message.text)
    async with state.proxy() as data:
        photo_file_id = data.get("photo_file_id")
        category_code = data.get("category_code")
        category_name = data.get("category_name")
        product_name = data.get("product_name")
        product_caption = data.get("product_caption")
    product_price = message.text
    caption = (f"<b>category_code:</b> {category_code}\n"
               f"<b>category_name:</b> {category_name}\n"
               f"<b>Название:</b> {product_name}\n"
               f"<b>Описание:</b> {product_caption}\n"
               f"<b>Цена:</b> {product_price} сум\n\n"
               f"❗️ Добавить товар в базу данных?")

    await message.answer_photo(photo=photo_file_id, caption=caption, reply_markup=reply_approve_kb)
    await AddProduct.ApproveNewProduct.set()


async def approve_new_product(message: types.Message, state: FSMContext, session: AsyncSession):
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


def register_adding_product(dp: Dispatcher):
    dp.register_message_handler(add_product, commands=["add_product"], is_admin=True, state="*")
    dp.register_message_handler(cancel_adding_product, text="❌ Отмена", state=AddProduct)

    dp.register_message_handler(get_product_photo, content_types=types.ContentType.PHOTO,
                                state=AddProduct.GetProductPhoto)
    dp.register_message_handler(get_category_code, content_types=types.ContentType.TEXT,
                                state=AddProduct.GetProductCategoryCode)
    dp.register_message_handler(get_category_name, content_types=types.ContentType.TEXT,
                                state=AddProduct.GetProductCategoryName)
    dp.register_message_handler(get_product_name, content_types=types.ContentType.TEXT,
                                state=AddProduct.GetProductName)
    dp.register_message_handler(get_product_caption, content_types=types.ContentType.TEXT,
                                state=AddProduct.GetProductCaption)
    dp.register_message_handler(get_product_price, content_types=types.ContentType.TEXT,
                                state=AddProduct.GetProductPrice)
    dp.register_message_handler(approve_new_product, content_types=types.ContentType.TEXT,
                                state=AddProduct.ApproveNewProduct)
