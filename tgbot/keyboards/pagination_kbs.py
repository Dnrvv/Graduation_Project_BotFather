from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

orders_pagination_call_cd = CallbackData("orders_paginator", "key", "page")


def user_orders_kb(orders_count: int, page: int = 1):
    key = "user_orders"
    keyboard = InlineKeyboardMarkup(row_width=2)
    MAX_ITEMS_PER_PAGE = 1

    pages_buttons = list()
    if orders_count > MAX_ITEMS_PER_PAGE:
        first_page = 1

        if orders_count % MAX_ITEMS_PER_PAGE == 0:
            max_page = orders_count // MAX_ITEMS_PER_PAGE
        else:
            max_page = orders_count // MAX_ITEMS_PER_PAGE + 1

        previous_page = page - 1
        previous_page_text = f"⬅️"

        if previous_page >= first_page:
            pages_buttons.append(
                InlineKeyboardButton(
                    text=previous_page_text,
                    callback_data=orders_pagination_call_cd.new(key=key, page=previous_page)))
        else:
            pages_buttons.append(
                InlineKeyboardButton(
                    text="⏺",
                    callback_data=orders_pagination_call_cd.new(key=key, page="begin_empty")))

        pages_buttons.append(
            InlineKeyboardButton(
                text=f"{page}/{max_page}",
                callback_data=orders_pagination_call_cd.new(key=key, page="current_page")))

        next_page = page + 1
        next_page_text = f"➡️"

        if next_page <= max_page:
            pages_buttons.append(
                InlineKeyboardButton(
                    text=next_page_text,
                    callback_data=orders_pagination_call_cd.new(key=key, page=next_page)))
        else:
            pages_buttons.append(
                InlineKeyboardButton(
                    text="⏺",
                    callback_data=orders_pagination_call_cd.new(key=key, page="end_empty")))

    keyboard.row(*pages_buttons)
    keyboard.row(InlineKeyboardButton(text="❌ Закрыть",
                                      callback_data=orders_pagination_call_cd.new(key=key, page="cancel")))
    return keyboard


feedbacks_pagination_call_cd = CallbackData("feedbacks_paginator", "key", "page")


def feedbacks_kb(feedbacks_count: int, page: int = 1):
    key = "feedbacks"
    keyboard = InlineKeyboardMarkup(row_width=2)
    MAX_ITEMS_PER_PAGE = 1

    pages_buttons = list()
    if feedbacks_count > MAX_ITEMS_PER_PAGE:
        first_page = 1

        if feedbacks_count % MAX_ITEMS_PER_PAGE == 0:
            max_page = feedbacks_count // MAX_ITEMS_PER_PAGE
        else:
            max_page = feedbacks_count // MAX_ITEMS_PER_PAGE + 1

        previous_page = page - 1
        previous_page_text = f"⬅️"

        if previous_page >= first_page:
            pages_buttons.append(
                InlineKeyboardButton(
                    text=previous_page_text,
                    callback_data=feedbacks_pagination_call_cd.new(key=key, page=previous_page)))
        else:
            pages_buttons.append(
                InlineKeyboardButton(
                    text="⏺",
                    callback_data=feedbacks_pagination_call_cd.new(key=key, page="begin_empty")))

        pages_buttons.append(
            InlineKeyboardButton(
                text=f"{page}/{max_page}",
                callback_data=feedbacks_pagination_call_cd.new(key=key, page="current_page")))

        next_page = page + 1
        next_page_text = f"➡️"

        if next_page <= max_page:
            pages_buttons.append(
                InlineKeyboardButton(
                    text=next_page_text,
                    callback_data=feedbacks_pagination_call_cd.new(key=key, page=next_page)))
        else:
            pages_buttons.append(
                InlineKeyboardButton(
                    text="⏺",
                    callback_data=feedbacks_pagination_call_cd.new(key=key, page="end_empty")))

    keyboard.row(*pages_buttons)
    keyboard.row(InlineKeyboardButton(text="❌ Закрыть",
                                      callback_data=feedbacks_pagination_call_cd.new(key=key, page="cancel")))
    return keyboard
