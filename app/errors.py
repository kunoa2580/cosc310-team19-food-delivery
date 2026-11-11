class DuplicateRestaurantError(Exception):
    pass


class RestaurantNotFoundError(Exception):
    pass

class MenuItemNotFoundError(Exception):
    pass


class DuplicateMenuItemError(Exception):
    pass

class MenuItemRestaurantNotFoundError(Exception):
    pass

class InvalidMenuItemUpdateError(Exception):
    pass

class EmptyCartError(Exception):
    pass

class InvalidCartError(Exception):
    pass

class CheckoutCustomerInactiveError(Exception):
    pass

class OrderNotFoundError(Exception):
    pass