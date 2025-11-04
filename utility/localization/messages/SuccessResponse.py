from fastapi.responses import JSONResponse
from typing import Any, Dict

# Local imports
from utility.localization.localizer import Localizer

class SuccessResponse(JSONResponse):
    """
    Standardized JSON response for successful operations,
    localizing the message according to the given Localizer.\n
    Usage:
        return SuccessResponse(success_code)
    """

    def __init__(self, success_code: Any):
        localizer = Localizer()
        message = localizer.get_message(success_code.message_key)
        super().__init__(
            content={"message": message},
            status_code=success_code.status_code
        )
