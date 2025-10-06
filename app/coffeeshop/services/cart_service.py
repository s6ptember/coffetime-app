# app/coffeeshop/services/cart_service.py
from typing import Dict, List, Optional
from decimal import Decimal
import json
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload

from ..domain.schemas import Cart
from ..domain.models import ProductSize, Product, Size
from pydantic import BaseModel


class CartItemWithImage(BaseModel):
    product_size_id: int
    product_name: str
    size_name: str
    price: Decimal
    quantity: int
    total_price: Decimal
    image_path: Optional[str] = None


class CartService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self._carts: Dict[str, Dict] = {}

    async def add_item(self, cart_id: str, product_size_id: int, quantity: int = 1):
        product_size = await self._get_product_size(product_size_id)
        if not product_size:
            raise ValueError("Product not found")

        cart_data = self._carts.get(cart_id, {"items": {}})
        items = cart_data.get("items", {})

        item_key = str(product_size_id)
        if item_key in items:
            items[item_key]["quantity"] += quantity
        else:
            items[item_key] = {
                "product_size_id": product_size_id,
                "product_name": product_size.product.name,
                "size_name": product_size.size.name,
                "price": float(product_size.price),
                "quantity": quantity,
                "image_path": product_size.product.image_path
            }

        cart_data["items"] = items
        self._carts[cart_id] = cart_data

        return await self.get_cart(cart_id)

    async def remove_item(self, cart_id: str, product_size_id: int):
        cart_data = self._carts.get(cart_id, {"items": {}})
        items = cart_data.get("items", {})

        item_key = str(product_size_id)
        if item_key in items:
            del items[item_key]

        cart_data["items"] = items
        self._carts[cart_id] = cart_data

        return await self.get_cart(cart_id)

    async def update_quantity(self, cart_id: str, product_size_id: int, quantity: int):
        if quantity <= 0:
            return await self.remove_item(cart_id, product_size_id)

        cart_data = self._carts.get(cart_id, {"items": {}})
        items = cart_data.get("items", {})

        item_key = str(product_size_id)
        if item_key in items:
            items[item_key]["quantity"] = quantity
        else:
            product_size = await self._get_product_size(product_size_id)
            if product_size:
                items[item_key] = {
                    "product_size_id": product_size_id,
                    "product_name": product_size.product.name,
                    "size_name": product_size.size.name,
                    "price": float(product_size.price),
                    "quantity": quantity,
                    "image_path": product_size.product.image_path
                }

        cart_data["items"] = items
        self._carts[cart_id] = cart_data

        return await self.get_cart(cart_id)

    async def get_cart(self, cart_id: str):
        cart_data = self._carts.get(cart_id, {"items": {}})
        items_dict = cart_data.get("items", {})

        cart_items = []
        total_amount = Decimal('0.00')
        items_count = 0

        for item_data in items_dict.values():
            item = CartItemWithImage(
                product_size_id=item_data["product_size_id"],
                product_name=item_data["product_name"],
                size_name=item_data["size_name"],
                price=Decimal(str(item_data["price"])),
                quantity=item_data["quantity"],
                total_price=Decimal(str(item_data["price"])) * item_data["quantity"],
                image_path=item_data.get("image_path")
            )
            cart_items.append(item)
            total_amount += item.total_price
            items_count += item.quantity

        class CartResponse:
            def __init__(self, items, total_amount, items_count):
                self.items = items
                self.total_amount = total_amount
                self.items_count = items_count

        return CartResponse(cart_items, total_amount, items_count)

    async def clear_cart(self, cart_id: str) -> bool:
        if cart_id in self._carts:
            del self._carts[cart_id]
        return True

    async def _get_product_size(self, product_size_id: int) -> Optional[ProductSize]:
        query = (
            select(ProductSize)
            .options(
                joinedload(ProductSize.product),
                joinedload(ProductSize.size)
            )
            .where(ProductSize.id == product_size_id)
            .where(ProductSize.is_active == True)
        )

        result = await self.db.execute(query)
        return result.unique().scalar_one_or_none()
