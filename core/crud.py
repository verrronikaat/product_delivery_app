from typing import List, Optional

from sqlmodel import Session, select

from core.exceptions import ProductNotFoundError, OrderNotFoundError
from core.models import Product, Category, Customer, Order, OrderItem


# ---------- Category ----------
def create_category(session: Session, name: str) -> Category:
    category = Category(name=name)
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


def list_categories(session: Session) -> List[Category]:
    return list(session.exec(select(Category)).all())


# ---------- Product ----------
def create_product(
    session: Session, name: str, price: float, stock: int, category_id: Optional[int] = None
) -> Product:
    product = Product(name=name, price=price, stock=stock, category_id=category_id)
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


def list_products(session: Session) -> List[Product]:
    return list(session.exec(select(Product)).all())


def get_product(session: Session, product_id: int) -> Product:
    product = session.get(Product, product_id)
    if not product:
        raise ProductNotFoundError(f"Товар с id={product_id} не найден")
    return product


# ---------- Customer ----------
def create_customer(session: Session, full_name: str, phone: str, address: str) -> Customer:
    customer = Customer(full_name=full_name, phone=phone, address=address)
    session.add(customer)
    session.commit()
    session.refresh(customer)
    return customer


def list_customers(session: Session) -> List[Customer]:
    return list(session.exec(select(Customer)).all())


# ---------- Order ----------
def create_order(session: Session, customer_id: int, items: List[dict]) -> Order:
    """
    items: [{"product_id": 1, "quantity": 2}, ...]
    """
    order = Order(customer_id=customer_id)
    session.add(order)
    session.commit()
    session.refresh(order)

    for item in items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item["product_id"],
            quantity=item["quantity"],
        )
        session.add(order_item)

    session.commit()
    session.refresh(order)
    return order


def list_orders(session: Session) -> List[Order]:
    return list(session.exec(select(Order)).all())


def get_order(session: Session, order_id: int) -> Order:
    order = session.get(Order, order_id)
    if not order:
        raise OrderNotFoundError(f"Заказ с id={order_id} не найден")
    return order