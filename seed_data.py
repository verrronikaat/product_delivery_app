from datetime import datetime, timedelta
import random
from sqlmodel import Session
from core.database import engine, init_db
from core.models import Product, Customer, Order, OrderItem

def seed():
    init_db()
    with Session(engine) as session:
        # 1. Создаем клиентов, если их нет
        customers = [
            Customer(full_name="Иванов Иван", phone="+79991112233", address="ул. Пушкина, 1"),
            Customer(full_name="Петрова Анна", phone="+79994445566", address="пр. Ленина, 10"),
            Customer(full_name="Сидоров Олег", phone="+79997778899", address="ул. Гагарина, 5")
        ]
        for c in customers:
            session.add(c)
        
        # 2. Берем существующие товары (или создаем, если пусто)
        from sqlmodel import select
        products = session.exec(select(Product)).all()
        if not products:
            products = [
                Product(name="Молоко 2.5%", price=80.0, stock=50),
                Product(name="Хлеб Бородинский", price=45.0, stock=30),
                Product(name="Яблоки Голден", price=120.0, stock=100),
                Product(name="Сыр Российский", price=350.0, stock=20),
                Product(name="Кофе молотый", price=500.0, stock=15)
            ]
            for p in products:
                session.add(p)
        session.commit()

        # Обновляем объекты, чтобы получить их ID
        for p in products: session.refresh(p)
        for c in customers: session.refresh(c)

        # 3. Создаем 15 случайных заказов за последние 7 дней
        for i in range(15):
            days_ago = random.randint(0, 6)
            order_date = datetime.utcnow() - timedelta(days=days_ago)
            
            order = Order(customer_id=random.choice(customers).id, created_at=order_date, status="paid")
            session.add(order)
            session.commit()
            session.refresh(order)

            # Добавляем 1-2 случайных товара в заказ
            for _ in range(random.randint(1, 2)):
                prod = random.choice(products)
                item = OrderItem(order_id=order.id, product_id=prod.id, quantity=random.randint(1, 3))
                session.add(item)

        session.commit()
    print(" База данных успешно заполнена тестовыми заказами!")

if __name__ == "__main__":
    seed()