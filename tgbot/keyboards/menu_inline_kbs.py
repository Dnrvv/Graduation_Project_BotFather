from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.infrastructure.database.db_functions import product_functions

cafe_menu_cd = CallbackData("show_menu", "level", "category", "product_id")
interaction_with_item_cd = CallbackData("action", "product_id")
order_products_cd = CallbackData("order", "product_id", "category", "quantity_counter")

cart_actions_cd = CallbackData("cart", "action")
cart_products_cd = CallbackData("cart", "product_id", "category", "product_quantity")


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


async def items_keyboard(category, session: AsyncSession):
    current_level = 1
    keyboard = InlineKeyboardMarkup(row_width=2)
    products = await product_functions.get_products(session, category)
    for product in products:
        if product.is_hidden:
            continue
        button_text = f"{product.product_name}"
        callback_data = make_callback_data(level=current_level + 1,
                                           category=category,
                                           product_id=f"{product.product_id}")

        keyboard.insert(
            InlineKeyboardButton(text=button_text, callback_data=callback_data)
        )

    keyboard.row(
        InlineKeyboardButton(text="⬅️ Назад",
                             callback_data=make_callback_data(level=current_level - 1,
                                                              category=category))
    )
    return keyboard


async def item_keyboard(category, product_id, session: AsyncSession, quantity_counter=1):
    current_level = 2
    keyboard = InlineKeyboardMarkup(row_width=3)
    product = await product_functions.get_product(session, product_id=product_id)
    keyboard.row(
        InlineKeyboardButton(text="-",
                             callback_data=order_products_cd.new(product_id=product_id, category=category,
                                                                 quantity_counter=f"{quantity_counter - 1}")),

        InlineKeyboardButton(text=f"{quantity_counter}",
                             callback_data=order_products_cd.new(product_id="counter", category="category",
                                                                 quantity_counter=f"{quantity_counter}")),

        InlineKeyboardButton(text="+",
                             callback_data=order_products_cd.new(product_id=product_id, category=category,
                                                                 quantity_counter=f"{quantity_counter + 1}"))
    )
    keyboard.row(InlineKeyboardButton(text="📥 В корзину", callback_data=make_callback_data(level=current_level + 1,
                                                                                           category=category,
                                                                                           product_id=product_id)))
    keyboard.row(InlineKeyboardButton(text="⬅️ Назад", callback_data=make_callback_data(level=current_level - 1,
                                                                                        category=category)))
    return keyboard


async def cart_keyboard(category, selected_products: dict, session: AsyncSession):
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
    )

    for product_id, product_quantity in selected_products.items():
        product = await product_functions.get_product(session, product_id=int(product_id))
        keyboard.row(
            InlineKeyboardButton(text="-", callback_data=cart_products_cd.new(product_id=product.product_id,
                                                                              category=category,
                                                                              product_quantity=f"{product_quantity - 1}")),
            InlineKeyboardButton(text=f"{product.product_name}",
                                 callback_data=cart_products_cd.new(product_id="product_name",
                                                                    category=category,
                                                                    product_quantity=f"{product_quantity}")
                                 ),
            InlineKeyboardButton(text="+", callback_data=cart_products_cd.new(product_id=product.product_id,
                                                                              category=category,
                                                                              product_quantity=f"{product_quantity + 1}"))
        )
    return keyboard
