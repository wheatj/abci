from result import Result
import types_pb2 as types

class Error(Result):
    def __init__(self, code, log):
        super().__init__(code, bytes(), log)

class ErrInternalError(Error):
    def __init__(self, log):
        super().__init__(types.InternalError, log)

class ErrEncodingError(Error):
    def __init__(self, log):
        super().__init__(types.EncodingError, log)

class ErrBadNonce(Error):
    def __init__(self, log):
        super().__init__(types.BadNonce, log)

class ErrUnauthorized(Error):
    def __init__(self, log):
        super().__init__(types.Unauthorized, log)

class ErrInsufficientFunds(Error):
    def __init__(self, log):
        super().__init__(types.InsufficientFunds, log)

class ErrUnknownRequest(Error):
    def __init__(self, log):
        super().__init__(types.UnknownRequest, log)
