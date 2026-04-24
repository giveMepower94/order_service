class OrderServiceError(Exception):
    pass


class OrderNotFoundError(OrderServiceError):
    pass


class CatalogServiceError(OrderServiceError):
    pass


class ItemNotAvailableError(OrderServiceError):
    pass
