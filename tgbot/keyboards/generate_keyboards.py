from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.infrastructure.database.db_functions import product_functions

cafe_menu_cd = CallbackData("show_menu", "level", "category", "product_id")
interaction_with_item_cd = CallbackData("action", "product_id")
order_products_cd = CallbackData("order", "product_id", "category", "quantity_counter")
cart_actions_cd = CallbackData("cart", "action")


def make_callback_data(level, product_id="0", category="0"):
    return cafe_menu_cd.new(level=level, category=category, product_id=product_id)


async def categories_keyboard(session: AsyncSession):
    current_level = 0
    keyboard = InlineKeyboardMarkup(row_width=2)
    categories_dict = await product_functions.get_categories(session)

    for category_code, category_name in categories_dict.items():
        button_text = f"{category_name}"
        callback_data = make_callback_data(level=current_level + 1,
                                           category=category_code)
        keyboard.insert(InlineKeyboardButton(text=button_text, callback_data=callback_data))

    keyboard.row(InlineKeyboardButton(text="📥 Корзина",
                                      callback_data=make_callback_data(level=current_level+4)))
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
                                           product_id=f"{product.product_id}")

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


async def item_keyboard(category, product_id, session: AsyncSession, quantity_counter=1):
    current_level = 2
    keyboard = InlineKeyboardMarkup(row_width=3)
    product = await product_functions.get_product(session, product_id=product_id)
    keyboard.row(
        InlineKeyboardButton(text="➖",
                             callback_data=order_products_cd.new(product_id=product_id, category=category,
                                                                 quantity_counter=f"{quantity_counter - 1}")),

        InlineKeyboardButton(text=f"{quantity_counter}",
                             callback_data=order_products_cd.new(product_id="counter", category="category",
                                                                 quantity_counter=f"{quantity_counter}")),

        InlineKeyboardButton(text="➕",
                             callback_data=order_products_cd.new(product_id=product_id, category=category,
                                                                 quantity_counter=f"{quantity_counter + 1}"))
    )
    keyboard.row(InlineKeyboardButton(text="📥 В корзину", callback_data=make_callback_data(level=current_level + 1,
                                                                                           category=category,
                                                                                           product_id=product_id)))
    keyboard.row(InlineKeyboardButton(text="⬅️ Назад", callback_data=make_callback_data(level=current_level - 1,
                                                                                        category=category)))
    return keyboard


async def cart_keyboard(category, session: AsyncSession):
    # Сюда еще надо загнать список selected_products
    current_level = 4
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.row(
        InlineKeyboardButton(text="⬅️ Назад",
                             callback_data=make_callback_data(level=current_level - 4,
                                                              category=category)),
        InlineKeyboardButton(text="🛵 Оформить заказ",
                             callback_data=cart_actions_cd.new(action="order_checkout"))
    )
    keyboard.row(
        InlineKeyboardButton(text="🧹 Очистить корзину",
                             callback_data=cart_actions_cd.new(action="clear_cart"))
        # InlineKeyboardButton(text="⏰ Время доставки",
        #                      callback_data=cart_actions_cd.new(action="set_delivery_time"))
    )
    return keyboard
