"""
Custom Exception for Authentication & Authorization errors
"""
from fastapi import HTTPException

# from pathlib import Path
# import sys
# sys.path.append(str(Path(__file__).resolve().parent.parent))
# Local imports
from utility.localization.messages import ErrorCode
from utility.localization.localizer import Localizer

class AuthException(HTTPException):
    """Base auth error"""
    def __init__(self, error_code: ErrorCode, headers = None, **kwargs):
        localizer = Localizer()
        status_code = error_code.status_code
        detail = localizer.get_message(key=error_code.message_key, **kwargs)
        super().__init__(status_code, detail, headers)
        
        
    
if __name__ == "__main__":
    from utility.localization.messages import UNEXPECTED_ERROR
    import uuid
    raise AuthException(UNEXPECTED_ERROR, error_id=str(uuid.uuid1()))