# Authentication & Localization System

A FastAPI-based authentication system integrated with Keycloak for user management and JWT verification, combined with a multi-language localization framework.

## Table of Contents

- [Features](#features)
- [Architecture Overview](#architecture-overview)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Authentication](#authentication)
  - [Localization](#localization)
  - [Error Handling](#error-handling)
- [Technical Choices](#technical-choices)
- [API Examples](#api-examples)

---

## Features

### Authentication
- **Keycloak Integration**: Full integration with Keycloak for SSO and user management
- **JWT Verification**: Async JWT token verification with public key caching
- **Role-Based Access Control (RBAC)**: Client and realm-level role management
- **Admin Operations**: User creation, role assignment, profile updates
- **Resilient Error Handling**: Automatic retry with exponential backoff
- **Token Caching**: LRU cache for admin tokens to reduce overhead

### Localization
- **Multi-language Support**: Currently supports English and Arabic
- **Context-aware**: Thread-safe and async-safe locale management
- **Message Caching**: LRU cache for constant messages (512 entries)
- **Flexible Formatting**: Support for dynamic parameters in messages
- **Centralized Error Codes**: Standardized error codes with HTTP status mapping

---

## Architecture Overview

```
auth/
├── KeycloakConfig.py      # Configuration and endpoint management
├── KeycloakJWTHandler.py  # JWT verification and RBAC
├── KeycloakAdmin.py       # Admin operations (user/role management)
└── Exceptions.py          # Custom auth exceptions

utility/
├── localization/
│   ├── locale_context/    # Thread-safe locale storage
│   ├── locales/          # JSON message files (en.json, ar.json)
│   ├── localizer/        # Message retrieval with caching
│   └── messages/         # Error/success code definitions
├── exc/
│   └── BusinessException.py  # Localized business exceptions
└── error_handlers/
    └── Handler.py        # Decorator for database error handling
```

---

## Installation

```bash
# Install dependencies
pip install fastapi aiohttp jwt async-lru python-dotenv

# Set up environment variables
cp .env.example .env
```

---

## Configuration

Create a `.env` file with your Keycloak settings:

```env
KEYCLOAK_URL=http://localhost:8080
KEYCLOAK_REALM=my-realm
KEYCLOAK_CLIENT_ID=your-client-id
KEYCLOAK_CLIENT_SECRET=your-client-secret
```

---

## Usage

### Authentication

#### JWT Verification with RBAC

```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from auth import KeycloakJWTHandler

security = HTTPBearer()
jwt_handler = KeycloakJWTHandler()

async def verify_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    required_roles: list[str] = ["user"]
):
    """Verify token and check roles"""
    token = credentials.credentials
    payload = await jwt_handler.verify_token(token, roles=required_roles)
    return payload

# Use in endpoints
@app.get("/protected")
async def protected_route(user = Depends(verify_user)):
    return {"message": f"Hello {user['name']}"}
```

#### Admin Operations

```python
from auth import KeycloakAdmin
import logging

logger = logging.getLogger(__name__)
admin = KeycloakAdmin(main_logger=logger)

# Assign role to user
await admin.assign_role_to_user(
    user_id="keycloak-user-id",
    role_name="premium_user",
    client_id="your-client-id"  # Optional: for client-level roles
)

# Update user profile
await admin.update_user_info(
    user_id="keycloak-user-id",
    first_name="John",
    email="john@example.com",
    phone_number="+1234567890"
)

# Add custom attribute
await admin.add_user_uuidv7_attribute(
    user_id="keycloak-user-id",
    uuidv7="custom-uuid-value"
)
```

### Localization

#### Setting Locale per Request

```python
from fastapi import Request
from utility.localization.locale_context import set_locale

@app.middleware("http")
async def locale_middleware(request: Request, call_next):
    # Get language from header, query param, or default to 'en'
    lang = request.headers.get("Accept-Language", "en").split(",")[0][:2]
    set_locale(lang if lang in ["en", "ar"] else "en")
    response = await call_next(request)
    return response
```

#### Using Localized Messages

```python
from utility.localization.localizer import Localizer
from utility.localization.messages import PRODUCT_NOT_FOUND, UNEXPECTED_ERROR

localizer = Localizer()

# Simple message
message = localizer.get_message(PRODUCT_NOT_FOUND.message_key)

# Message with parameters
message = localizer.get_message(
    UNEXPECTED_ERROR.message_key,
    error_id="abc-123"
)
```

#### Adding New Languages

1. Create `utility/localization/locales/{lang_code}.json`
2. Copy keys from `en.json` and translate values
3. Restart application (auto-loaded on initialization)

```json
{
  "error.product.notfound": "Producto no encontrado",
  "error.unexpected": "Error inesperado. ID: {error_id}"
}
```

### Error Handling

#### Using BusinessException

```python
from utility.exc import BusinessException
from utility.localization.messages import USER_NOT_FOUND, UNEXPECTED_ERROR
import uuid

# Raise localized exception
if not user:
    raise BusinessException(USER_NOT_FOUND)

# With dynamic parameters
try:
    # risky operation
    pass
except Exception as e:
    error_id = str(uuid.uuid1())
    logger.exception(f"[{error_id}] Unexpected error: {e}")
    raise BusinessException(UNEXPECTED_ERROR, error_id=error_id)
```

#### Database Error Handler Decorator

```python
from utility.error_handlers import handle_db_errors
import logging

logger = logging.getLogger(__name__)

@handle_db_errors(logger)
async def get_user_from_db(user_id: int):
    # Database operations
    # Automatically catches and converts DB errors to BusinessException
    return await db.query(User).filter(User.id == user_id).first()
```

#### Success Responses

```python
from utility.localization.messages import SuccessResponse, USER_CREATED

@app.post("/users")
async def create_user(user_data: UserCreate):
    # ... create user logic
    return SuccessResponse(USER_CREATED)
```

---

## Technical Choices

### Why Singleton Pattern?
**KeycloakConfig**, **KeycloakAdmin**, and **Localizer** use singleton pattern to:
- Share configuration across the application
- Maintain a single cache for tokens and messages
- Reduce memory overhead
- Ensure consistency in admin token management

### Why Async LRU Cache?
- **Admin Tokens**: Cached to avoid unnecessary token requests (1 hour validity)
- **Public Keys**: Cached JWT verification keys, with invalidation on rotation
- **Messages**: Constant messages cached (512 limit) to reduce dictionary lookups

### Why Context Variables for Locale?
- **Thread-safe**: Unlike global variables, context vars are isolated per request
- **Async-safe**: Works correctly with FastAPI's async handlers
- **No contamination**: Each request maintains its own locale without interference

### Error Handling Strategy
1. **Separation of Concerns**: Business exceptions vs HTTP exceptions
2. **Developer vs User Messages**: Detailed logs for developers, user-friendly messages for clients
3. **Error IDs**: UUID tracking for correlating user reports with logs
4. **Retry Logic**: Exponential backoff for transient failures (network, token expiry)

### Why Message Key Pattern?
Instead of hardcoding messages:
```python
# ❌ Bad: Hardcoded
raise HTTPException(404, "Product not found")

# ✅ Good: Centralized and localized
raise BusinessException(PRODUCT_NOT_FOUND)
```

Benefits:
- Single source of truth for error definitions
- Easy to maintain and update messages
- Automatic localization support
- Type-safe with IDE autocomplete

---

## API Examples

### Complete Endpoint Example

```python
from fastapi import FastAPI, Depends
from utility.localization.locale_context import set_locale
from utility.localization.messages import SuccessResponse, USER_CREATED
from utility.exc import BusinessException
from auth import KeycloakAdmin, KeycloakJWTHandler

app = FastAPI()
admin = KeycloakAdmin()
jwt_handler = KeycloakJWTHandler()

@app.middleware("http")
async def locale_middleware(request, call_next):
    lang = request.headers.get("Accept-Language", "en")[:2]
    set_locale(lang if lang in ["en", "ar"] else "en")
    return await call_next(request)

@app.post("/users")
async def create_user(
    user_data: UserCreate,
    token_payload = Depends(verify_admin_token)
):
    """Create user with automatic role assignment"""
    try:
        # Assign role
        await admin.assign_role_to_user(
            user_id=user_data.keycloak_id,
            role_name="customer"
        )
        return SuccessResponse(USER_CREATED)
    except BusinessException:
        raise  # Re-raise to let FastAPI handle it
```

### Error Response Format

```json
{
  "detail": "User not found."
}
```

With Arabic locale:
```json
{
  "detail": "المستخدم غير موجود."
}
```

---

## Best Practices

1. **Always set locale** at the start of request handling
2. **Use BusinessException** for all business logic errors
3. **Log with error IDs** for tracking unexpected errors
4. **Don't cache** messages with dynamic parameters (error_id, etc.)
5. **Use RBAC** - verify roles at endpoint level, not in business logic
6. **Retry transient failures** - network errors, token expiry (built-in)
7. **Clear token cache** when encountering 401/403 (automatic)

---

## Contributing

When adding new error codes:

1. Add to `utility/localization/messages/Errors.py`:
```python
NEW_ERROR = ErrorCode("NEW_ERROR", "error.new.message", status.HTTP_400_BAD_REQUEST)
```

2. Add translations to all locale files:
```json
{
  "error.new.message": "Your error message here"
}
```

3. Use in code:
```python
raise BusinessException(NEW_ERROR)
```

---

---

## Authors

### Authentication & Localization System
- **Zeyad Hemeda** - [@T1t4n25](https://github.com/ahmeda335)

### RabbitMQ Streams Module
- **Ahmed Adel** - [@ahmeda335](https://github.com/ahmeda335)
- **Zeyad Hemeda** - [@T1t4n25](https://github.com/T1t4n25)
