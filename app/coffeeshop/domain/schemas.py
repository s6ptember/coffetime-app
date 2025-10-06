# app/coffeeshop/domain/schemas.py
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from decimal import Decimal
from datetime import datetime


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: bool = True


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class Category(CategoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class SizeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    volume: int = Field(..., gt=0)
    unit: str = Field(default='ml', max_length=10)
    is_active: bool = True


class SizeCreate(SizeBase):
    pass


class SizeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    volume: Optional[int] = Field(None, gt=0)
    unit: Optional[str] = Field(None, max_length=10)
    is_active: Optional[bool] = None


class Size(SizeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class ProductSizeBase(BaseModel):
    product_id: int
    size_id: int
    price: Decimal = Field(..., ge=0)
    is_active: bool = True


class ProductSizeCreate(BaseModel):
    size_id: int
    price: Decimal = Field(..., ge=0)


class ProductSize(ProductSizeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    size: Size
    created_at: datetime
    updated_at: Optional[datetime] = None


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category_id: int
    is_active: bool = True


class ProductCreate(ProductBase):
    sizes: List[ProductSizeCreate] = []


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    category_id: Optional[int] = None
    is_active: Optional[bool] = None


class Product(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    image_path: Optional[str] = None
    category: Category
    product_sizes: List[ProductSize] = []
    created_at: datetime
    updated_at: Optional[datetime] = None


class CartItemBase(BaseModel):
    product_size_id: int
    quantity: int = Field(..., gt=0)


class CartItem(CartItemBase):
    product_name: str
    size_name: str
    price: Decimal
    total_price: Decimal


class Cart(BaseModel):
    items: List[CartItem] = []
    total_amount: Decimal = Decimal('0.00')
    items_count: int = 0


class OrderItemCreate(BaseModel):
    product_size_id: int
    quantity: int = Field(..., gt=0)
    price: Decimal = Field(..., ge=0)


class OrderCreate(BaseModel):
    customer_name: str = Field(..., min_length=1, max_length=255)
    ready_time: str = Field(..., min_length=1, max_length=10)
    items: List[OrderItemCreate]


class OrderItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_size_id: int
    quantity: int
    price: Decimal
    product_size: ProductSize


class Order(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_name: str
    ready_time: str
    total_amount: Decimal
    status: str
    order_items: List[OrderItem] = []
    created_at: datetime
    updated_at: Optional[datetime] = None


class APIResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    message: Optional[str] = None
    error: Optional[str] = None


# Frontend-specific schemas for the HTML template
class CoffeeItemForFrontend(BaseModel):
    id: int
    name: str
    price: float
    category: str
    image: str


class CartItemForFrontend(BaseModel):
    coffee: CoffeeItemForFrontend
    quantity: int = 1


class CartItem(CartItemBase):
    product_name: str
    size_name: str
    price: Decimal
    total_price: Decimal
    image_path: Optional[str] = None  # Добавляем изображение


class CartItemWithImage(CartItem):
    """Расширенная версия CartItem с обязательным изображением"""
    image_path: Optional[str] = None
