# app/coffeeshop/api/admin/products.py
from fastapi import APIRouter, Depends, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from decimal import Decimal
from pathlib import Path
import shutil
import uuid

from ...api.dependencies import get_admin_service
from ...domain.schemas import ProductCreate, ProductSizeCreate

router = APIRouter()
templates = Jinja2Templates(directory="app/coffeeshop/templates")


@router.get("", response_class=HTMLResponse)
async def admin_products(
    request: Request,
    admin_service = Depends(get_admin_service)
):
    """Manage products"""
    try:
        products = await admin_service.get_all_products()
        categories = await admin_service.get_all_categories()
        sizes = await admin_service.get_all_sizes()

        products_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Products - Admin</title>
            <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body class="bg-gray-100 min-h-screen">
            <div class="max-w-7xl mx-auto p-8">
                <div class="flex justify-between items-center mb-6">
                    <h1 class="text-3xl font-bold">Products</h1>
                    <div class="space-x-2">
                        <a href="/admin" class="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600">Dashboard</a>
                        <button onclick="document.getElementById('addProductModal').classList.remove('hidden')"
                                class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">Add Product</button>
                    </div>
                </div>

                <div class="bg-white rounded-lg shadow overflow-hidden">
                    <table class="min-w-full">
                        <thead class="bg-gray-50">
                            <tr>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Image</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Category</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Sizes & Prices</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-gray-200">
        """

        for product in products:
            status_badge = "bg-green-100 text-green-800" if product.is_active else "bg-red-100 text-red-800"
            status_text = "Active" if product.is_active else "Inactive"

            # Product image
            if product.image_path:
                image_cell = f'<img src="{product.image_path}" alt="{product.name}" class="w-16 h-16 object-cover rounded-lg">'
            else:
                image_cell = '<div class="w-16 h-16 bg-gray-200 rounded-lg flex items-center justify-center"><svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg></div>'

            # Format sizes and prices
            sizes_info = ""
            for ps in product.product_sizes:
                sizes_info += f"<div class='text-xs mb-1'>{ps.size.name}: ${ps.price:.2f}</div>"

            products_html += f"""
                            <tr class="hover:bg-gray-50">
                                <td class="px-6 py-4">{image_cell}</td>
                                <td class="px-6 py-4">
                                    <div class="font-medium text-gray-900">{product.name}</div>
                                    <div class="text-sm text-gray-500">{product.description or ''}</div>
                                </td>
                                <td class="px-6 py-4 text-sm text-gray-900">{product.category.name}</td>
                                <td class="px-6 py-4">{sizes_info}</td>
                                <td class="px-6 py-4">
                                    <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full {status_badge}">
                                        {status_text}
                                    </span>
                                </td>
                                <td class="px-6 py-4 text-sm space-x-2">
                                    <a href="/admin/products/{product.id}/edit"
                                       class="text-blue-600 hover:text-blue-900 font-medium">Edit</a>
                                    <form method="post" action="/admin/products/{product.id}/toggle" style="display: inline;">
                                        <button type="submit" class="text-indigo-600 hover:text-indigo-900 font-medium">
                                            {'Deactivate' if product.is_active else 'Activate'}
                                        </button>
                                    </form>
                                </td>
                            </tr>
            """

        # Build category options
        category_options = ""
        for category in categories:
            if category.is_active:
                category_options += f'<option value="{category.id}">{category.name}</option>'

        # Build size checkboxes
        size_checkboxes = ""
        for size in sizes:
            if size.is_active:
                size_checkboxes += f"""
                <div class="flex items-center justify-between border p-2 rounded">
                    <div class="flex items-center">
                        <input type="checkbox" name="sizes" value="{size.id}" class="mr-2" onchange="togglePriceInput(this, {size.id})">
                        <label class="text-sm">{size.name} ({size.volume}{size.unit})</label>
                    </div>
                    <input type="number" step="0.01" min="0" placeholder="0.00" name="price_{size.id}"
                           class="w-20 p-1 border rounded text-sm"
                           disabled>
                </div>
                """

        products_html += f"""
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Add Product Modal -->
            <div id="addProductModal" class="hidden fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center">
                <div class="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
                    <h3 class="text-lg font-semibold mb-4">Add New Product</h3>
                    <form method="post" action="/admin/products/create">
                        <div class="mb-4">
                            <label class="block text-sm font-medium mb-2">Name</label>
                            <input type="text" name="name" required class="w-full p-2 border rounded">
                        </div>
                        <div class="mb-4">
                            <label class="block text-sm font-medium mb-2">Description</label>
                            <textarea name="description" class="w-full p-2 border rounded" rows="3"></textarea>
                        </div>
                        <div class="mb-4">
                            <label class="block text-sm font-medium mb-2">Category</label>
                            <select name="category_id" required class="w-full p-2 border rounded">
                                <option value="">Select Category</option>
                                {category_options}
                            </select>
                        </div>
                        <div class="mb-4">
                            <label class="block text-sm font-medium mb-2">Sizes & Prices</label>
                            <div class="space-y-2 max-h-40 overflow-y-auto">
                                {size_checkboxes}
                            </div>
                        </div>
                        <div class="flex justify-end space-x-2">
                            <button type="button" onclick="document.getElementById('addProductModal').classList.add('hidden')"
                                    class="px-4 py-2 text-gray-600 border rounded hover:bg-gray-50">Cancel</button>
                            <button type="submit" class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">Add Product</button>
                        </div>
                    </form>
                </div>
            </div>

            <script>
                function togglePriceInput(checkbox, sizeId) {{
                    const priceInput = document.querySelector(`input[name="price_${{sizeId}}"]`);
                    if (checkbox.checked) {{
                        priceInput.disabled = false;
                        priceInput.required = true;
                        priceInput.focus();
                    }} else {{
                        priceInput.disabled = true;
                        priceInput.required = false;
                        priceInput.value = '';
                    }}
                }}
            </script>
        </body>
        </html>
        """

        return HTMLResponse(content=products_html)

    except Exception as e:
        return HTMLResponse(content=f"<html><body><h1>Error</h1><p>{str(e)}</p></body></html>")


@router.post("/create")
async def create_product(
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    category_id: int = Form(...),
    admin_service = Depends(get_admin_service)
):
    """Create new product"""
    try:
        form_data = await request.form()

        # Parse sizes and prices
        size_ids = form_data.getlist("sizes")
        sizes_data = []

        for size_id in size_ids:
            price_value = form_data.get(f"price_{size_id}")

            if price_value:
                try:
                    price = float(price_value)
                    if price > 0:  # Only add if price is positive
                        sizes_data.append(ProductSizeCreate(
                            size_id=int(size_id),
                            price=Decimal(str(price))
                        ))
                except (ValueError, TypeError):
                    continue

        if not sizes_data:
            return HTMLResponse(content="""
            <html><body style='padding: 20px; font-family: Arial;'>
                <h1>Error</h1>
                <p>At least one size with a valid price is required</p>
                <a href='/admin/products'>Back to Products</a>
            </body></html>
            """)

        product_data = ProductCreate(
            name=name,
            description=description if description else None,
            category_id=category_id,
            is_active=True,
            sizes=sizes_data
        )

        await admin_service.create_product(product_data)
        return RedirectResponse(url="/admin/products", status_code=303)

    except Exception as e:
        return HTMLResponse(content=f"""
        <html><body style='padding: 20px; font-family: Arial;'>
            <h1>Error</h1>
            <p>An error occurred: {str(e)}</p>
            <a href='/admin/products'>Back to Products</a>
        </body></html>
        """)


@router.post("/{product_id}/toggle")
async def toggle_product(
    product_id: int,
    admin_service = Depends(get_admin_service)
):
    """Toggle product active status"""
    try:
        # Get current status
        products = await admin_service.get_all_products()
        product = next((p for p in products if p.id == product_id), None)

        if product:
            await admin_service.update_product(product_id, is_active=not product.is_active)

        return RedirectResponse(url="/admin/products", status_code=303)
    except Exception as e:
        return HTMLResponse(content=f"<html><body><h1>Error</h1><p>{str(e)}</p></body></html>")


@router.get("/{product_id}/edit", response_class=HTMLResponse)
async def edit_product_page(
    product_id: int,
    request: Request,
    admin_service = Depends(get_admin_service)
):
    """Edit product page"""
    try:
        products = await admin_service.get_all_products()
        product = next((p for p in products if p.id == product_id), None)

        if not product:
            return HTMLResponse(content="<html><body><h1>Product not found</h1></body></html>")

        categories = await admin_service.get_all_categories()
        sizes = await admin_service.get_all_sizes()

        # Build category options
        category_options = ""
        for category in categories:
            if category.is_active:
                selected = "selected" if category.id == product.category_id else ""
                category_options += f'<option value="{category.id}" {selected}>{category.name}</option>'

        # Build size options with existing prices
        size_options = ""
        for size in sizes:
            if size.is_active:
                existing_price = ""
                existing_checked = ""
                for ps in product.product_sizes:
                    if ps.size_id == size.id:
                        existing_price = str(ps.price)
                        existing_checked = "checked"
                        break

                size_options += f"""
                <div class="flex items-center justify-between border p-3 rounded-lg">
                    <div class="flex items-center">
                        <input type="checkbox" name="sizes" value="{size.id}" {existing_checked}
                               class="mr-3" onchange="togglePriceInput(this, {size.id})">
                        <label class="text-sm font-medium">{size.name} ({size.volume}{size.unit})</label>
                    </div>
                    <input type="number" step="0.01" min="0" placeholder="0.00"
                           name="price_{size.id}" value="{existing_price}"
                           class="w-24 p-2 border rounded text-sm" {'required' if existing_checked else 'disabled'}>
                </div>
                """

        image_display = ""
        if product.image_path:
            image_display = f"""
            <div class="border rounded-lg p-4 bg-gray-50">
                <img src="{product.image_path}" alt="Product Image" class="w-full h-48 object-cover rounded-lg">
            </div>
            """
        else:
            image_display = """
            <div class="border rounded-lg p-4 bg-gray-50">
                <div class="w-full h-48 bg-gray-200 rounded-lg flex items-center justify-center">
                    <span class="text-gray-500">No image</span>
                </div>
            </div>
            """

        remove_image_option = ""
        if product.image_path:
            remove_image_option = """
            <label class="flex items-center mt-2">
                <input type="checkbox" name="remove_image" class="mr-2">
                <span class="text-sm text-red-600">Remove current image</span>
            </label>
            """

        edit_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Edit Product - Admin</title>
            <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body class="bg-gray-100 min-h-screen">
            <div class="max-w-4xl mx-auto p-8">
                <div class="flex justify-between items-center mb-6">
                    <h1 class="text-3xl font-bold">Edit Product: {product.name}</h1>
                    <a href="/admin/products" class="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600">Back to Products</a>
                </div>

                <div class="bg-white rounded-lg shadow p-6">
                    <form method="post" action="/admin/products/{product_id}/update" enctype="multipart/form-data">
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <!-- Left Column -->
                            <div class="space-y-4">
                                <div>
                                    <label class="block text-sm font-medium mb-2">Product Name</label>
                                    <input type="text" name="name" value="{product.name}" required
                                           class="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500">
                                </div>

                                <div>
                                    <label class="block text-sm font-medium mb-2">Description</label>
                                    <textarea name="description" rows="4"
                                              class="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500">{product.description or ''}</textarea>
                                </div>

                                <div>
                                    <label class="block text-sm font-medium mb-2">Category</label>
                                    <select name="category_id" required class="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500">
                                        {category_options}
                                    </select>
                                </div>

                                <div>
                                    <label class="flex items-center">
                                        <input type="checkbox" name="is_active" {"checked" if product.is_active else ""} class="mr-2">
                                        <span class="text-sm font-medium">Active Product</span>
                                    </label>
                                </div>
                            </div>

                            <!-- Right Column -->
                            <div class="space-y-4">
                                <!-- Current Image -->
                                <div>
                                    <label class="block text-sm font-medium mb-2">Current Image</label>
                                    {image_display}
                                </div>

                                <!-- Upload New Image -->
                                <div>
                                    <label class="block text-sm font-medium mb-2">Upload New Image</label>
                                    <input type="file" name="image" accept="image/*"
                                           class="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500">
                                    <p class="text-sm text-gray-500 mt-1">Leave empty to keep current image</p>
                                    {remove_image_option}
                                </div>
                            </div>
                        </div>

                        <!-- Sizes and Prices -->
                        <div class="mt-8">
                            <h3 class="text-lg font-semibold mb-4">Sizes & Prices</h3>
                            <div class="space-y-3">
                                {size_options}
                            </div>
                        </div>

                        <!-- Submit Button -->
                        <div class="mt-8 flex justify-end space-x-4">
                            <a href="/admin/products" class="px-6 py-3 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors">
                                Cancel
                            </a>
                            <button type="submit" class="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">
                                Update Product
                            </button>
                        </div>
                    </form>
                </div>
            </div>

            <script>
                function togglePriceInput(checkbox, sizeId) {{
                    const priceInput = document.querySelector(`input[name="price_${{sizeId}}"]`);
                    if (checkbox.checked) {{
                        priceInput.disabled = false;
                        priceInput.required = true;
                        if (!priceInput.value) {{
                            priceInput.focus();
                        }}
                    }} else {{
                        priceInput.disabled = true;
                        priceInput.required = false;
                    }}
                }}
            </script>
        </body>
        </html>
        """

        return HTMLResponse(content=edit_html)

    except Exception as e:
        return HTMLResponse(content=f"<html><body><h1>Error</h1><p>{str(e)}</p></body></html>")


