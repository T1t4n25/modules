"""
Module Contains the Errors data needed to fet the localized versions
"""
from fastapi import status
from dataclasses import dataclass

@dataclass
class ErrorCode:
    """Error code with message key and HTTP status"""
    code: str
    message_key: str
    status_code: int


# Define error codes
PRODUCT_NOT_FOUND = ErrorCode("PRODUCT_NOT_FOUND", "error.product.notfound", status.HTTP_404_NOT_FOUND)
PRODUCT_NAME_EXISTS = ErrorCode("PRODUCT_NAME_EXISTS", "error.product.name_exists", status.HTTP_409_CONFLICT)
PRODUCT_ALREADY_EXISTS = ErrorCode("PRODUCT_ALREADY_EXISTS", "error.product.already_exists", status.HTTP_409_CONFLICT)
IMAGE_FILENAME_NOT_UNIQUE = ErrorCode("IMAGE_FILENAME_NOT_UNIQUE", "error.image.filename_not_unique", status.HTTP_409_CONFLICT)
PRODUCT_VARIANTS_NOT_FOUND = ErrorCode("PRODUCT_VARIANTS_NOT_FOUND", "error.product.variants_notfound", status.HTTP_404_NOT_FOUND)

CATEGORY_NOT_FOUND = ErrorCode("CATEGORY_NOT_FOUND", "error.category.notfound", status.HTTP_404_NOT_FOUND)
SUBCATEGORY_NOT_FOUND = ErrorCode("SUBCATEGORY_NOT_FOUND", "error.subcategory.notfound", status.HTTP_404_NOT_FOUND)
DATABASE_OPERATIONAL_ERROR = ErrorCode("DATABASE_OPERATIONAL_ERROR", "error.database.operational", status.HTTP_503_SERVICE_UNAVAILABLE)
DATABASE_INTEGRITY_ERROR = ErrorCode("DATABASE_INTEGRITY_ERROR", "error.database.integrity", status.HTTP_422_UNPROCESSABLE_CONTENT)
DATABASE_NOT_FOUND = ErrorCode("DATABASE_NOT_FOUND", "error.database.notfound", status.HTTP_404_NOT_FOUND)
UNEXPECTED_ERROR = ErrorCode("UNEXPECTED_ERROR", "error.unexpected", status.HTTP_500_INTERNAL_SERVER_ERROR)
DATA_RETRIEVAL_FAILED = ErrorCode("DATA_RETRIEVAL_FAILED", "error.data.retrieval_failed", status.HTTP_503_SERVICE_UNAVAILABLE)

# --------------------------
# Cart-related error codes
# --------------------------

CART_NOT_FOUND = ErrorCode("CART_NOT_FOUND", "error.cart.notfound", status.HTTP_404_NOT_FOUND)
CART_ITEM_NOT_FOUND = ErrorCode("CART_ITEM_NOT_FOUND", "error.cart.item_notfound", status.HTTP_404_NOT_FOUND)
CART_EMPTY = ErrorCode("CART_EMPTY", "error.cart.empty", status.HTTP_400_BAD_REQUEST)
CART_UPDATE_FAILED = ErrorCode("CART_UPDATE_FAILED", "error.cart.update_failed", status.HTTP_422_UNPROCESSABLE_CONTENT)
CART_ADD_FAILED = ErrorCode("CART_ADD_FAILED", "error.cart.add_failed", status.HTTP_422_UNPROCESSABLE_CONTENT)

# --------------------------
# Auth-related error codes
# --------------------------

AUTH_UNAUTHORIZED = ErrorCode("AUTH_UNAUTHORIZED", "error.auth.unauthorized", status.HTTP_401_UNAUTHORIZED)
AUTH_INVALID_CREDENTIALS = ErrorCode("AUTH_INVALID_CREDENTIALS", "error.auth.credentials", status.HTTP_401_UNAUTHORIZED)
AUTH_TOKEN_EXPIRED = ErrorCode("AUTH_TOKEN_EXPIRED", "error.auth.expired", status.HTTP_401_UNAUTHORIZED)
AUTH_FORBIDDEN = ErrorCode("AUTH_FORBIDDEN", "error.auth.forbidden", status.HTTP_403_FORBIDDEN)
AUTH_INSUFFICIENT_PERMISSIONS = ErrorCode("AUTH_INSUFFICIENT_PERMISSIONS", "error.auth.insufficient_permissions", status.HTTP_403_FORBIDDEN)
AUTH_INVALID_SESSION = ErrorCode("AUTH_INVALID_SESSION", "error.auth.invalid_session", status.HTTP_401_UNAUTHORIZED)
AUTH_SERVER_UNAVAILABLE = ErrorCode("AUTH_SERVER_UNAVAILABLE", "error.auth.server_unavailable", status.HTTP_503_SERVICE_UNAVAILABLE)
AUTH_INVALID_AUDIENCE = ErrorCode("AUTH_INVALID_AUDIENCE", "error.auth.invalid_audience", status.HTTP_401_UNAUTHORIZED)

