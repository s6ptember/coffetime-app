# app/coffeeshop/services/order_service.py
from typing import List
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload

from ..domain.models import Order, OrderItem, ProductSize
from ..domain.schemas import Order as OrderSchema
from ..services.session_cart_service import CartItemWithDetails


class OrderService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_order(
        self,
        customer_name: str,
        ready_time: str,
        cart_items: List[CartItemWithDetails]
    ) -> OrderSchema:
        total_amount = sum(item.total_price for item in cart_items)

        order = Order(
            customer_name=customer_name,
            ready_time=ready_time,
            total_amount=total_amount,
            status="pending"
        )

        self.db.add(order)
        await self.db.flush()

        for cart_item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_size_id=cart_item.product_size_id,
                quantity=cart_item.quantity,
                price=cart_item.price
            )
            self.db.add(order_item)

        await self.db.commit()

        await self.db.refresh(order)

        return OrderSchema.model_validate(order)

    async def get_orders(self) -> List[OrderSchema]:
        query = (
            select(Order)
            .options(
                selectinload(Order.order_items).joinedload(OrderItem.product_size).joinedload(ProductSize.product),
                selectinload(Order.order_items).joinedload(OrderItem.product_size).joinedload(ProductSize.size)
            )
            .order_by(Order.created_at.desc())
        )

        result = await self.db.execute(query)
        orders = result.scalars().all()

        return [OrderSchema.model_validate(order) for order in orders]