@router.post("/{product_id}/update")
async def update_product(
    product_id: int,
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    category_id: int = Form(...),
    is_active: bool = Form(False),
    remove_image: bool = Form(False),
    image: UploadFile = File(None),
    admin_service = Depends(get_admin_service)
):
    """Update product"""
    try:
        form_data = await request.form()

        # Handle image upload
        image_path = None
        if image and image.filename:
            # Create upload directory if it doesn't exist
            upload_dir = Path("app/coffeeshop/static/images/products")
            upload_dir.mkdir(parents=True, exist_ok=True)

            # Generate unique filename
            file_extension = Path(image.filename).suffix.lower()
            if file_extension not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                file_extension = '.jpg'

            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = upload_dir / unique_filename

            # Save file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)

            image_path = f"/static/images/products/{unique_filename}"

        # Update basic product info
        update_data = {
            "name": name,
            "description": description if description else None,
            "category_id": category_id,
            "is_active": is_active
        }

        # Handle image update
        if remove_image:
            update_data["image_path"] = None
        elif image_path:
            update_data["image_path"] = image_path

        await admin_service.update_product(product_id, **update_data)

        # Update sizes and prices
        size_ids = form_data.getlist("sizes")

        # Get current product to manage sizes
        current_products = await admin_service.get_all_products()
        current_product = next((p for p in current_products if p.id == product_id), None)

        if current_product:
            # Deactivate sizes that are no longer selected
            for ps in current_product.product_sizes:
                if str(ps.size_id) not in size_ids:
                    await admin_service.deactivate_product_size(product_id, ps.size_id)

        # Add/update selected sizes
        for size_id in size_ids:
            price_value = form_data.get(f"price_{size_id}")
            if price_value:
                try:
                    price = float(price_value)
                    if price > 0:
                        await admin_service.update_or_create_product_size(
                            product_id, int(size_id), Decimal(str(price))
                        )
                except (ValueError, TypeError):
                    continue

        return RedirectResponse(url="/admin/products", status_code=303)

    except Exception as e:
        return HTMLResponse(content=f"""
        <html><body style='padding: 20px; font-family: Arial;'>
            <h1>Error</h1>
            <p>Failed to update product: {str(e)}</p>
            <a href='/admin/products'>Back to Products</a>
        </body></html>
        """)
