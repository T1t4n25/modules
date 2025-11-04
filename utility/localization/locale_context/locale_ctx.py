from contextvars import ContextVar

# Context variable to store the current locale
# This is thread-safe and async-safe
lang_ctx: ContextVar[str] = ContextVar('lang_ctx', default='en')


def set_locale(locale: str):
    """Set the locale for the current request context"""
    lang_ctx.set(locale)


def get_locale() -> str:
    """Get the locale from the current request context"""
    return lang_ctx.get()