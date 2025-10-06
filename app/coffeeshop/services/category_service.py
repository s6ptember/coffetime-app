from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload, joinedload

from ..domain.models import Product, Category, ProductSize, Size
from ..domain.schemas import Product as ProductSchema, Category as CategorySchema

class CategoryService:
    """Service for category operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_active_categories(self) -> List[CategorySchema]:
        """Get all active categories"""
        query = (
            select(Category)
            .where(Category.is_active == True)
            .order_by(Category.name)
        )

        result = await self.db.execute(query)
        categories = result.scalars().all()

        return [CategorySchema.model_validate(category) for category in categories]

    async def get_category_by_slug(self, slug: str) -> Optional[CategorySchema]:
        """Get category by slug"""
        query = (
            select(Category)
            .where(Category.slug == slug)
            .where(Category.is_active == True)
        )

        result = await self.db.execute(query)
        category = result.scalar_one_or_none()

        if category:
            return CategorySchema.model_validate(category)
        return None
