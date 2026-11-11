from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import List

from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session

from core.database import get_session, init_db
from core import crud, service
from core.exceptions import AppError

BASE_DIR = Path(__file__).resolve().parent
LOG_FILE = BASE_DIR.parent / "activity.log"


def log_event(message: str) -> None:
    """Простое логирование активности в файл."""
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(f"[{datetime.utcnow().isoformat(timespec='seconds')}] {message}\n")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    log_event("Приложение запущено")
    yield
    log_event("Приложение остановлено")


app = FastAPI(title="Product Delivery App", lifespan=lifespan)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


# ---------- HTML-страницы ----------
@app.get("/", response_class=HTMLResponse)
def index(request: Request, session: Session = Depends(get_session)):
    products = crud.list_products(session)
    categories = crud.list_categories(session)
    customers = crud.list_customers(session)
    orders = crud.list_orders(session)
    stats = service.orders_stats_last_7_days(session)
    top = service.top_products(session)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "products": products,
            "categories": categories,
            "customers": customers,
            "orders": orders,
            "stats": stats,
            "top": top,
        },
    )


@app.get("/logs", response_class=HTMLResponse)
def logs_page(request: Request):
    content = LOG_FILE.read_text(encoding="utf-8") if LOG_FILE.exists() else ""
    lines = content.strip().splitlines()[-200:]  # последние 200 строк
    return templates.TemplateResponse(
        "logs.html", {"request": request, "lines": lines}
    )


# ---------- Формы (POST) ----------
@app.post("/products")
def add_product(
    name: str = Form(...),
    price: float = Form(...),
    stock: int = Form(0),
    category_id: str = Form(""),
    session: Session = Depends(get_session),
):
    try:
        cat_id = int(category_id) if category_id.strip() else None
        product = crud.create_product(session, name, price, stock, cat_id)
        log_event(f"Добавлен товар: {product.name} (id={product.id})")
    except AppError as e:
        log_event(f"Ошибка добавления товара: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    return RedirectResponse("/", status_code=303)


@app.post("/categories")
def add_category(
    name: str = Form(...),
    session: Session = Depends(get_session),
):
    try:
        cat = crud.create_category(session, name)
        log_event(f"Добавлена категория: {cat.name} (id={cat.id})")
    except AppError as e:
        log_event(f"Ошибка добавления категории: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    return RedirectResponse("/", status_code=303)


@app.post("/customers")
def add_customer(
    full_name: str = Form(...),
    phone: str = Form(...),
    address: str = Form(...),
    session: Session = Depends(get_session),
):
    try:
        c = crud.create_customer(session, full_name, phone, address)
        log_event(f"Добавлен клиент: {c.full_name} (id={c.id})")
    except AppError as e:
        log_event(f"Ошибка добавления клиента: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    return RedirectResponse("/", status_code=303)


@app.post("/orders")
def add_order(
    customer_id: int = Form(...),
    product_id: int = Form(...),
    quantity: int = Form(...),
    session: Session = Depends(get_session),
):
    try:
        order = service.place_order(
            session, customer_id, [{"product_id": product_id, "quantity": quantity}]
        )
        log_event(
            f"Создан заказ id={order.id} клиента {customer_id}, "
            f"товар {product_id} x{quantity}"
        )
    except AppError as e:
        log_event(f"Ошибка создания заказа: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    return RedirectResponse("/", status_code=303)


# ---------- JSON API (для графика и тестов) ----------
@app.get("/api/stats/orders")
def api_orders_stats(session: Session = Depends(get_session)):
    return service.orders_stats_last_7_days(session)


@app.get("/api/stats/top-products")
def api_top_products(session: Session = Depends(get_session)):
    return service.top_products(session)


@app.get("/api/products")
def api_products(session: Session = Depends(get_session)):
    return crud.list_products(session)


@app.get("/api/orders")
def api_orders(session: Session = Depends(get_session)):
    return crud.list_orders(session)


@app.get("/api/health")
def health():
    return {"status": "ok"}