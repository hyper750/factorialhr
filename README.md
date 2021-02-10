# Factorialhr
Python adapter to use the factorialhr api and automate
sign tasks.

## Configure settings file
Configuring the settings file we can use the `main.py`
to automatically sign the work of today (default) 
or for a different day.
By default the name of the settings file is
`factorial_settings.json` you can always change it.
```json5
{
  "user": {
    // Email to login on factorialhr
    "email": "",
    // Password to login on factorialhr
    "password": ""
  },
  "work": {
    // Work start time
    "start": "7:30",
    // Work end time
    "end": "15:30",
    /* Random minutes to variate, for example if the variation
    is 10, the sign time will be max 15:40 and min 7:20,
    always with the same hours worked, eg:
    start: 7:32
    end: 15:32
    -----
    start: 7:36
    end: 15:36
    If the minutes_variation is 0 the start and end will
    not variate in this case:
    start: 7:30
    end: 15:30
    */
    "minutes_variation": 10,
    /* If a day we have already sign the work and we
    save it again, we should delete the saved worked and save it again
    or not
    */
    "resave": false,
    /* List of breaks to take, following the same
    structure of start and end of work
    */
    "breaks": [
      {
        /*
          A random break min: 9:30 and max 11:00, for example 9:45 - 10:15
        */
        "start": "10:00",
        "end": "10:30",
        "minutes_variation": 30
      }
    ]
  }
}
```

## Automatically sign today
1. You just need to login calling the method
`FactorialClient.load_from_settings` or the
constructor.

2. Call the method `client.worked_day` passing by
parameter the day to sign, by default will sign today.

The following code will sign today, according to the
settings file.

```python
from factorial.exceptions import AuthenticationTokenNotFound, ApiError, UserNotLoggedIn
from factorial.factorialclient import FactorialClient
from factorial.loader import JsonCredentials, JsonWork

settings_file = 'factorial_settings.json'


if __name__ == '__main__':
    try:
        client = FactorialClient.load_from_settings(JsonCredentials(settings_file))
        client.worked_day(JsonWork(settings_file))
    except AuthenticationTokenNotFound as err:
        print(f"Can't retrieve the login token: {err}")
    except UserNotLoggedIn as err:
        print(f'User not logged in: {err}')
    except ApiError as err:
        print(f"Api error: {err}")

```

Sign for a different day

```python
from factorial.exceptions import AuthenticationTokenNotFound, ApiError, UserNotLoggedIn
from factorial.factorialclient import FactorialClient
from factorial.loader import JsonCredentials, JsonWork
from datetime import date

settings_file = 'factorial_settings.json'
day = date(2021, 1, 19)

if __name__ == '__main__':
    try:
        client = FactorialClient.load_from_settings(JsonCredentials(settings_file))
        client.worked_day(JsonWork(settings_file), day)
    except AuthenticationTokenNotFound as err:
        print(f"Can't retrieve the login token: {err}")
    except UserNotLoggedIn as err:
        print(f'User not logged in: {err}')
    except ApiError as err:
        print(f"Api error: {err}")

```