# --------------------------
# User-related error codes
# --------------------------

USER_NOT_FOUND = ErrorCode("USER_NOT_FOUND", "error.user.notfound", status.HTTP_404_NOT_FOUND)
USER_CREATION_FAILED = ErrorCode("USER_CREATION_FAILED", "error.user.creation_failed", status.HTTP_400_BAD_REQUEST)
USER_UPDATE_FAILED = ErrorCode("USER_UPDATE_FAILED", "error.user.update_failed", status.HTTP_400_BAD_REQUEST)
USER_DELETE_FAILED = ErrorCode("USER_DELETE_FAILED", "error.user.delete_failed", status.HTTP_400_BAD_REQUEST)
USER_UNAUTHORIZED = ErrorCode("USER_UNAUTHORIZED", "error.user.unauthorized", status.HTTP_403_FORBIDDEN)
USER_ALREADY_EXISTS = ErrorCode("USER_ALREADY_EXISTS", "error.user.already_exists", status.HTTP_409_CONFLICT)
USER_EMAIL_EXISTS = ErrorCode("USER_EMAIL_EXISTS", "error.user.email_exists", status.HTTP_409_CONFLICT)
USER_PHONE_EXISTS = ErrorCode("USER_PHONE_EXISTS", "error.user.phone_exists", status.HTTP_409_CONFLICT)
USER_NOT_REGISTERED = ErrorCode("USER_NOT_REGISTERED", "error.user.not_registered", status.HTTP_403_FORBIDDEN)

# --------------------------
# Order-related error codes
# --------------------------

ORDER_NOT_FOUND = ErrorCode("ORDER_NOT_FOUND", "error.order.notfound", status.HTTP_404_NOT_FOUND)
ORDER_ITEM_NOT_FOUND = ErrorCode("ORDER_ITEM_NOT_FOUND", "error.order.item_notfound", status.HTTP_404_NOT_FOUND)
ORDER_CREATION_FAILED = ErrorCode("ORDER_CREATION_FAILED", "error.order.create_failed", status.HTTP_400_BAD_REQUEST)
ORDER_UPDATE_FAILED = ErrorCode("ORDER_UPDATE_FAILED", "error.order.update_failed", status.HTTP_400_BAD_REQUEST)
ORDER_DELETE_FAILED = ErrorCode("ORDER_DELETE_FAILED", "error.order.delete_failed", status.HTTP_400_BAD_REQUEST)
ORDER_CANCEL_FAILED = ErrorCode("ORDER_CANCEL_FAILED", "error.order.cancel_failed", status.HTTP_400_BAD_REQUEST)
ORDER_STATUS_INVALID = ErrorCode("ORDER_STATUS_INVALID", "error.order.status_invalid", status.HTTP_400_BAD_REQUEST)
ORDER_PAYMENT_FAILED = ErrorCode("ORDER_PAYMENT_FAILED", "error.order.payment_failed", status.HTTP_402_PAYMENT_REQUIRED)
ORDER_UNAUTHORIZED_ACCESS = ErrorCode("ORDER_UNAUTHORIZED_ACCESS", "error.order.unauthorized_access", status.HTTP_403_FORBIDDEN)
ORDER_ALREADY_CANCELLED = ErrorCode("ORDER_ALREADY_CANCELLED", "error.order.already_cancelled", status.HTTP_409_CONFLICT)

# --------------------------
# Role-related error codes
# --------------------------

ROLE_NOT_FOUND = ErrorCode("ROLE_NOT_FOUND", "error.role.notfound", status.HTTP_404_NOT_FOUND)

ROLE_ASSIGNMENT_FAILED = ErrorCode("ROLE_ASSIGNMENT_FAILED", "error.role.assignment_failed", status.HTTP_400_BAD_REQUEST)
ROLE_REVOCATION_FAILED = ErrorCode("ROLE_REVOCATION_FAILED", "error.role.revocation_failed", status.HTTP_400_BAD_REQUEST)

if __name__ == "__main__":
    print(PRODUCT_NOT_FOUND.status_code)
    