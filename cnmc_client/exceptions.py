class APIError(Exception):
    pass

class APIConfigError(APIError):
    pass

class APIUsageError(APIError):
    pass

class CNMCError(APIError):
    pass

class CNMCResponseError(CNMCError):
    def __init__(self, code, message="HTTP error returned by CNMC"):
        super(CNMCResponseError, self).__init__("{} (code={})".format(message, code))
        self.code = code
