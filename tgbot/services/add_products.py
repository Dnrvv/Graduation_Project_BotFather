from sqlalchemy.ext.asyncio import AsyncSession

from tgbot.infrastructure.database.db_functions.product_functions import add_product

#  photo_file_id=photo_file_id,
#  category_code=category_code,
#  category_name=category_name,
#  subcategory_code=subcategory_code,
#  subcategory_name=subcategory_name,
#  product_name=product_name,
#  product_caption=product_caption,
#  product_price=product_price


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
                      photo_file_id="AgACAgIAAxkBAAMtZOBhk7p_WmW0t5cxllYzXK-IpSwAAi3HMRvWMAABS_Xxq-cg15_iAQADAgADeQADMAQ",
                      category_code="snacks", category_name="Закуски",
                      product_name="Чипсы", product_caption="ммм чипсы",
                      product_price=6500)
