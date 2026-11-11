import pytest
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.pool import StaticPool

from core.models import Product, Customer

@pytest.fixture(name="session")
def session_fixture():
    # Используем SQLite в памяти для тестов
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture(name="sample_data")
def sample_data_fixture(session: Session):
    # Создаём тестовые данные перед каждым тестом
    customer = Customer(full_name="Иван", phone="123", address="Улица")
    product = Product(name="Хлеб", price=50.0, stock=10)
    session.add(customer)
    session.add(product)
    session.commit()
    session.refresh(customer)
    session.refresh(product)
    return {"customer_id": customer.id, "product_id": product.id}