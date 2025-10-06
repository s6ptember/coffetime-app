# app/coffeeshop/services/product_service.py
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload, joinedload

from ..domain.models import Product, Category, ProductSize, Size
from ..domain.schemas import Product as ProductSchema


class ProductService:
    """Service for product operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_active_products(self) -> List[ProductSchema]:
        """Get all active products with sizes and categories"""
        query = (
            select(Product)
            .options(
                joinedload(Product.category),
                selectinload(Product.product_sizes).joinedload(ProductSize.size)
            )
            .where(Product.is_active == True)
            .order_by(Product.name)
        )

        result = await self.db.execute(query)
        products = result.unique().scalars().all()

        return [ProductSchema.model_validate(product) for product in products]

    async def get_products_by_category(self, category_name: str) -> List[ProductSchema]:
        """Get products by category name"""
        query = (
            select(Product)
            .options(
                joinedload(Product.category),
                selectinload(Product.product_sizes).joinedload(ProductSize.size)
            )
            .join(Category)
            .where(
                and_(
                    Product.is_active == True,
                    Category.is_active == True,
                    Category.name == category_name
                )
            )
            .order_by(Product.name)
        )

        result = await self.db.execute(query)
        products = result.unique().scalars().all()

        return [ProductSchema.model_validate(product) for product in products]

    async def get_products_by_category_slug(self, category_slug: str) -> List[ProductSchema]:
        """Get products by category slug"""
        query = (
            select(Product)
            .options(
                joinedload(Product.category),
                selectinload(Product.product_sizes).joinedload(ProductSize.size)
            )
            .join(Category)
            .where(
                and_(
                    Product.is_active == True,
                    Category.is_active == True,
                    Category.slug == category_slug
                )
            )
            .order_by(Product.name)
        )

        result = await self.db.execute(query)
        products = result.unique().scalars().all()

        return [ProductSchema.model_validate(product) for product in products]

    async def search_products(self, query: str) -> List[ProductSchema]:
        """Search products by name"""
        search_query = (
            select(Product)
            .options(
                joinedload(Product.category),
                selectinload(Product.product_sizes).joinedload(ProductSize.size)
            )
            .where(
                and_(
                    Product.is_active == True,
                    Product.name.ilike(f"%{query}%")
                )
            )
            .order_by(Product.name)
            .limit(20)
        )

        result = await self.db.execute(search_query)
        products = result.unique().scalars().all()

        return [ProductSchema.model_validate(product) for product in products]

    async def get_product_by_id(self, product_id: int) -> Optional[ProductSchema]:
        """Get product by ID"""
        query = (
            select(Product)
            .options(
                joinedload(Product.category),
                selectinload(Product.product_sizes).joinedload(ProductSize.size)
            )
            .where(Product.id == product_id)
            .where(Product.is_active == True)
        )

        result = await self.db.execute(query)
        product = result.unique().scalar_one_or_none()

        if product:
            return ProductSchema.model_validate(product)
        return None
