from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.infrastructure.database.db_functions import product_functions

menu_callback = CallbackData("show_menu", "level", "category", "subcategory", "product_id")
interaction_with_item_callback = CallbackData("action", "product_id")


def make_callback_data(level, category="0", subcategory="0", product_id="0"):
    return menu_callback.new(level=level, category=category,
                             subcategory=subcategory, product_id=product_id)


async def categories_keyboard(session: AsyncSession):
    current_level = 0
    markup = InlineKeyboardMarkup(row_width=2)
    categories = await product_functions.get_categories(session)

    for category in categories:
        button_text = f"{category.category_name}"
        callback_data = make_callback_data(level=current_level + 1,
                                           category=category.category_code)
        markup.insert(
            InlineKeyboardButton(text=button_text, callback_data=callback_data)
        )
    markup.row(
        # level = ... Мы передали тот уровень НА КОТОРЫЙ хотим переместиться
        InlineKeyboardButton(text="⬅️ Главное меню",
                             callback_data=make_callback_data(level=current_level - 1)),
    )
    return markup


async def subcategories_keyboard(category, session: AsyncSession):
    current_level = 1
    markup = InlineKeyboardMarkup(row_width=2)
    subcategories = await product_functions.get_subcategories(session)
    for subcategory in subcategories:
        button_text = f"{subcategory.subcategory_name}"
        callback_data = make_callback_data(level=current_level + 1,
                                           category=category,
                                           subcategory=subcategory.subcategory_code)
        markup.insert(
            InlineKeyboardButton(text=button_text, callback_data=callback_data)
        )
    markup.row(
        # level = ... Мы передали тот уровень НА КОТОРЫЙ хотим переместиться
        InlineKeyboardButton(text="⬅️ Назад",
                             callback_data=make_callback_data(level=current_level - 1)),
        InlineKeyboardButton(text="⏺ Главное меню",
                             callback_data=make_callback_data(level=current_level - 2))
    )
    return markup


async def items_keyboard(category, subcategory, session: AsyncSession):
    current_level = 2
    markup = InlineKeyboardMarkup(row_width=2)
    products = await product_functions.get_products(session, category, subcategory)
    for product in products:
        button_text = f"{product.product_name}"
        callback_data = make_callback_data(level=current_level + 1,
                                           category=category,
                                           subcategory=subcategory,
                                           product_id=product.product_id)

        markup.insert(
            InlineKeyboardButton(text=button_text, callback_data=callback_data)
        )
    markup.row(
        # level = ... Мы передали тот уровень НА КОТОРЫЙ хотим переместиться
        InlineKeyboardButton(text="⬅️ Назад",
                             callback_data=make_callback_data(level=current_level - 1,
                                                              category=category)),
        InlineKeyboardButton(text="⏺ Главное меню",
                             callback_data=make_callback_data(level=current_level - 3))
    )
    return markup


async def item_keyboard(category, subcategory, product_id, session: AsyncSession):
    current_level = 3
    markup = InlineKeyboardMarkup(row_width=3)
    product = await product_functions.get_product(session, product_id=product_id)
    markup.row(
        InlineKeyboardButton(text="+", callback_data=interaction_with_item_callback.new(product_id=product_id)),
        InlineKeyboardButton(text="счетчик", callback_data=interaction_with_item_callback.new(product_id=product_id)),
        InlineKeyboardButton(text="-", callback_data=interaction_with_item_callback.new(product_id=product_id))
    )
    markup.row(
        InlineKeyboardButton(text="⬅️ Назад",
                             callback_data=make_callback_data(level=current_level - 1,
                                                              category=category,
                                                              subcategory=subcategory)),
    )
    return markup
