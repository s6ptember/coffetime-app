# app/coffeeshop/api/admin/orders.py
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ...api.dependencies import get_order_service

router = APIRouter()
templates = Jinja2Templates(directory="app/coffeeshop/templates")


@router.get("", response_class=HTMLResponse)
async def admin_orders(
    request: Request,
    order_service = Depends(get_order_service)
):
    """View all orders"""
    try:
        orders = await order_service.get_orders()

        orders_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Orders - Admin</title>
            <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body class="bg-gray-100 p-8">
            <div class="max-w-6xl mx-auto">
                <div class="flex justify-between items-center mb-6">
                    <h1 class="text-3xl font-bold">All Orders</h1>
                    <a href="/admin" class="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600">Back to Dashboard</a>
                </div>
                <div class="bg-white rounded-lg shadow overflow-hidden">
                    <table class="min-w-full">
                        <thead class="bg-gray-50">
                            <tr>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Order ID</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Customer</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Ready Time</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-gray-200">
        """

        for order in orders:
            status_color = {"pending": "yellow", "completed": "green", "cancelled": "red"}.get(order.status, "gray")

            orders_html += f"""
                            <tr>
                                <td class="px-6 py-4 text-sm font-medium text-gray-900">#{order.id}</td>
                                <td class="px-6 py-4 text-sm text-gray-900">{order.customer_name}</td>
                                <td class="px-6 py-4 text-sm text-gray-900">{order.ready_time}</td>
                                <td class="px-6 py-4 text-sm text-gray-900">${order.total_amount:.2f}</td>
                                <td class="px-6 py-4">
                                    <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-{status_color}-100 text-{status_color}-800">
                                        {order.status.title()}
                                    </span>
                                </td>
                                <td class="px-6 py-4 text-sm text-gray-500">{order.created_at.strftime('%m/%d/%Y %H:%M')}</td>
                            </tr>
            """

        orders_html += """
                        </tbody>
                    </table>
                </div>
            </div>
        </body>
        </html>
        """

        return HTMLResponse(content=orders_html)

    except Exception as e:
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head><title>Error</title></head>
        <body style="padding: 20px; font-family: Arial;">
            <h1>Error</h1>
            <p>An error occurred: {str(e)}</p>
            <a href="/admin">Back to Admin</a>
        </body>
        </html>
        """
        return HTMLResponse(content=error_html)
