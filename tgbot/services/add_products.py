from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.infrastructure.database.db_functions.product_functions import add_product


async def add_products(session: AsyncSession):
    await add_product(session,
                      photo_file_id="AgACAgIAAxkBAAMFZQRxkfBAvusHDT6s-D7KpbR__8oAAvzOMRuyLyBI8GFlzoOaB28BAAMCAAN5AAMwBA",
                      photo_link="https://ic.wampi.ru/2023/10/04/bot_logo.jpg",
                      category_code="main_dishes", category_name="Основные блюда",
                      product_name="Мясо с картофелем по-домашнему", product_caption="Сочное мяско",
                      product_price=45000)
    await add_product(session,
                      photo_file_id="AgACAgIAAxkBAAMGZQRxkcyrAnoHuiM1yJCwYtCDX4UAAv_OMRuyLyBI4O2A52pxQfwBAAMCAAN4AAMwBA",
                      photo_link="https://ic.wampi.ru/2023/10/04/bot_logo.jpg",
                      category_code="main_dishes", category_name="Основные блюда",
                      product_name="Котлета по-киевски с пюре", product_caption="Вкусная котлеточка",
                      product_price=19000)
    await add_product(session,
                      photo_file_id="AgACAgIAAxkBAAMRZQRyF6e_VmpxeJDoXGP4yejOtjMAA88xG7IvIEhYxaTvIgnwQAEAAwIAA3kAAzAE",
                      photo_link="https://ic.wampi.ru/2023/10/04/bot_logo.jpg",
                      category_code="main_dishes", category_name="Основные блюда",
                      product_name="Куриный рулет с сыром и овощным соте", product_caption="Куриный рулетик",
                      product_price=23000)
    await add_product(session,
                      photo_file_id="AgACAgIAAxkBAAMTZQRyO33Agt2gWJDQ8Xi8pil7FSoAAgXPMRuyLyBINLcX19pP_ZABAAMCAAN5AAMwBA",
                      photo_link="https://ic.wampi.ru/2023/10/04/bot_logo.jpg",
                      category_code="main_dishes", category_name="Основные блюда",
                      product_name="Бараньи семечки во фритюре", product_caption="Вкусное мясцо",
                      product_price=30000)
    await add_product(session,
                      photo_file_id="AgACAgIAAxkBAAMVZQRyiGp6MwPlkMN0yAWWNFPAO1sAAgrPMRuyLyBI1zknVnldt4cBAAMCAAN4AAMwBA",
                      photo_link="https://ic.wampi.ru/2023/10/04/bot_logo.jpg",
                      category_code="main_dishes", category_name="Основные блюда",
                      product_name="Лосось с фетой и шпинатом", product_caption="Рыбка рыбка рыбка!!!",
                      product_price=30000)

    await add_product(session,
                      photo_file_id="AgACAgIAAxkBAAMXZQRysEFil1-cTyj_yXCJVTv1RX8AAgvPMRuyLyBIU7xiuGdKCBMBAAMCAAN4AAMwBA",
                      photo_link="https://ic.wampi.ru/2023/10/04/bot_logo.jpg",
                      category_code="snacks", category_name="Закуски",
                      product_name="Мясное ассорти", product_caption="Хорошая закусочка ммм",
                      product_price=17000)
    await add_product(session,
                      photo_file_id="AgACAgIAAxkBAAMZZQRy3WCnM3lsBYNC8uHBQGcnC8kAAhDPMRuyLyBIvmIgjKkcXcQBAAMCAAN5AAMwBA",
                      photo_link="https://ic.wampi.ru/2023/10/04/bot_logo.jpg",
                      category_code="snacks", category_name="Закуски",
                      product_name="Рулетики из семги с творожным сыром", product_caption="Вкусненькие рулетики",
                      product_price=14000)
    await add_product(session,
                      photo_file_id="AgACAgIAAxkBAAMbZQRzAsiCMCdRcmnrR85Yl97AApgAAhPPMRuyLyBIFvNf5RtsJg4BAAMCAAN4AAMwBA",
                      photo_link="https://ic.wampi.ru/2023/10/04/bot_logo.jpg",
                      category_code="snacks", category_name="Закуски",
                      product_name="Канапе с красной икрой", product_caption="Канапешечка",
                      product_price=13500)
    await add_product(session,
                      photo_file_id="AgACAgIAAxkBAAMsZQRz77K0WQ25OUKR6PNZxvJ_jiAAAhzPMRuyLyBIuMcoO_QhAvcBAAMCAAN4AAMwBA",
                      photo_link="https://ic.wampi.ru/2023/10/04/bot_logo.jpg",
                      category_code="drinks", category_name="Напитки",
                      product_name="Яблочный фреш", product_caption="Освежает :)",
                      product_price=8500)
    await add_product(session,
                      photo_file_id="AgACAgIAAxkBAAMuZQR0JPTEBEyw6z8Onuu7hUAKQEsAAh_PMRuyLyBIIcPy_yN6-eQBAAMCAAN4AAMwBA",
                      photo_link="https://ic.wampi.ru/2023/10/04/bot_logo.jpg",
                      category_code="drinks", category_name="Напитки",
                      product_name="Морковный фреш", product_caption="Освежает :)",
                      product_price=8500)
    await session.commit()
