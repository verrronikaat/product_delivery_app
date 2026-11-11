import pytest
from core import service, crud
from core.exceptions import EmptyOrderError, InsufficientStockError

def test_place_order_success(session, sample_data):
    # Успешное создание заказа
    items = [{"product_id": sample_data["product_id"], "quantity": 2}]
    order = service.place_order(session, sample_data["customer_id"], items)
    
    assert order.id is not None
    assert len(order.items) == 1
    
    # Проверяем, что остаток на складе уменьшился
    product = crud.get_product(session, sample_data["product_id"])
    assert product.stock == 8  # Было 10, купили 2

def test_place_order_empty(session, sample_data):
    # Проверка кастомного исключения на пустой заказ
    with pytest.raises(EmptyOrderError):
        service.place_order(session, sample_data["customer_id"], [])

def test_place_order_insufficient_stock(session, sample_data):
    # Проверка кастомного исключения при нехватке товара
    items = [{"product_id": sample_data["product_id"], "quantity": 999}]
    with pytest.raises(InsufficientStockError):
        service.place_order(session, sample_data["customer_id"], items)