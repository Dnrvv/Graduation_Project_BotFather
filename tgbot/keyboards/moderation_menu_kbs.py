from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.infrastructure.database.db_functions import product_functions


moderation_menu_cd = CallbackData("show_menu", "level", "category", "product_id")
mod_interaction_with_item_cd = CallbackData("action", "product_id")
product_moderation_cd = CallbackData("product_mod", "product_id", "category", "action")
cart_actions_cd = CallbackData("cart", "action")


moderation_mm_cd = CallbackData("moderation", "action")
moderation_mm_actions = ["add_product", "edit_product", "cancel"]
moderation_mm_kb = InlineKeyboardMarkup(
    row_width=2,
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Добавить продукт",
                                 callback_data=moderation_mm_cd.new(action="add_product"))
        ],
        [
            InlineKeyboardButton(text="Редактировать продукт",
                                 callback_data=moderation_mm_cd.new(action="edit_product"))
        ],
        [
            InlineKeyboardButton(text="↩️ Отмена",
                                 callback_data=moderation_mm_cd.new(action="cancel"))
        ]
    ]
)


def make_callback_data(level, product_id="0", category="0"):
    return moderation_menu_cd.new(level=level, category=category, product_id=product_id)


async def moderation_categories_kb(session: AsyncSession):
    current_level = 0
    keyboard = InlineKeyboardMarkup(row_width=2)
    categories_dict = await product_functions.get_all_categories(session)

    for category_code, category_name in categories_dict.items():
        button_text = f"{category_name}"
        callback_data = make_callback_data(level=current_level + 1,
                                           category=category_code)
        keyboard.insert(InlineKeyboardButton(text=button_text, callback_data=callback_data))

    keyboard.row(InlineKeyboardButton(text="⬅️ Назад",
                                      callback_data=make_callback_data(level=current_level - 1)),)
    return keyboard


async def moderation_items_kb(category, session: AsyncSession):
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
        InlineKeyboardButton(text="⬅️ Назад",
                             callback_data=make_callback_data(level=current_level - 1,
                                                              category=category))
    )
    return keyboard


async def moderation_item_kb(category, product_id, session: AsyncSession):
    current_level = 2
    keyboard = InlineKeyboardMarkup(row_width=3)
    product_obj = await product_functions.get_product(session, product_id=product_id)
    text = "Скрыть продукт"
    action = "hide_product"
    if product_obj.is_hidden:
        text = "Восстановить продукт"
        action = "reveal_product"

    buttons = [
        InlineKeyboardButton(text="Фото",
                             callback_data=product_moderation_cd.new(product_id=product_id, category=category,
                                                                     action="edit_photo")),
        InlineKeyboardButton(text="Превью",
                             callback_data=product_moderation_cd.new(product_id=product_id, category=category,
                                                                     action="edit_photo_web_link")),
        InlineKeyboardButton(text="Название",
                             callback_data=product_moderation_cd.new(product_id=product_id, category=category,
                                                                     action="edit_name")),
        InlineKeyboardButton(text="Описание",
                             callback_data=product_moderation_cd.new(product_id=product_id,
                                                                     category=category,
                                                                     action="edit_caption")),
        InlineKeyboardButton(text="Цена",
                             callback_data=product_moderation_cd.new(product_id=product_id,
                                                                     category=category,
                                                                     action="edit_price")),
        InlineKeyboardButton(text=f"{text}",
                             callback_data=product_moderation_cd.new(product_id=product_id,
                                                                     category=category,
                                                                     action=f"{action}"))

    ]
    keyboard.row(buttons[0], buttons[1])
    keyboard.row(buttons[2], buttons[3])
    keyboard.row(buttons[4])
    keyboard.row(buttons[5])

    keyboard.row(InlineKeyboardButton(text="⬅️ Назад", callback_data=make_callback_data(level=current_level - 1,
                                                                                        category=category)))
    return keyboard
