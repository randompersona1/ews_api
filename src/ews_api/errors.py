class BaseEwsError(RuntimeError):
    pass


class InvalidCredentialsError(BaseEwsError):
    pass


class EwsConnectionError(BaseEwsError):
    pass


class EwsRateLimitError(BaseEwsError):
    pass


class EwsResponseError(BaseEwsError):
    pass


class EwsInternalError(BaseEwsError):
    pass
