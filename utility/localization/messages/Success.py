from dataclasses import dataclass
from fastapi import status


@dataclass
class SuccessCode:
    """Success code with message key and HTTP status"""
    code: str
    message_key: str
    status_code: int


# Product success codes
PRODUCT_ADDED = SuccessCode(
    "PRODUCT_ADDED", "success.product.added", status.HTTP_201_CREATED)
PRODUCT_UPDATED = SuccessCode(
    "PRODUCT_UPDATED", "success.product.updated", status.HTTP_200_OK)
PRODUCT_DELETED = SuccessCode(
    "PRODUCT_DELETED", "success.product.deleted", status.HTTP_200_OK)
PRODUCT_VARIANTS_UPDATED = SuccessCode(
    "PRODUCT_VARIANTS_UPDATED", "success.product.variants_updated", status.HTTP_200_OK)
PRODUCT_VARIANTS_DELETED = SuccessCode(
    "PRODUCT_VARIANTS_DELETED", "success.product.variants_deleted", status.HTTP_200_OK)

# Category success codes
CATEGORY_ADDED = SuccessCode(
    "CATEGORY_ADDED", "success.category.added", status.HTTP_201_CREATED)
CATEGORY_UPDATED = SuccessCode(
    "CATEGORY_UPDATED", "success.category.updated", status.HTTP_200_OK)
CATEGORY_DELETED = SuccessCode(
    "CATEGORY_DELETED", "success.category.deleted", status.HTTP_200_OK)

# Subcategory success codes
SUBCATEGORY_ADDED = SuccessCode(
    "SUBCATEGORY_ADDED", "success.subcategory.added", status.HTTP_201_CREATED)
SUBCATEGORY_UPDATED = SuccessCode(
    "SUBCATEGORY_UPDATED", "success.subcategory.updated", status.HTTP_200_OK)
SUBCATEGORY_DELETED = SuccessCode(
    "SUBCATEGORY_DELETED", "success.subcategory.deleted", status.HTTP_200_OK)


# Cart success codes
CART_ITEM_ADDED = SuccessCode(
    "CART_ITEM_ADDED", "success.cart.item_added", status.HTTP_200_OK)
CART_ITEM_REMOVED = SuccessCode(
    "CART_ITEM_REMOVED", "success.cart.item_removed", status.HTTP_200_OK)
CART_CLEARED = SuccessCode(
    "CART_CLEARED", "success.cart.cleared", status.HTTP_200_OK)
CART_ITEM_UPDATED = SuccessCode(
    "CART_ITEM_UPDATED", "success.cart.item_updated", status.HTTP_200_OK)

# --------------------------
# User-related success codes
# --------------------------

USER_CREATED = SuccessCode(
    "USER_CREATED", "success.user.created", status.HTTP_201_CREATED
)
USER_UPDATED = SuccessCode(
    "USER_UPDATED", "success.user.updated", status.HTTP_200_OK
)
USER_DELETED = SuccessCode(
    "USER_DELETED", "success.user.deleted", status.HTTP_200_OK
)
ROLE_ASSIGNED = SuccessCode(
    "ROLE_ASSIGNED", "success.role.assigned", status.HTTP_200_OK
)
ROLE_REVOKED = SuccessCode(
    "ROLE_REVOKED", "success.role.revoked", status.HTTP_200_OK
)

# --------------------------
# Address-related success codes
# --------------------------

ADDRESS_ADDED = SuccessCode(
    "ADDRESS_ADDED", "success.address.added", status.HTTP_201_CREATED
)
ADDRESS_UPDATED = SuccessCode(
    "ADDRESS_UPDATED", "success.address.updated", status.HTTP_200_OK
)
ADDRESS_DELETED = SuccessCode(
    "ADDRESS_DELETED", "success.address.deleted", status.HTTP_200_OK
)

# --------------------------
# Order-related success codes
# --------------------------

ORDER_CREATED = SuccessCode(
    "ORDER_CREATED", "success.order.created", status.HTTP_201_CREATED
)
ORDER_UPDATED = SuccessCode(
    "ORDER_UPDATED", "success.order.updated", status.HTTP_200_OK
)
ORDER_CANCELLED = SuccessCode(
    "ORDER_CANCELLED", "success.order.cancelled", status.HTTP_200_OK
)
ORDER_DELETED = SuccessCode(
    "ORDER_DELETED", "success.order.deleted", status.HTTP_200_OK
)
ORDER_STATUS_CHANGED = SuccessCode(
    "ORDER_STATUS_CHANGED", "success.order.status_changed", status.HTTP_200_OK
)
