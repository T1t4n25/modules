from functools import wraps
from fastapi import HTTPException, status
from sqlalchemy.exc import OperationalError
from logging import Logger, getLogger
import uuid
import asyncio


# Local import
from utility.exc import BusinessException
from utility.localization.messages.Errors import UNEXPECTED_ERROR, DATA_RETRIEVAL_FAILED

def handle_db_errors(main_logger: Logger):
    def decorator(func):
        # init Localizer
        @wraps(func)
        async def wrapper(*args, **kwargs):
            logger = getLogger(f"{main_logger.name}.{func.__name__}")
            try:
                
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                return func(*args, **kwargs)

            except OperationalError as e:
                error_id = uuid.uuid1()
                logger.error(f"[{error_id}] Database connection error {str(e)}")
                raise BusinessException(DATA_RETRIEVAL_FAILED, error_id=error_id)
            except BusinessException:
                raise
            except Exception as e:
                error_id = str(uuid.uuid1())
                logger.exception(f"[{error_id}] Unexpected error: {str(e)}")
                raise BusinessException(error_code=UNEXPECTED_ERROR, error_id=error_id)
        return wrapper
    return decorator
