# app/coffeeshop/services/session_cart_service.py
import json
import base64
from typing import Dict, List, Optional
from decimal import Decimal
from fastapi import Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload

from ..domain.models import ProductSize, Product, Size
from pydantic import BaseModel


class SessionCartItem(BaseModel):
    product_size_id: int
    quantity: int


class CartItemWithDetails(BaseModel):
    product_size_id: int
    product_name: str
    size_name: str
    price: Decimal
    quantity: int
    total_price: Decimal
    image_path: Optional[str] = None


class SessionCartResponse:
    def __init__(self, items: List[CartItemWithDetails], total_amount: Decimal, items_count: int):
        self._items = items
        self.total_amount = total_amount
        self.items_count = items_count

    @property
    def items(self) -> List[CartItemWithDetails]:
        return self._items


class SessionCartService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.cart_cookie_name = "cart_data"
        self.max_cookie_age = 86400 * 30

    def _encode_cart_data(self, items: Dict[str, SessionCartItem]) -> str:
        try:
            if not items:
                return ""

            cart_dict = {}
            for key, item in items.items():
                cart_dict[key] = {
                    "product_size_id": item.product_size_id,
                    "quantity": item.quantity
                }

            json_data = json.dumps(cart_dict, separators=(',', ':'))
            encoded_data = base64.b64encode(json_data.encode('utf-8')).decode('utf-8')

            return encoded_data
        except Exception:
            return ""

    def _decode_cart_data(self, encoded_data: str) -> Dict[str, SessionCartItem]:
        try:
            if not encoded_data or encoded_data.strip() == "" or encoded_data == '""':
                return {}

            clean_encoded = encoded_data.strip().strip('"')
            if not clean_encoded:
                return {}

            decoded = base64.b64decode(clean_encoded.encode('utf-8')).decode('utf-8')
            cart_dict = json.loads(decoded)

            items = {}
            for key, item_data in cart_dict.items():
                items[key] = SessionCartItem(
                    product_size_id=item_data["product_size_id"],
                    quantity=item_data["quantity"]
                )

            return items

        except Exception:
            return {}

    def _get_cart_from_request(self, request: Request) -> Dict[str, SessionCartItem]:
        try:
            cart_data = request.cookies.get(self.cart_cookie_name, "")
            return self._decode_cart_data(cart_data)
        except Exception:
            return {}

    def _set_cart_cookie(self, response: Response, items: Dict[str, SessionCartItem]):
        try:
            encoded_data = self._encode_cart_data(items)

            response.set_cookie(
                key=self.cart_cookie_name,
                value=encoded_data if encoded_data else "",
                max_age=self.max_cookie_age,
                httponly=False,
                samesite="lax",
                secure=False,
                path="/",
                domain=None
            )
        except Exception:
            pass

    async def add_item(self, request: Request, response: Response, product_size_id: int, quantity: int = 1) -> SessionCartResponse:
        try:
            product_size = await self._get_product_size(product_size_id)
            if not product_size:
                raise ValueError("Product not found")

            cart_items = self._get_cart_from_request(request)

            item_key = str(product_size_id)
            if item_key in cart_items:
                cart_items[item_key].quantity += quantity
            else:
                cart_items[item_key] = SessionCartItem(
                    product_size_id=product_size_id,
                    quantity=quantity
                )

            self._set_cart_cookie(response, cart_items)
            return await self._build_cart_response(cart_items)
        except Exception:
            raise

    async def remove_item(self, request: Request, response: Response, product_size_id: int) -> SessionCartResponse:
        try:
            cart_items = self._get_cart_from_request(request)

            item_key = str(product_size_id)
            if item_key in cart_items:
                del cart_items[item_key]

            self._set_cart_cookie(response, cart_items)
            return await self._build_cart_response(cart_items)
        except Exception:
            return await self._build_cart_response({})

    async def update_quantity(self, request: Request, response: Response, product_size_id: int, quantity: int) -> SessionCartResponse:
        try:
            if quantity <= 0:
                return await self.remove_item(request, response, product_size_id)

            cart_items = self._get_cart_from_request(request)

            item_key = str(product_size_id)
            if item_key in cart_items:
                cart_items[item_key].quantity = quantity
            else:
                product_size = await self._get_product_size(product_size_id)
                if product_size:
                    cart_items[item_key] = SessionCartItem(
                        product_size_id=product_size_id,
                        quantity=quantity
                    )

            self._set_cart_cookie(response, cart_items)
            return await self._build_cart_response(cart_items)
        except Exception:
            return await self._build_cart_response({})

    async def get_cart(self, request: Request) -> SessionCartResponse:
        try:
            cart_items = self._get_cart_from_request(request)
            result = await self._build_cart_response(cart_items)
            return result

        except Exception:
            return SessionCartResponse([], Decimal('0.00'), 0)

    async def clear_cart(self, request: Request, response: Response) -> SessionCartResponse:
        try:
            self._set_cart_cookie(response, {})
            return await self._build_cart_response({})
        except Exception:
            return SessionCartResponse([], Decimal('0.00'), 0)

    async def _build_cart_response(self, cart_items: Dict[str, SessionCartItem]) -> SessionCartResponse:
        try:
            if not cart_items:
                return SessionCartResponse([], Decimal('0.00'), 0)

            product_size_ids = [item.product_size_id for item in cart_items.values()]

            query = (
                select(ProductSize)
                .options(
                    joinedload(ProductSize.product),
                    joinedload(ProductSize.size)
                )
                .where(ProductSize.id.in_(product_size_ids))
                .where(ProductSize.is_active == True)
            )

            result = await self.db.execute(query)
            product_sizes = result.unique().scalars().all()

            if not product_sizes:
                return SessionCartResponse([], Decimal('0.00'), 0)

            product_size_dict = {ps.id: ps for ps in product_sizes}

            detailed_items = []
            total_amount = Decimal('0.00')
            items_count = 0

            for item in cart_items.values():
                product_size = product_size_dict.get(item.product_size_id)
                if not product_size:
                    continue

                try:
                    item_total = product_size.price * item.quantity

                    detailed_item = CartItemWithDetails(
                        product_size_id=item.product_size_id,
                        product_name=product_size.product.name,
                        size_name=product_size.size.name,
                        price=product_size.price,
                        quantity=item.quantity,
                        total_price=item_total,
                        image_path=product_size.product.image_path
                    )

                    detailed_items.append(detailed_item)
                    total_amount += item_total
                    items_count += item.quantity

                except Exception:
                    continue

            return SessionCartResponse(detailed_items, total_amount, items_count)

        except Exception:
            return SessionCartResponse([], Decimal('0.00'), 0)

    async def _get_product_size(self, product_size_id: int) -> Optional[ProductSize]:
        try:
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
        except Exception:
            return None

    def get_cart_items_for_order(self, request: Request) -> List[SessionCartItem]:
        try:
            cart_items = self._get_cart_from_request(request)
            return list(cart_items.values())
        except Exception:
            return []
