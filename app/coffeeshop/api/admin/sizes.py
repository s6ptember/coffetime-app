# app/coffeeshop/api/admin/sizes.py
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from ...api.dependencies import get_admin_service
from ...domain.schemas import SizeCreate

router = APIRouter()
templates = Jinja2Templates(directory="app/coffeeshop/templates")


@router.get("", response_class=HTMLResponse)
async def admin_sizes(
    request: Request,
    admin_service = Depends(get_admin_service)
):
    """Manage sizes"""
    try:
        sizes = await admin_service.get_all_sizes()

        sizes_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Sizes - Admin</title>
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
                            <a href="/admin/categories" class="hover:text-coffee-yellow transition-colors">Categories</a>
                            <a href="/admin/sizes" class="text-coffee-yellow">Sizes</a>
                            <a href="/admin/products" class="hover:text-coffee-yellow transition-colors">Products</a>
                            <a href="/admin/orders" class="hover:text-coffee-yellow transition-colors">Orders</a>
                            <a href="/" class="hover:text-coffee-yellow transition-colors">View Site</a>
                        </nav>
                    </div>
                </div>
            </header>

            <div class="max-w-4xl mx-auto p-8">
                <div class="flex justify-between items-center mb-6">
                    <h1 class="text-3xl font-bold">Sizes</h1>
                    <div class="space-x-2">
                        <a href="/admin" class="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600">Dashboard</a>
                        <button onclick="document.getElementById('addSizeModal').classList.remove('hidden')"
                                class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">Add Size</button>
                    </div>
                </div>

                <div class="bg-white rounded-lg shadow overflow-hidden">
                    <table class="min-w-full">
                        <thead class="bg-gray-50">
                            <tr>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Volume</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Unit</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Full Size</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-gray-200">
        """

        for size in sizes:
            status_badge = "bg-green-100 text-green-800" if size.is_active else "bg-red-100 text-red-800"
            status_text = "Active" if size.is_active else "Inactive"

            sizes_html += f"""
                            <tr class="hover:bg-gray-50">
                                <td class="px-6 py-4 text-sm text-gray-900">{size.id}</td>
                                <td class="px-6 py-4 text-sm font-medium text-gray-900">{size.name}</td>
                                <td class="px-6 py-4 text-sm text-gray-500">{size.volume}</td>
                                <td class="px-6 py-4 text-sm text-gray-500">{size.unit}</td>
                                <td class="px-6 py-4 text-sm text-gray-900">{size.volume}{size.unit}</td>
                                <td class="px-6 py-4">
                                    <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full {status_badge}">
                                        {status_text}
                                    </span>
                                </td>
                                <td class="px-6 py-4 text-sm space-x-2">
                                    <form method="post" action="/admin/sizes/{size.id}/toggle" style="display: inline;">
                                        <button type="submit" class="text-blue-600 hover:text-blue-900 font-medium transition-colors">
                                            {'Deactivate' if size.is_active else 'Activate'}
                                        </button>
                                    </form>
                                </td>
                            </tr>
            """

        sizes_html += f"""
                        </tbody>
                    </table>
                </div>

                <!-- Stats Card -->
                <div class="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div class="bg-white rounded-lg shadow p-6">
                        <div class="flex items-center">
                            <div class="flex-shrink-0">
                                <svg class="h-8 w-8 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4a1 1 0 011-1h4m0 0V2m0 1h3m0 0V2m0 1h3m0 0V2m0 1h1a1 1 0 011 1v4m0 0h1m-1 0v3m0 0h1m-1 0v3m0 0h1m-1 0v1a1 1 0 01-1 1h-4m0 0v1m0-1h-3m0 0v1m0-1h-3m0 0v1m0-1H5a1 1 0 01-1-1v-4m0 0H3m1 0V8m0 0H3"></path>
                                </svg>
                            </div>
                            <div class="ml-5">
                                <p class="text-sm font-medium text-gray-500">Total Sizes</p>
                                <p class="text-2xl font-semibold text-gray-900">{len(sizes)}</p>
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
                                <p class="text-sm font-medium text-gray-500">Active Sizes</p>
                                <p class="text-2xl font-semibold text-green-600">{len([s for s in sizes if s.is_active])}</p>
                            </div>
                        </div>
                    </div>

                    <div class="bg-white rounded-lg shadow p-6">
                        <div class="flex items-center">
                            <div class="flex-shrink-0">
                                <svg class="h-8 w-8 text-coffee-yellow" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                                </svg>
                            </div>
                            <div class="ml-5">
                                <p class="text-sm font-medium text-gray-500">Most Popular Unit</p>
                                <p class="text-2xl font-semibold text-coffee-black">{"ml" if any(s.unit == "ml" for s in sizes) else "oz"}</p>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Size Guide -->
                <div class="mt-8 bg-white rounded-lg shadow p-6">
                    <h3 class="text-lg font-semibold mb-4">Size Guide</h3>
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        """

        # Add size guide cards
        for size in sizes:
            if size.is_active:
                size_class = "bg-green-50 border-green-200"
                icon_class = "text-green-600"
            else:
                size_class = "bg-gray-50 border-gray-200"
                icon_class = "text-gray-400"

            sizes_html += f"""
                        <div class="{size_class} border rounded-lg p-4">
                            <div class="flex items-center mb-2">
                                <svg class="h-6 w-6 {icon_class} mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"></path>
                                </svg>
                                <h4 class="font-semibold text-gray-900">{size.name}</h4>
                            </div>
                            <p class="text-sm text-gray-600">{size.volume}{size.unit}</p>
                            <p class="text-xs text-gray-500 mt-1">{"Perfect for a quick coffee" if size.volume < 300 else "Great for coffee lovers" if size.volume < 450 else "Extra large serving"}</p>
                        </div>
            """

        sizes_html += f"""
                    </div>
                </div>
            </div>

            <!-- Add Size Modal -->
            <div id="addSizeModal" class="hidden fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
                <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4 transform transition-all">
                    <h3 class="text-lg font-semibold mb-4">Add New Size</h3>
                    <form method="post" action="/admin/sizes/create">
                        <div class="mb-4">
                            <label class="block text-sm font-medium mb-2">Size Name</label>
                            <input type="text" name="name" required
                                   class="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                   placeholder="e.g., Small, Medium, Large">
                        </div>
                        <div class="mb-4">
                            <label class="block text-sm font-medium mb-2">Volume</label>
                            <input type="number" name="volume" required min="1"
                                   class="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                   placeholder="240">
                        </div>
                        <div class="mb-6">
                            <label class="block text-sm font-medium mb-2">Unit</label>
                            <select name="unit"
                                    class="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                                <option value="ml" selected>ml (milliliters)</option>
                                <option value="oz">oz (ounces)</option>
                                <option value="l">l (liters)</option>
                            </select>
                        </div>
                        <div class="flex justify-end space-x-3">
                            <button type="button" onclick="document.getElementById('addSizeModal').classList.add('hidden')"
                                    class="px-4 py-2 text-gray-700 bg-gray-200 rounded-lg hover:bg-gray-300 transition-colors">
                                Cancel
                            </button>
                            <button type="submit"
                                    class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">
                                Add Size
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </body>
        </html>
        """

        return HTMLResponse(content=sizes_html)

    except Exception as e:
        return HTMLResponse(content=f"<html><body><h1>Error</h1><p>{str(e)}</p></body></html>")


@router.post("/create")
async def create_size(
    request: Request,
    name: str = Form(...),
    volume: int = Form(...),
    unit: str = Form("ml"),
    admin_service = Depends(get_admin_service)
):
    """Create new size"""
    try:
        size_data = SizeCreate(
            name=name,
            volume=volume,
            unit=unit,
            is_active=True
        )
        await admin_service.create_size(size_data)
        return RedirectResponse(url="/admin/sizes", status_code=303)
    except Exception as e:
        return HTMLResponse(content=f"""
        <html><body style='padding: 20px; font-family: Arial;'>
            <h1>Error</h1>
            <p>Failed to create size: {str(e)}</p>
            <a href='/admin/sizes'>Back to Sizes</a>
        </body></html>
        """)


@router.post("/{size_id}/toggle")
async def toggle_size(
    size_id: int,
    admin_service = Depends(get_admin_service)
):
    """Toggle size active status"""
    try:
        # Get current status
        sizes = await admin_service.get_all_sizes()
        size = next((s for s in sizes if s.id == size_id), None)

        if size:
            await admin_service.update_size(size_id, is_active=not size.is_active)

        return RedirectResponse(url="/admin/sizes", status_code=303)
    except Exception as e:
        return HTMLResponse(content=f"""
        <html><body style='padding: 20px; font-family: Arial;'>
            <h1>Error</h1>
            <p>Failed to update size: {str(e)}</p>
            <a href='/admin/sizes'>Back to Sizes</a>
        </body></html>
        """)
