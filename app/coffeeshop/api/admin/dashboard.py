# app/coffeeshop/api/admin/dashboard.py
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ...api.dependencies import get_order_service, get_admin_service

router = APIRouter()
templates = Jinja2Templates(directory="app/coffeeshop/templates")


@router.get("/", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    order_service = Depends(get_order_service),
    admin_service = Depends(get_admin_service)
):
    """Admin dashboard"""
    try:
        orders = await order_service.get_orders()
        products = await admin_service.get_all_products()
        categories = await admin_service.get_all_categories()

        dashboard_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Admin Dashboard - Coffetime</title>
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
        <body class="bg-gray-100">
            <div class="min-h-screen">
                <!-- Header -->
                <header class="bg-coffee-black text-white shadow-lg">
                    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                        <div class="flex justify-between items-center h-16">
                            <h1 class="text-xl font-bold">Coffetime Admin</h1>
                            <nav class="flex space-x-4">
                                <a href="/admin" class="hover:text-coffee-yellow transition-colors">Dashboard</a>
                                <a href="/admin/categories" class="hover:text-coffee-yellow transition-colors">Categories</a>
                                <a href="/admin/sizes" class="hover:text-coffee-yellow transition-colors">Sizes</a>
                                <a href="/admin/products" class="hover:text-coffee-yellow transition-colors">Products</a>
                                <a href="/admin/orders" class="hover:text-coffee-yellow transition-colors">Orders</a>
                                <a href="/" class="hover:text-coffee-yellow transition-colors">View Site</a>
                            </nav>
                        </div>
                    </div>
                </header>

                <!-- Main Content -->
                <main class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
                    <!-- Stats Cards -->
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                        <div class="bg-white rounded-lg shadow p-6">
                            <div class="flex items-center">
                                <div class="flex-shrink-0">
                                    <svg class="h-8 w-8 text-coffee-purple" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"></path>
                                    </svg>
                                </div>
                                <div class="ml-5 w-0 flex-1">
                                    <dl>
                                        <dt class="text-sm font-medium text-gray-500 truncate">Total Orders</dt>
                                        <dd class="text-lg font-medium text-gray-900">{len(orders)}</dd>
                                    </dl>
                                </div>
                            </div>
                        </div>

                        <div class="bg-white rounded-lg shadow p-6">
                            <div class="flex items-center">
                                <div class="flex-shrink-0">
                                    <svg class="h-8 w-8 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"></path>
                                    </svg>
                                </div>
                                <div class="ml-5 w-0 flex-1">
                                    <dl>
                                        <dt class="text-sm font-medium text-gray-500 truncate">Products</dt>
                                        <dd class="text-lg font-medium text-gray-900">{len([p for p in products if p.is_active])}/{len(products)}</dd>
                                        <dd class="text-xs text-gray-500">Active/Total</dd>
                                    </dl>
                                </div>
                            </div>
                        </div>

                        <div class="bg-white rounded-lg shadow p-6">
                            <div class="flex items-center">
                                <div class="flex-shrink-0">
                                    <svg class="h-8 w-8 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"></path>
                                    </svg>
                                </div>
                                <div class="ml-5 w-0 flex-1">
                                    <dl>
                                        <dt class="text-sm font-medium text-gray-500 truncate">Categories</dt>
                                        <dd class="text-lg font-medium text-gray-900">{len([c for c in categories if c.is_active])}/{len(categories)}</dd>
                                        <dd class="text-xs text-gray-500">Active/Total</dd>
                                    </dl>
                                </div>
                            </div>
                        </div>

                        <div class="bg-white rounded-lg shadow p-6">
                            <div class="flex items-center">
                                <div class="flex-shrink-0">
                                    <svg class="h-8 w-8 text-coffee-yellow" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"></path>
                                    </svg>
                                </div>
                                <div class="ml-5 w-0 flex-1">
                                    <dl>
                                        <dt class="text-sm font-medium text-gray-500 truncate">Total Revenue</dt>
                                        <dd class="text-lg font-medium text-gray-900">${sum(order.total_amount for order in orders):.2f}</dd>
                                    </dl>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Quick Actions -->
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                        <a href="/admin/categories" class="bg-white rounded-lg shadow p-4 hover:shadow-md transition-shadow">
                            <div class="flex items-center">
                                <svg class="h-6 w-6 text-blue-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"></path>
                                </svg>
                                <span class="font-medium">Manage Categories</span>
                            </div>
                        </a>

                        <a href="/admin/sizes" class="bg-white rounded-lg shadow p-4 hover:shadow-md transition-shadow">
                            <div class="flex items-center">
                                <svg class="h-6 w-6 text-purple-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4a1 1 0 011-1h4m0 0V2m0 1h3m0 0V2m0 1h3m0 0V2m0 1h1a1 1 0 011 1v4m0 0h1m-1 0v3m0 0h1m-1 0v3m0 0h1m-1 0v1a1 1 0 01-1 1h-4m0 0v1m0-1h-3m0 0v1m0-1h-3m0 0v1m0-1H5a1 1 0 01-1-1v-4m0 0H3m1 0V8m0 0H3"></path>
                                </svg>
                                <span class="font-medium">Manage Sizes</span>
                            </div>
                        </a>

                        <a href="/admin/products" class="bg-white rounded-lg shadow p-4 hover:shadow-md transition-shadow">
                            <div class="flex items-center">
                                <svg class="h-6 w-6 text-green-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"></path>
                                </svg>
                                <span class="font-medium">Manage Products</span>
                            </div>
                        </a>

                        <a href="/admin/orders" class="bg-white rounded-lg shadow p-4 hover:shadow-md transition-shadow">
                            <div class="flex items-center">
                                <svg class="h-6 w-6 text-coffee-purple mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"></path>
                                </svg>
                                <span class="font-medium">View All Orders</span>
                            </div>
                        </a>
                    </div>

                    <!-- Recent Orders -->
                    <div class="bg-white shadow rounded-lg">
                        <div class="px-4 py-5 sm:p-6">
                            <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">Recent Orders</h3>

                            {_render_orders_table(orders[:10])}
                        </div>
                    </div>
                </main>
            </div>
        </body>
        </html>
        """

        return HTMLResponse(content=dashboard_html)

    except Exception as e:
        return HTMLResponse(content=f"<html><body><h1>Error</h1><p>{str(e)}</p></body></html>")


def _render_orders_table(orders):
    """Helper function to render orders table"""
    if not orders:
        return """
        <div class="text-center py-8">
            <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"></path>
            </svg>
            <h3 class="mt-2 text-sm font-medium text-gray-900">No orders yet</h3>
            <p class="mt-1 text-sm text-gray-500">Orders will appear here once customers start placing them.</p>
        </div>
        """

    table_html = """
    <div class="overflow-hidden">
        <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
                <tr>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Order ID</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Customer</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ready Time</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
    """

    for order in orders:
        status_classes = {
            "pending": "bg-yellow-100 text-yellow-800",
            "completed": "bg-green-100 text-green-800",
            "cancelled": "bg-red-100 text-red-800"
        }.get(order.status, "bg-gray-100 text-gray-800")

        table_html += f"""
        <tr class="hover:bg-gray-50">
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">#{order.id}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{order.customer_name}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{order.ready_time}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${order.total_amount:.2f}</td>
            <td class="px-6 py-4 whitespace-nowrap">
                <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full {status_classes}">
                    {order.status.title()}
                </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {order.created_at.strftime('%m/%d/%Y %H:%M')}
            </td>
        </tr>
        """

    table_html += """
            </tbody>
        </table>
    </div>

    <div class="mt-4">
        <a href="/admin/orders" class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-coffee-black hover:bg-gray-800 transition-colors">
            View All Orders
            <svg class="ml-2 -mr-1 w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
            </svg>
        </a>
    </div>
    """

    return table_html
