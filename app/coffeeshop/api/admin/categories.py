# app/coffeeshop/api/admin/categories.py
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from ...api.dependencies import get_admin_service
from ...domain.schemas import CategoryCreate

router = APIRouter()
templates = Jinja2Templates(directory="app/coffeeshop/templates")


@router.get("", response_class=HTMLResponse)
async def admin_categories(
    request: Request,
    admin_service = Depends(get_admin_service)
):
    """Manage categories"""
    try:
        categories = await admin_service.get_all_categories()

        categories_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Categories - Admin</title>
            <script src="https://cdn.tailwindcss.com"></script>
            <script>
                tailwind.config = {{
                    theme: {{
                        extend: {{
                            colors: {{
                                'coffee-yellow': '#FED728',
                                'coffee-gray': '#E3E8EF',
                                'coffee-black': '#0D121C',
                                'coffee-purple': '#7A5AF8',
                                'coffee-purple-light': '#EBE9FE'
                            }}
                        }}
                    }}
                }}
            </script>
        </head>
        <body class="bg-gray-100 min-h-screen">
            <!-- Header -->
            <header class="bg-coffee-black text-white shadow-lg">
                <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div class="flex justify-between items-center h-16">
                        <h1 class="text-xl font-bold">Coffetime Admin</h1>
                        <nav class="flex space-x-4">
                            <a href="/admin" class="hover:text-coffee-yellow transition-colors">Dashboard</a>
                            <a href="/admin/categories" class="text-coffee-yellow">Categories</a>
                            <a href="/admin/sizes" class="hover:text-coffee-yellow transition-colors">Sizes</a>
                            <a href="/admin/products" class="hover:text-coffee-yellow transition-colors">Products</a>
                            <a href="/admin/orders" class="hover:text-coffee-yellow transition-colors">Orders</a>
                            <a href="/" class="hover:text-coffee-yellow transition-colors">View Site</a>
                        </nav>
                    </div>
                </div>
            </header>

            <div class="max-w-6xl mx-auto p-8">
                <div class="flex justify-between items-center mb-6">
                    <h1 class="text-3xl font-bold">Categories</h1>
                    <div class="space-x-2">
                        <a href="/admin" class="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600">Dashboard</a>
                        <button onclick="document.getElementById('addCategoryModal').classList.remove('hidden')"
                                class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">Add Category</button>
                    </div>
                </div>

                <div class="bg-white rounded-lg shadow overflow-hidden">
                    <table class="min-w-full">
                        <thead class="bg-gray-50">
                            <tr>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Slug</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-gray-200">
        """

        for category in categories:
            status_badge = "bg-green-100 text-green-800" if category.is_active else "bg-red-100 text-red-800"
            status_text = "Active" if category.is_active else "Inactive"

            categories_html += f"""
                            <tr class="hover:bg-gray-50">
                                <td class="px-6 py-4 text-sm text-gray-900">{category.id}</td>
                                <td class="px-6 py-4 text-sm font-medium text-gray-900">{category.name}</td>
                                <td class="px-6 py-4 text-sm text-gray-500">{category.slug}</td>
                                <td class="px-6 py-4 text-sm text-gray-500">{category.description or ''}</td>
                                <td class="px-6 py-4">
                                    <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full {status_badge}">
                                        {status_text}
                                    </span>
                                </td>
                                <td class="px-6 py-4 text-sm space-x-2">
                                    <form method="post" action="/admin/categories/{category.id}/toggle" style="display: inline;">
                                        <button type="submit" class="text-blue-600 hover:text-blue-900 font-medium transition-colors">
                                            {'Deactivate' if category.is_active else 'Activate'}
                                        </button>
                                    </form>
                                </td>
                            </tr>
            """

        categories_html += f"""
                        </tbody>
                    </table>
                </div>

                <!-- Stats Card -->
                <div class="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div class="bg-white rounded-lg shadow p-6">
                        <div class="flex items-center">
                            <div class="flex-shrink-0">
                                <svg class="h-8 w-8 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"></path>
                                </svg>
                            </div>
                            <div class="ml-5">
                                <p class="text-sm font-medium text-gray-500">Total Categories</p>
                                <p class="text-2xl font-semibold text-gray-900">{len(categories)}</p>
                            </div>
                        </div>
                    </div>

                    <div class="bg-white rounded-lg shadow p-6">
                        <div class="flex items-center">
                            <div class="flex-shrink-0">
                                <svg class="h-8 w-8 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                </svg>
                            </div>
                            <div class="ml-5">
                                <p class="text-sm font-medium text-gray-500">Active Categories</p>
                                <p class="text-2xl font-semibold text-green-600">{len([c for c in categories if c.is_active])}</p>
                            </div>
                        </div>
                    </div>

                    <div class="bg-white rounded-lg shadow p-6">
                        <div class="flex items-center">
                            <div class="flex-shrink-0">
                                <svg class="h-8 w-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                </svg>
                            </div>
                            <div class="ml-5">
                                <p class="text-sm font-medium text-gray-500">Inactive Categories</p>
                                <p class="text-2xl font-semibold text-red-600">{len([c for c in categories if not c.is_active])}</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Add Category Modal -->
            <div id="addCategoryModal" class="hidden fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
                <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4 transform transition-all">
                    <h3 class="text-lg font-semibold mb-4">Add New Category</h3>
                    <form method="post" action="/admin/categories/create">
                        <div class="mb-4">
                            <label class="block text-sm font-medium mb-2">Category Name</label>
                            <input type="text" name="name" required
                                   class="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                   placeholder="e.g., Latte, Cappuccino">
                        </div>
                        <div class="mb-6">
                            <label class="block text-sm font-medium mb-2">Description (Optional)</label>
                            <textarea name="description"
                                      class="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                      rows="3"
                                      placeholder="Brief description of the category..."></textarea>
                        </div>
                        <div class="flex justify-end space-x-3">
                            <button type="button" onclick="document.getElementById('addCategoryModal').classList.add('hidden')"
                                    class="px-4 py-2 text-gray-700 bg-gray-200 rounded-lg hover:bg-gray-300 transition-colors">
                                Cancel
                            </button>
                            <button type="submit"
                                    class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">
                                Add Category
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </body>
        </html>
        """

        return HTMLResponse(content=categories_html)

    except Exception as e:
        return HTMLResponse(content=f"<html><body><h1>Error</h1><p>{str(e)}</p></body></html>")


@router.post("/create")
async def create_category(
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    admin_service = Depends(get_admin_service)
):
    """Create new category"""
    try:
        category_data = CategoryCreate(
            name=name,
            description=description if description else None,
            is_active=True
        )
        await admin_service.create_category(category_data)
        return RedirectResponse(url="/admin/categories", status_code=303)
    except Exception as e:
        return HTMLResponse(content=f"""
        <html><body style='padding: 20px; font-family: Arial;'>
            <h1>Error</h1>
            <p>Failed to create category: {str(e)}</p>
            <a href='/admin/categories'>Back to Categories</a>
        </body></html>
        """)


@router.post("/{category_id}/toggle")
async def toggle_category(
    category_id: int,
    admin_service = Depends(get_admin_service)
):
    """Toggle category active status"""
    try:
        # Get current status
        categories = await admin_service.get_all_categories()
        category = next((c for c in categories if c.id == category_id), None)

        if category:
            await admin_service.update_category(category_id, is_active=not category.is_active)

        return RedirectResponse(url="/admin/categories", status_code=303)
    except Exception as e:
        return HTMLResponse(content=f"""
        <html><body style='padding: 20px; font-family: Arial;'>
            <h1>Error</h1>
            <p>Failed to update category: {str(e)}</p>
            <a href='/admin/categories'>Back to Categories</a>
        </body></html>
        """)
