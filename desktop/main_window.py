from datetime import datetime
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLabel, QLineEdit,
    QMessageBox, QTabWidget, QTextEdit, QHeaderView, QFrame, QScrollArea,
    QComboBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from core.database import engine, init_db
from core import crud, service
from core.exceptions import AppError
from core.models import Order


STYLE_SHEET = """
QMainWindow {
    background-color: #F8FAFC;
}
QTabWidget::pane {
    border: 1px solid #E2E8F0;
    background-color: #F8FAFC;
    border-radius: 12px;
    top: -1px;
}
QTabBar::tab {
    background-color: #E2E8F0;
    color: #64748B;
    padding: 12px 24px;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
    margin-right: 4px;
    font-size: 14px;
    font-weight: 600;
}
QTabBar::tab:selected {
    background-color: #FFFFFF;
    color: #0F172A;
    border-bottom: 3px solid #6366F1;
}
QTabBar::tab:hover:!selected {
    background-color: #CBD5E1;
    color: #1E293B;
}
QLabel {
    color: #334155;
    font-size: 14px;
    font-weight: 500;
}
QLineEdit, QComboBox {
    background-color: #FFFFFF;
    color: #0F172A;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    padding: 10px 12px;
    font-size: 14px;
    selection-background-color: #C7D2FE;
}
QLineEdit:focus, QComboBox:focus {
    border: 2px solid #6366F1;
    padding: 9px 11px;
}
QComboBox::drop-down {
    border: none;
    width: 30px;
}
QPushButton {
    background-color: #6366F1;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 12px 24px;
    font-size: 14px;
    font-weight: 600;
}
QPushButton:hover {
    background-color: #4F46E5;
}
QPushButton:pressed {
    background-color: #4338CA;
}
QPushButton#SecondaryBtn {
    background-color: #F1F5F9;
    color: #475569;
    border: 1px solid #E2E8F0;
}
QPushButton#SecondaryBtn:hover {
    background-color: #E2E8F0;
    color: #0F172A;
}
QTableWidget {
    background-color: #FFFFFF;
    color: #0F172A;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    gridline-color: #F1F5F9;
    font-size: 14px;
    alternate-background-color: #F8FAFC;
}
QHeaderView::section {
    background-color: #F8FAFC;
    color: #64748B;
    padding: 12px;
    border: none;
    border-bottom: 2px solid #E2E8F0;
    font-weight: 700;
    font-size: 13px;
    text-transform: uppercase;
}
QTextEdit {
    background-color: #FFFFFF;
    color: #334155;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 12px;
    font-family: 'Segoe UI', 'Arial', sans-serif;
    font-size: 14px;
    line-height: 1.5;
}
QFrame#Card {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 16px;
}
QFrame#HeaderCard {
    background-color: #EEF2FF;
    border: none;
    border-radius: 16px;
}
QScrollArea {
    border: none;
    background-color: transparent;
}
"""

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Сервис доставки продуктов - Desktop")
        self.resize(1150, 850)
        self.setStyleSheet(STYLE_SHEET)
        init_db()

        font = QFont("Segoe UI", 10)
        self.setFont(font)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Вкладка 1: Товары
        self.tab_main = QWidget()
        self.tabs.addTab(self.tab_main, " Товары")
        self.setup_main_tab()

        # Вкладка 2: Клиенты и Категории
        self.tab_people = QWidget()
        self.tabs.addTab(self.tab_people, " Клиенты")
        self.setup_people_tab()

        # Вкладка 3: Заказы
        self.tab_orders = QWidget()
        self.tabs.addTab(self.tab_orders, " Заказы")
        self.setup_orders_tab()

        # Вкладка 4: Графики
        self.tab_charts = QWidget()
        self.tabs.addTab(self.tab_charts, " Статистика")
        self.setup_charts_tab()

        # Вкладка 5: Логи
        self.tab_logs = QWidget()
        self.tabs.addTab(self.tab_logs, " Лог активности")
        self.setup_logs_tab()

        # Вкладка 6: Справка
        self.tab_help = QWidget()
        self.tabs.addTab(self.tab_help, " Справка")
        self.setup_help_tab()

        self.refresh_data()

    def setup_main_tab(self):
        layout = QVBoxLayout(self.tab_main)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)

        header_card = QFrame()
        header_card.setObjectName("HeaderCard")
        header_layout = QVBoxLayout(header_card)
        title = QLabel("Добро пожаловать в систему доставки!")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #4338CA;")
        subtitle = QLabel("Управляйте товарами, отслеживайте остатки на складе.")
        subtitle.setStyleSheet("font-size: 14px; color: #6366F1;")
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        layout.addWidget(header_card)

        form_card = QFrame()
        form_card.setObjectName("Card")
        form_layout = QVBoxLayout(form_card)
        form_layout.setContentsMargins(20, 20, 20, 20)
        
        form_title = QLabel("Добавить новый товар")
        form_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #0F172A; margin-bottom: 10px;")
        form_layout.addWidget(form_title)

        grid = QGridLayout()
        grid.setSpacing(15)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Например: Молоко 2.5%")
        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("0.00")
        self.stock_input = QLineEdit()
        self.stock_input.setPlaceholderText("10")
        self.category_combo = QComboBox()
        self.category_combo.addItem("— без категории —", None)

        grid.addWidget(QLabel("Название товара"), 0, 0)
        grid.addWidget(QLabel("Цена (₽)"), 0, 1)
        grid.addWidget(QLabel("Количество"), 0, 2)
        grid.addWidget(QLabel("Категория"), 0, 3)
        
        grid.addWidget(self.name_input, 1, 0)
        grid.addWidget(self.price_input, 1, 1)
        grid.addWidget(self.stock_input, 1, 2)
        grid.addWidget(self.category_combo, 1, 3)

        self.add_product_btn = QPushButton(" Добавить на склад")
        self.add_product_btn.clicked.connect(self.add_product)
        grid.addWidget(self.add_product_btn, 2, 0, 1, 4)

        form_layout.addLayout(grid)
        layout.addWidget(form_card)

        table_card = QFrame()
        table_card.setObjectName("Card")
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(20, 20, 20, 20)

        table_header = QHBoxLayout()
        table_title = QLabel("Текущие остатки на складе")
        table_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #0F172A;")
        self.refresh_btn = QPushButton(" Обновить")
        self.refresh_btn.setObjectName("SecondaryBtn")
        self.refresh_btn.clicked.connect(self.refresh_data)
        table_header.addWidget(table_title)
        table_header.addStretch()
        table_header.addWidget(self.refresh_btn)
        table_layout.addLayout(table_header)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Название", "Цена", "Остаток", "Категория"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        table_layout.addWidget(self.table)
        
        layout.addWidget(table_card)

    def setup_people_tab(self):
        layout = QVBoxLayout(self.tab_people)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)

        client_card = QFrame()
        client_card.setObjectName("Card")
        client_layout = QVBoxLayout(client_card)
        client_layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Добавить нового клиента")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #0F172A; margin-bottom: 10px;")
        client_layout.addWidget(title)

        grid = QGridLayout()
        grid.setSpacing(15)

        self.client_name = QLineEdit()
        self.client_name.setPlaceholderText("Иванов Иван")
        self.client_phone = QLineEdit()
        self.client_phone.setPlaceholderText("+7 (999) 123-45-67")
        self.client_address = QLineEdit()
        self.client_address.setPlaceholderText("г. Москва, ул. Ленина, д. 1")

        grid.addWidget(QLabel("ФИО"), 0, 0)
        grid.addWidget(QLabel("Телефон"), 0, 1)
        grid.addWidget(QLabel("Адрес"), 0, 2)
        
        grid.addWidget(self.client_name, 1, 0)
        grid.addWidget(self.client_phone, 1, 1)
        grid.addWidget(self.client_address, 1, 2)

        self.add_client_btn = QPushButton(" Добавить клиента")
        self.add_client_btn.clicked.connect(self.add_client)
        grid.addWidget(self.add_client_btn, 2, 0, 1, 3)

        client_layout.addLayout(grid)
        layout.addWidget(client_card)

        cat_card = QFrame()
        cat_card.setObjectName("Card")
        cat_layout = QHBoxLayout(cat_card)
        cat_layout.setContentsMargins(20, 20, 20, 20)

        self.cat_name = QLineEdit()
        self.cat_name.setPlaceholderText("Например: Молочные продукты")
        
        self.add_cat_btn = QPushButton(" Добавить категорию")
        self.add_cat_btn.clicked.connect(self.add_category)

        cat_layout.addWidget(QLabel("Название категории:"))
        cat_layout.addWidget(self.cat_name)
        cat_layout.addWidget(self.add_cat_btn)
        
        layout.addWidget(cat_card)
        layout.addStretch()

    def setup_orders_tab(self):
        layout = QVBoxLayout(self.tab_orders)
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)

        order_card = QFrame()
        order_card.setObjectName("Card")
        order_layout = QVBoxLayout(order_card)
        order_layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Оформить новый заказ")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #0F172A; margin-bottom: 10px;")
        order_layout.addWidget(title)

        grid = QGridLayout()
        grid.setSpacing(15)

        self.order_client_combo = QComboBox()
        self.order_product_combo = QComboBox()
        self.order_qty = QLineEdit()
        self.order_qty.setPlaceholderText("1")

        grid.addWidget(QLabel("Клиент"), 0, 0)
        grid.addWidget(QLabel("Товар"), 0, 1)
        grid.addWidget(QLabel("Количество"), 0, 2)
        
        grid.addWidget(self.order_client_combo, 1, 0)
        grid.addWidget(self.order_product_combo, 1, 1)
        grid.addWidget(self.order_qty, 1, 2)

        self.create_order_btn = QPushButton(" Оформить заказ")
        self.create_order_btn.clicked.connect(self.create_order)
        grid.addWidget(self.create_order_btn, 2, 0, 1, 3)

        order_layout.addLayout(grid)
        layout.addWidget(order_card)

        table_card = QFrame()
        table_card.setObjectName("Card")
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(20, 20, 20, 20)

        table_title = QLabel("Последние заказы")
        table_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #0F172A;")
        table_layout.addWidget(table_title)

        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(4)
        self.orders_table.setHorizontalHeaderLabels(["ID", "Дата", "Клиент", "Статус"])
        self.orders_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.orders_table.verticalHeader().setVisible(False)
        self.orders_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.orders_table.setAlternatingRowColors(True)
        self.orders_table.setShowGrid(False)
        table_layout.addWidget(self.orders_table)
        
        layout.addWidget(table_card)

    def setup_charts_tab(self):
        layout = QVBoxLayout(self.tab_charts)
        layout.setContentsMargins(24, 24, 24, 24)
        
        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Аналитика продаж")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #0F172A; margin-bottom: 15px;")
        card_layout.addWidget(title)
        
        self.figure = Figure(figsize=(6, 5), dpi=100, facecolor='#FFFFFF')
        self.canvas = FigureCanvas(self.figure)
        card_layout.addWidget(self.canvas)
        
        layout.addWidget(card)

    def setup_logs_tab(self):
        layout = QVBoxLayout(self.tab_logs)
        layout.setContentsMargins(24, 24, 24, 24)
        
        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("История действий")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #0F172A; margin-bottom: 15px;")
        card_layout.addWidget(title)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        card_layout.addWidget(self.log_text)
        
        layout.addWidget(card)

    def setup_help_tab(self):
        layout = QVBoxLayout(self.tab_help)
        layout.setContentsMargins(24, 24, 24, 24)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(20)

        header = QLabel("Руководство пользователя")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #4338CA;")
        content_layout.addWidget(header)

        block1 = QFrame()
        block1.setObjectName("Card")
        l1 = QVBoxLayout(block1)
        t1 = QLabel("1. Как добавить товар?")
        t1.setStyleSheet("font-size: 16px; font-weight: bold; color: #0F172A;")
        d1 = QLabel("Перейдите на вкладку « Товары». В карточке «Добавить новый товар» заполните поля:\n"
                    "• Название (например, Яблоки)\n"
                    "• Цена (только число, например 150.50)\n"
                    "• Количество (целое число)\n"
                    "Также можно выбрать категорию из списка.\n"
                    "Нажмите кнопку « Добавить на склад». Товар сразу появится в таблице ниже.")
        d1.setWordWrap(True)
        d1.setStyleSheet("font-size: 14px; color: #475569; line-height: 1.6;")
        l1.addWidget(t1)
        l1.addWidget(d1)
        content_layout.addWidget(block1)

        block2 = QFrame()
        block2.setObjectName("Card")
        l2 = QVBoxLayout(block2)
        t2 = QLabel("2. Как добавить клиента и категорию?")
        t2.setStyleSheet("font-size: 16px; font-weight: bold; color: #0F172A;")
        d2 = QLabel("Перейдите на вкладку « Клиенты».\n"
                    "• Для клиента заполните ФИО, телефон и адрес, затем нажмите «Добавить клиента».\n"
                    "• Для категории введите название и нажмите «Добавить категорию». После этого категорию можно выбрать при создании товара.")
        d2.setWordWrap(True)
        d2.setStyleSheet("font-size: 14px; color: #475569; line-height: 1.6;")
        l2.addWidget(t2)
        l2.addWidget(d2)
        content_layout.addWidget(block2)

        block3 = QFrame()
        block3.setObjectName("Card")
        l3 = QVBoxLayout(block3)
        t3 = QLabel("3. Как оформить заказ?")
        t3.setStyleSheet("font-size: 16px; font-weight: bold; color: #0F172A;")
        d3 = QLabel("Перейдите на вкладку « Заказы». Выберите клиента из списка, товар, укажите количество "
                    "и нажмите «Оформить заказ». Система автоматически спишет товар со склада и добавит заказ в историю.")
        d3.setWordWrap(True)
        d3.setStyleSheet("font-size: 14px; color: #475569; line-height: 1.6;")
        l3.addWidget(t3)
        l3.addWidget(d3)
        content_layout.addWidget(block3)

        block4 = QFrame()
        block4.setObjectName("Card")
        l4 = QVBoxLayout(block4)
        t4 = QLabel("4. Как посмотреть статистику и логи?")
        t4.setStyleSheet("font-size: 16px; font-weight: bold; color: #0F172A;")
        d4 = QLabel("• Вкладка « Статистика» показывает графики заказов за неделю и топ товаров.\n"
                    "• Вкладка « Лог активности» содержит историю всех действий (добавления, ошибки, заказы).")
        d4.setWordWrap(True)
        d4.setStyleSheet("font-size: 14px; color: #475569; line-height: 1.6;")
        l4.addWidget(t4)
        l4.addWidget(d4)
        content_layout.addWidget(block4)

        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)

    def log(self, message: str):
        time_str = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{time_str}] {message}")

    def add_product(self):
        name = self.name_input.text().strip()
        price = self.price_input.text().strip()
        stock = self.stock_input.text().strip()
        category_id = self.category_combo.currentData()

        if not name or not price:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните название и цену.")
            return

        try:
            with Session(engine) as session:
                crud.create_product(session, name, float(price), int(stock or 0), category_id)
            self.log(f" Добавлен товар: {name}")
            self.refresh_data()
            self.name_input.clear()
            self.price_input.clear()
            self.stock_input.clear()
        except AppError as e:
            QMessageBox.critical(self, "Ошибка", str(e))
            self.log(f" Ошибка: {e}")
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Цена и количество должны быть числами.")
            self.log(" Ошибка: неверный формат чисел")

    def add_client(self):
        full_name = self.client_name.text().strip()
        phone = self.client_phone.text().strip()
        address = self.client_address.text().strip()

        if not full_name or not phone or not address:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля клиента.")
            return

        try:
            with Session(engine) as session:
                crud.create_customer(session, full_name, phone, address)
            self.log(f" Добавлен клиент: {full_name}")
            QMessageBox.information(self, "Успех", f"Клиент {full_name} добавлен!")
            self.client_name.clear()
            self.client_phone.clear()
            self.client_address.clear()
            self.refresh_data()
        except AppError as e:
            QMessageBox.critical(self, "Ошибка", str(e))
            self.log(f" Ошибка: {e}")

    def add_category(self):
        name = self.cat_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Ошибка", "Введите название категории.")
            return

        try:
            with Session(engine) as session:
                crud.create_category(session, name)
            self.log(f" Добавлена категория: {name}")
            QMessageBox.information(self, "Успех", f"Категория '{name}' добавлена!")
            self.cat_name.clear()
            self.refresh_data()
        except AppError as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка: {e}")
            self.log(f" Ошибка: {e}")

    def create_order(self):
        if self.order_client_combo.count() == 0 or self.order_product_combo.count() == 0:
            QMessageBox.warning(self, "Ошибка", "Сначала добавьте клиентов и товары.")
            return

        client_id = self.order_client_combo.currentData()
        product_id = self.order_product_combo.currentData()
        qty_text = self.order_qty.text().strip()

        try:
            qty = int(qty_text) if qty_text else 1
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Количество должно быть целым числом.")
            return

        try:
            with Session(engine) as session:
                service.place_order(session, client_id, [{"product_id": product_id, "quantity": qty}])
            self.log(f" Оформлен заказ: клиент #{client_id}, товар #{product_id}, {qty} шт.")
            QMessageBox.information(self, "Успех", "Заказ успешно оформлен!")
            self.order_qty.clear()
            self.refresh_data()
        except AppError as e:
            QMessageBox.critical(self, "Ошибка", str(e))
            self.log(f" Ошибка: {e}")

    def refresh_data(self):
        with Session(engine) as session:
            products = crud.list_products(session)
            stats = service.orders_stats_last_7_days(session)
            top = service.top_products(session)
            customers = crud.list_customers(session)
            
            
            orders = list(session.exec(
                select(Order).options(selectinload(Order.customer))
            ).all())
            
            categories = crud.list_categories(session)

        # --- Обновляем выпадающий список категорий (для формы товара) ---
        self.category_combo.clear()
        self.category_combo.addItem("— без категории —", None)
        for c in categories:
            self.category_combo.addItem(c.name, c.id)

        # --- Обновляем выпадающие списки для заказов ---
        self.order_client_combo.clear()
        for c in customers:
            self.order_client_combo.addItem(f"{c.full_name} ({c.phone})", c.id)

        self.order_product_combo.clear()
        for p in products:
            self.order_product_combo.addItem(f"{p.name} — {p.price:.2f} ₽ (ост. {p.stock})", p.id)

        # --- Обновляем таблицу заказов ---
        self.orders_table.setRowCount(len(orders))
        for row, o in enumerate(reversed(orders)):
            self.orders_table.setItem(row, 0, QTableWidgetItem(f"#{o.id}"))
            self.orders_table.setItem(row, 1, QTableWidgetItem(o.created_at.strftime("%d.%m.%Y %H:%M")))
            c_name = o.customer.full_name if o.customer else "—"
            self.orders_table.setItem(row, 2, QTableWidgetItem(c_name))
            
            status_item = QTableWidgetItem(o.status)
            status_item.setForeground(QColor("#4F46E5"))
            self.orders_table.setItem(row, 3, status_item)

        # --- Обновляем таблицу товаров ---
        self.table.setRowCount(len(products))
        for row, p in enumerate(products):
            self.table.setItem(row, 0, QTableWidgetItem(str(p.id)))
            
            name_item = QTableWidgetItem(p.name)
            name_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
            self.table.setItem(row, 1, name_item)
            
            price_item = QTableWidgetItem(f"{p.price:.2f} ₽")
            price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row, 2, price_item)
            
            stock_item = QTableWidgetItem(str(p.stock))
            if p.stock < 5:
                stock_item.setForeground(QColor("#E11D48"))
            else:
                stock_item.setForeground(QColor("#059669"))
            stock_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 3, stock_item)
            
            cat_name = "—"
            if p.category:
                cat_name = p.category.name
            self.table.setItem(row, 4, QTableWidgetItem(cat_name))

        self.table.setRowHeight(0, 45)
        for i in range(1, len(products)):
            self.table.setRowHeight(i, 40)

        # --- Рисуем графики ---
        self.figure.clear()
        
        ax1 = self.figure.add_subplot(211)
        ax1.set_facecolor('#FFFFFF')
        ax1.bar(stats["labels"], stats["values"], color='#818CF8', width=0.5)
        ax1.set_title("Динамика заказов (7 дней)", color='#334155', pad=10, fontsize=12, fontweight='bold')
        ax1.tick_params(colors='#64748B')
        for spine in ax1.spines.values():
            spine.set_color('#E2E8F0')
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.grid(axis='y', color='#F1F5F9', linestyle='--')
        
        ax2 = self.figure.add_subplot(212)
        ax2.set_facecolor('#FFFFFF')
        ax2.bar(top["labels"], top["values"], color='#34D399', width=0.5)
        ax2.set_title("Топ товаров", color='#334155', pad=10, fontsize=12, fontweight='bold')
        ax2.tick_params(colors='#64748B')
        for spine in ax2.spines.values():
            spine.set_color('#E2E8F0')
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.grid(axis='y', color='#F1F5F9', linestyle='--')
        
        self.figure.tight_layout(pad=4.0)
        self.canvas.draw()