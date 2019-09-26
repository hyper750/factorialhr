class AuthenticationTokenNotFound(Exception):
    def __init__(self):
        super().__init__('Authentication token not found')


class UserNotLoggedIn(Exception):
    def __init__(self):
        super().__init__("User not logged in")


class ApiError(Exception):
    DEFAULT_MSG = "Can't complete the petition"

    def __init__(self, msg=DEFAULT_MSG):
        if not msg:
           msg = ApiError.DEFAULT_MSG
        super().__init__(msg)
