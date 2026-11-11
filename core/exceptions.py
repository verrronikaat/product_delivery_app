class AppError(Exception):
    """Базовое исключение приложения."""


class ValidationError(AppError):
    """Ошибка валидации входных данных."""


class ProductNotFoundError(AppError):
    """Товар не найден."""


class OrderNotFoundError(AppError):
    """Заказ не найден."""


class EmptyOrderError(AppError):
    """Попытка создать заказ без товаров."""


class InsufficientStockError(AppError):
    """Недостаточно товара на складе."""