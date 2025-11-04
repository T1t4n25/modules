from fastapi import HTTPException
from utility.localization.messages import ErrorCode
from utility.localization.localizer import Localizer

class BusinessException(HTTPException):
    def __init__(self, error_code: ErrorCode, headers = None, **kwargs):
        localizer = Localizer()
        status_code = error_code.status_code
        detail = localizer.get_message(key=error_code.message_key, **kwargs)
        super().__init__(status_code, detail, headers)
    
        