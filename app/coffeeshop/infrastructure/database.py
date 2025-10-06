# app/coffeeshop/infrastructure/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
from config import settings
from app.coffeeshop.domain.models import Base

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True
)

async_session_factory = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


def create_slug(text: str) -> str:
    import re
    slug = text.lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = slug.strip('-')
    return slug


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await create_sample_data()


async def create_sample_data():
    from app.coffeeshop.domain.models import Category, Size, Product, ProductSize
    from decimal import Decimal
    from sqlalchemy import select

    async with async_session_factory() as session:
        result = await session.execute(select(Category))
        if result.first():
            return

        categories_data = [
            {"name": "Latte", "description": "Smooth and creamy coffee with milk"},
            {"name": "Cappuccino", "description": "Espresso with steamed milk foam"},
            {"name": "Mocha", "description": "Coffee with chocolate"},
            {"name": "Espresso", "description": "Strong black coffee"},
        ]

        created_categories = {}
        for cat_data in categories_data:
            category = Category(
                name=cat_data["name"],
                slug=create_slug(cat_data["name"]),
                description=cat_data["description"]
            )
            session.add(category)
            await session.flush()
            created_categories[cat_data["name"]] = category.id

        sizes_data = [
            {"name": "Small", "volume": 240, "unit": "ml"},
            {"name": "Medium", "volume": 360, "unit": "ml"},
            {"name": "Large", "volume": 480, "unit": "ml"},
        ]

        created_sizes = {}
        for size_data in sizes_data:
            size = Size(**size_data)
            session.add(size)
            await session.flush()
            created_sizes[size_data["name"]] = size.id

        products_data = [
            {
                "name": "Steamy Bean",
                "description": "Rich and aromatic latte",
                "category": "Latte",
                "prices": {"Small": 4.50, "Medium": 5.00, "Large": 5.50}
            },
            {
                "name": "Velvet Brew",
                "description": "Smooth cappuccino with perfect foam",
                "category": "Cappuccino",
                "prices": {"Small": 4.00, "Medium": 4.50, "Large": 5.00}
            },
            {
                "name": "Dark Roast",
                "description": "Strong and bold espresso",
                "category": "Espresso",
                "prices": {"Small": 3.25, "Medium": 3.75, "Large": 4.25}
            },
            {
                "name": "Mocha Delight",
                "description": "Perfect blend of coffee and chocolate",
                "category": "Mocha",
                "prices": {"Small": 4.75, "Medium": 5.25, "Large": 5.75}
            },
            {
                "name": "Caramel Latte",
                "description": "Sweet caramel flavored latte",
                "category": "Latte",
                "prices": {"Small": 4.25, "Medium": 4.75, "Large": 5.25}
            }
        ]

        for prod_data in products_data:
            product = Product(
                name=prod_data["name"],
                slug=create_slug(prod_data["name"]),
                description=prod_data["description"],
                category_id=created_categories[prod_data["category"]],
                image_path=None
            )
            session.add(product)
            await session.flush()

            for size_name, price in prod_data["prices"].items():
                product_size = ProductSize(
                    product_id=product.id,
                    size_id=created_sizes[size_name],
                    price=Decimal(str(price))
                )
                session.add(product_size)

        await session.commit()
