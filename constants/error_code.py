from enum import Enum


class ErrorCode(str, Enum):
    """
    Enumeration of error code
    """
    OK = 0

    HTTP_OK = 200
    HTTP_BAD_REQUEST = 400
    HTTP_UNAUTHORIZED = 401
    HTTP_FORBIDDEN = 403
    HTTP_NOT_FOUND = 404
    HTTP_INTERNAL_SERVER_ERROR = 500

    E_SERVER = -500  # Server Error

    E_PARAM_ERROR = -10
