
class BusinessError(Exception):
    """Base exception for expected business rule violations."""


class ProductNotFoundError(BusinessError):
    pass


class CustomerNotFoundError(BusinessError):
    pass


class InsufficientStockError(BusinessError):
    pass


class InactiveProductError(BusinessError):
    pass