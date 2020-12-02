from factorial.exceptions import AuthenticationTokenNotFound, ApiError, UserNotLoggedIn
from factorial.factorialclient import FactorialClient
from factorial.loader import JsonCredentials, JsonWork

if __name__ == '__main__':
    settings_file = 'factorial_settings.json'
    try:
        client = FactorialClient.load_from_settings(JsonCredentials(settings_file))
        client.worked_day(JsonWork(settings_file))
    except AuthenticationTokenNotFound as err:
        print(f"Can't retrieve the login token: {err}")
    except UserNotLoggedIn as err:
        print(f'User not logged in: {err}')
    except ApiError as err:
        print(f"Api error: {err}")
