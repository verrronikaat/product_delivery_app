from collections import defaultdict
from datetime import datetime, timedelta
from typing import List

from sqlmodel import Session

from core import crud
from core.exceptions import EmptyOrderError, InsufficientStockError, ValidationError
from core.models import Order


def place_order(session: Session, customer_id: int, items: List[dict]) -> Order:
    """Создаёт заказ с проверкой валидности и остатков."""
    if not items:
        raise EmptyOrderError("Заказ не может быть пустым")

    for item in items:
        if item.get("quantity", 0) <= 0:
            raise ValidationError("Количество товара должно быть больше 0")

        product = crud.get_product(session, item["product_id"])
        if product.stock < item["quantity"]:
            raise InsufficientStockError(
                f"Недостаточно товара '{product.name}': на складе {product.stock}, "
                f"запрошено {item['quantity']}"
            )

    # списываем со склада
    for item in items:
        product = crud.get_product(session, item["product_id"])
        product.stock -= item["quantity"]
        session.add(product)
    session.commit()

    return crud.create_order(session, customer_id, items)


def orders_stats_last_7_days(session: Session) -> dict:
    """Количество заказов по дням за последние 7 дней — для графика."""
    today = datetime.utcnow().date()
    days = [today - timedelta(days=i) for i in range(6, -1, -1)]
    counts = defaultdict(int)

    orders = crud.list_orders(session)
    for order in orders:
        order_date = order.created_at.date()
        counts[order_date] += 1

    return {
        "labels": [d.strftime("%d.%m") for d in days],
        "values": [counts.get(d, 0) for d in days],
    }


def top_products(session: Session, limit: int = 5) -> dict:
    """Топ-N товаров по количеству проданных единиц — для графика."""
    from core.models import OrderItem
    from sqlmodel import select

    items = session.exec(select(OrderItem)).all()
    totals = defaultdict(int)
    for item in items:
        totals[item.product_id] += item.quantity

    sorted_items = sorted(totals.items(), key=lambda x: x[1], reverse=True)[:limit]
    labels = []
    values = []
    for product_id, qty in sorted_items:
        product = crud.get_product(session, product_id)
        labels.append(product.name)
        values.append(qty)

    return {"labels": labels, "values": values}