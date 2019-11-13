from factorial.factorialclient import FactorialClient
from factorial.exceptions import AuthenticationTokenNotFound, ApiError, UserNotLoggedIn


if __name__ == '__main__':
    try:
        client = FactorialClient.load_from_settings()
        client.worked_day()
    except AuthenticationTokenNotFound as err:
        print(f"Can't retrieve the login token: {err}")
    except UserNotLoggedIn as err:
        print(f'User not logged in: {err}')
    except ApiError as err:
        print(f"Api error: {err}")
