# Module: app/routes/invoice.py


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse, StreamingResponse
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime

from app.dependencies import get_db
from app.routes.order_management import get_orders_by_order_id, get_orders_by_id

router = APIRouter()

@router.get("/invoice/{order_id}")
def download_invoice(order_id: int, db: Session = Depends(get_db)):
    order = get_orders_by_order_id(order_id, db)
    if not order:
        raise HTTPException(status_code=404, detail=f"Order with {order_id} not found")

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    pdf.setTitle(f"Invoice for Order {order.id}")
    pdf.setFont("Helvetica", 16)
    pdf.drawString(50, height - 50, f"Invoice for Order {order.id}")
    
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, height - 80, f"Order ID : {order.id}")
    pdf.drawString(50, height - 100, f"Customer ID : {order.user_id}")
    pdf.drawString(50, height -120, f"Generated on : {order.created_at.strftime('%d-%m-%Y')}")
    pdf.drawString(50, height - 140, f"Payment Method : {order.payment_method}")
    pdf.drawString(50, height - 160, f"Status : {order.status}")

    pdf.drawString(50, height - 200, "Items:")
    y = height - 220

    pdf.setFont("Helvetica", 11)
    pdf.drawString(50, y, "Product ID")
    pdf.drawString(150, y, "Quantity")
    pdf.drawString(250, y, "Price")

    y -= 20

    for item in order.items:
        pdf.drawString(50, y, str(item.product_id))
        pdf.drawString(150, y, str(item.quantity))
        pdf.drawString(250, y, f"${item.price_at_purchase:.2f}")
        y -= 20

    y -= 10
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y, f"Total Price: ${order.total_price:.2f}")

    pdf.showPage()
    pdf.save()
    buffer.seek(0)

    return StreamingResponse(buffer, media_type="application/pdf", headers={
        "Content-Disposition": f"attachment; filename=invoice_{order.id}.pdf"
    })



@router.get("/invoice/user/{user_id}")
def download_user_invoices(user_id: int, db: Session = Depends(get_db)):
    orders = get_orders_by_id(user_id, db)
    if not orders:
        raise HTTPException(status_code=404, detail=f"No orders found for user {user_id}")

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    pdf.setTitle(f"Invoices for User {user_id}")

    for order in orders:
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(50, height - 50, f"Invoice for Order {order.id}")

        pdf.setFont("Helvetica", 12)
        pdf.drawString(50, height - 80, f"Order ID : {order.id}")
        pdf.drawString(50, height - 100, f"Customer ID : {order.user_id}")
        pdf.drawString(50, height - 120, f"Generated on : {order.created_at.strftime('%d-%m-%Y')}")
        pdf.drawString(50, height - 140, f"Payment Method : {order.payment_method}")
        pdf.drawString(50, height - 160, f"Status : {order.status}")

        pdf.drawString(50, height - 200, "Items:")
        y = height - 220

        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(50, y, "Product ID")
        pdf.drawString(150, y, "Quantity")
        pdf.drawString(250, y, "Price")
        y -= 20

        pdf.setFont("Helvetica", 11)
        for item in order.items:
            pdf.drawString(50, y, str(item.product_id))
            pdf.drawString(150, y, str(item.quantity))
            pdf.drawString(250, y, f"${item.price_at_purchase:.2f}")
            y -= 20

        y -= 10
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(50, y, f"Total Price: ${order.total_price:.2f}")

        pdf.showPage()  # Move to next page for the next order

    pdf.save()
    buffer.seek(0)

    return StreamingResponse(buffer, media_type="application/pdf", headers={
        "Content-Disposition": f"attachment; filename=invoices_user_{user_id}.pdf"
    })


