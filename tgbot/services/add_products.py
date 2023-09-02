from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.infrastructure.database.db_functions.product_functions import add_product


async def add_products(session: AsyncSession):
    await add_product(session,
                      photo_file_id="AgACAgIAAxkBAAMpZOBhLCL_3zYb44-Pi_9ebP1auMMAAivHMRvWMAABS0KTWku8P2wKAQADAgADeQADMAQ",
                      category_code="main_bludo", category_name="Основные блюда",
                      product_name="Рогалики", product_caption="ммм рогалики",
                      product_price=25000)
    await add_product(session,
                      photo_file_id="AgACAgIAAxkBAAMrZOBhXkN6KU69x6brh-qGqZUs4FsAAizHMRvWMAABS56RA6Y9JtjCAQADAgADeQADMAQ",
                      category_code="drinks", category_name="Напитки",
                      product_name="Спрайт", product_caption="ммм спрайт",
                      product_price=7000)
    await add_product(session,
                      photo_file_id="AgACAgIAAxkBAAMrZOBhXkN6KU69x6brh-qGqZUs4FsAAizHMRvWMAABS56RA6Y9JtjCAQADAgADeQADMAQ",
                      category_code="drinks", category_name="Напитки",
                      product_name="Кола", product_caption="ммм кола",
                      product_price=12000)
    await add_product(session,
                      photo_file_id="AgACAgIAAxkBAAMtZOBhk7p_WmW0t5cxllYzXK-IpSwAAi3HMRvWMAABS_Xxq-cg15_iAQADAgADeQADMAQ",
                      category_code="snacks", category_name="Закуски",
                      product_name="Чипсы", product_caption="ммм чипсы",
                      product_price=6500)
    await session.commit()
