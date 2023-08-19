from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.infrastructure.database.db_functions import product_functions

cafe_menu_cd = CallbackData("show_menu", "level", "category", "product_id")
interaction_with_item_cd = CallbackData("action", "product_id")
order_products_cd = CallbackData("order", "product_id")


def make_callback_data(level, category="0", product_id="0", quantity_counter=0):
    return cafe_menu_cd.new(level=level, category=category, product_id=product_id)


async def categories_keyboard(session: AsyncSession):
    current_level = 0
    keyboard = InlineKeyboardMarkup(row_width=2)
    categories = await product_functions.get_categories(session)

    for category in categories:
        button_text = f"{category.category_name}"
        callback_data = make_callback_data(level=current_level + 1,
                                           category=category.category_code)
        keyboard.insert(InlineKeyboardButton(text=button_text, callback_data=callback_data))
    # keyboard.row(InlineKeyboardButton(text="❌ Отменить заказ",
    #                                 callback_data=make_callback_data(level=current_level - 1)),
    #            )
    # level = ... Мы передали тот уровень НА КОТОРЫЙ хотим переместиться
    keyboard.row(InlineKeyboardButton(text="📥 Корзина", callback_data="asdf"))
    return keyboard


# async def subcategories_keyboard(category, session: AsyncSession):
#     current_level = 1
#     markup = InlineKeyboardMarkup(row_width=2)
#     subcategories = await product_functions.get_subcategories(session)
#     for subcategory in subcategories:
#         button_text = f"{subcategory.subcategory_name}"
#         callback_data = make_callback_data(level=current_level + 1,
#                                            category=category,
#                                            subcategory=subcategory.subcategory_code)
#         markup.insert(
#             InlineKeyboardButton(text=button_text, callback_data=callback_data)
#         )
#     markup.row(
#         # level = ... Мы передали тот уровень НА КОТОРЫЙ хотим переместиться
#         InlineKeyboardButton(text="⬅️ Назад",
#                              callback_data=make_callback_data(level=current_level - 1)),
#         InlineKeyboardButton(text="⏺ Главное меню",
#                              callback_data=make_callback_data(level=current_level - 2))
#     )
#     return markup


async def items_keyboard(category, session: AsyncSession):
    current_level = 1
    keyboard = InlineKeyboardMarkup(row_width=2)
    products = await product_functions.get_products(session, category)
    for product in products:
        button_text = f"{product.product_name}"
        callback_data = make_callback_data(level=current_level + 1,
                                           category=category,
                                           product_id=product.product_id)

        keyboard.insert(
            InlineKeyboardButton(text=button_text, callback_data=callback_data)
        )

    keyboard.row(
        # level = ... Мы передали тот уровень НА КОТОРЫЙ хотим переместиться
        InlineKeyboardButton(text="⬅️ Назад",
                             callback_data=make_callback_data(level=current_level - 1,
                                                              category=category))
        # InlineKeyboardButton(text="⏺ К оглавлению",
        #                      callback_data=make_callback_data(level=current_level - 3))
    )
    return keyboard


async def item_keyboard(category, product_id, quantity_counter, session: AsyncSession):
    current_level = 2
    keyboard = InlineKeyboardMarkup(row_width=3)
    product = await product_functions.get_product(session, product_id=product_id)
    keyboard.row(
        InlineKeyboardButton(text="+", callback_data=interaction_with_item_cd.new(product_id=product_id)),
        InlineKeyboardButton(text="счетчик", callback_data=interaction_with_item_cd.new(product_id=product_id)),
        InlineKeyboardButton(text="-", callback_data=interaction_with_item_cd.new(product_id=product_id))
    )
    keyboard.row(InlineKeyboardButton(text="📥 В корзину", callback_data=make_callback_data(level=current_level + 1,
                                                                                           category=category)))
    keyboard.row(InlineKeyboardButton(text="⬅️ Назад", callback_data=make_callback_data(level=current_level - 1,
                                                                                        category=category)))
    return keyboard
