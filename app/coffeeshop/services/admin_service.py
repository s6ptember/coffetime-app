# app/coffeeshop/services/admin_service.py
from typing import List, Optional
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload, joinedload

from ..domain.models import Product, Category, ProductSize, Size
from ..domain.schemas import (
    Product as ProductSchema,
    Category as CategorySchema,
    Size as SizeSchema,
    CategoryCreate,
    ProductCreate,
    SizeCreate
)
from ..infrastructure.database import create_slug


class AdminService:
    """Service for admin operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # Categories management
    async def get_all_categories(self) -> List[CategorySchema]:
        """Get all categories (including inactive)"""
        query = select(Category).order_by(Category.name)
        result = await self.db.execute(query)
        categories = result.scalars().all()
        return [CategorySchema.model_validate(category) for category in categories]

    async def create_category(self, category_data: CategoryCreate) -> CategorySchema:
        """Create a new category"""
        category = Category(
            name=category_data.name,
            slug=create_slug(category_data.name),
            description=category_data.description,
            is_active=category_data.is_active
        )

        self.db.add(category)
        await self.db.commit()
        await self.db.refresh(category)

        return CategorySchema.model_validate(category)

    async def update_category(self, category_id: int, **updates) -> Optional[CategorySchema]:
        """Update category"""
        query = select(Category).where(Category.id == category_id)
        result = await self.db.execute(query)
        category = result.scalar_one_or_none()

        if not category:
            return None

        for key, value in updates.items():
            if hasattr(category, key) and value is not None:
                if key == 'name':
                    category.slug = create_slug(value)
                setattr(category, key, value)

        await self.db.commit()
        await self.db.refresh(category)

        return CategorySchema.model_validate(category)

    async def delete_category(self, category_id: int) -> bool:
        """Delete category (soft delete by setting inactive)"""
        query = select(Category).where(Category.id == category_id)
        result = await self.db.execute(query)
        category = result.scalar_one_or_none()

        if not category:
            return False

        category.is_active = False
        await self.db.commit()
        return True

    # Sizes management
    async def get_all_sizes(self) -> List[SizeSchema]:
        """Get all sizes"""
        query = select(Size).order_by(Size.volume)
        result = await self.db.execute(query)
        sizes = result.scalars().all()
        return [SizeSchema.model_validate(size) for size in sizes]

    async def create_size(self, size_data: SizeCreate) -> SizeSchema:
        """Create a new size"""
        size = Size(
            name=size_data.name,
            volume=size_data.volume,
            unit=size_data.unit,
            is_active=size_data.is_active
        )

        self.db.add(size)
        await self.db.commit()
        await self.db.refresh(size)

        return SizeSchema.model_validate(size)

    # Products management
    async def get_all_products(self) -> List[ProductSchema]:
        """Get all products with relationships"""
        query = (
            select(Product)
            .options(
                joinedload(Product.category),
                selectinload(Product.product_sizes).joinedload(ProductSize.size)
            )
            .order_by(Product.name)
        )

        result = await self.db.execute(query)
        products = result.unique().scalars().all()
        return [ProductSchema.model_validate(product) for product in products]

    async def create_product(self, product_data: ProductCreate) -> ProductSchema:
        """Create a new product with sizes"""
        product = Product(
            name=product_data.name,
            slug=create_slug(product_data.name),
            description=product_data.description,
            category_id=product_data.category_id,
            is_active=product_data.is_active
        )

        self.db.add(product)
        await self.db.flush()  # Get product ID

        # Add product sizes
        for size_data in product_data.sizes:
            product_size = ProductSize(
                product_id=product.id,
                size_id=size_data.size_id,
                price=size_data.price
            )
            self.db.add(product_size)

        await self.db.commit()
        await self.db.refresh(product)

        # Return with relationships
        query = (
            select(Product)
            .options(
                joinedload(Product.category),
                selectinload(Product.product_sizes).joinedload(ProductSize.size)
            )
            .where(Product.id == product.id)
        )
        result = await self.db.execute(query)
        product = result.unique().scalar_one()

        return ProductSchema.model_validate(product)

    async def update_product(self, product_id: int, **updates) -> Optional[ProductSchema]:
        """Update product"""
        query = (
            select(Product)
            .options(
                joinedload(Product.category),
                selectinload(Product.product_sizes).joinedload(ProductSize.size)
            )
            .where(Product.id == product_id)
        )
        result = await self.db.execute(query)
        product = result.unique().scalar_one_or_none()

        if not product:
            return None

        for key, value in updates.items():
            if hasattr(product, key) and value is not None:
                if key == 'name':
                    product.slug = create_slug(value)
                setattr(product, key, value)

        await self.db.commit()
        await self.db.refresh(product)

        return ProductSchema.model_validate(product)

    async def delete_product(self, product_id: int) -> bool:
        """Delete product (soft delete)"""
        query = select(Product).where(Product.id == product_id)
        result = await self.db.execute(query)
        product = result.scalar_one_or_none()

        if not product:
            return False

        product.is_active = False
        await self.db.commit()
        return True

    async def update_product_size_price(self, product_id: int, size_id: int, price: Decimal) -> bool:
        """Update product size price"""
        query = select(ProductSize).where(
            and_(
                ProductSize.product_id == product_id,
                ProductSize.size_id == size_id
            )
        )
        result = await self.db.execute(query)
        product_size = result.scalar_one_or_none()

        if not product_size:
            return False

        product_size.price = price
        await self.db.commit()
        return True

    async def update_or_create_product_size(self, product_id: int, size_id: int, price: Decimal) -> bool:
        """Update existing or create new product size"""
        query = select(ProductSize).where(
            and_(
                ProductSize.product_id == product_id,
                ProductSize.size_id == size_id
            )
        )
        result = await self.db.execute(query)
        product_size = result.scalar_one_or_none()

        if product_size:
            # Update existing
            product_size.price = price
            product_size.is_active = True
        else:
            # Create new
            product_size = ProductSize(
                product_id=product_id,
                size_id=size_id,
                price=price,
                is_active=True
            )
            self.db.add(product_size)

        await self.db.commit()
        return True

    async def deactivate_product_size(self, product_id: int, size_id: int) -> bool:
        """Deactivate product size"""
        query = select(ProductSize).where(
            and_(
                ProductSize.product_id == product_id,
                ProductSize.size_id == size_id
            )
        )
        result = await self.db.execute(query)
        product_size = result.scalar_one_or_none()

        if product_size:
            product_size.is_active = False
            await self.db.commit()
            return True
        return False

    async def update_size(self, size_id: int, **updates) -> Optional[SizeSchema]:
        """Update size"""
        query = select(Size).where(Size.id == size_id)
        result = await self.db.execute(query)
        size = result.scalar_one_or_none()

        if not size:
            return None

        for key, value in updates.items():
            if hasattr(size, key) and value is not None:
                setattr(size, key, value)

        await self.db.commit()
        await self.db.refresh(size)

        return SizeSchema.model_validate(size)
