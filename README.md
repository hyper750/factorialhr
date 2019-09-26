# Factorialhr
Python adapter to use the factorialhr api and automate
tasks.

## Configure settings file
Configuring the settings file we can use the `main.py`
to automatically sign the work of today (default) 
or for a different day.
By default the name of the settings file is
`factorial_settings.json` you can always change it.
```json5
{
  // Email to login on factorialhr
  "email": "",
  // Password to login on factorialhr
  "password": "",
  "work": {
    // The start hour of work 
    "start": "7:30",
    // The end hour of work
    "end": "15:30",
    /* Random minutes to variate, max 15:40, min 7:20,
    always with the same hours worked, eg:
    start: 7:32
    end: 15:32
    If the minutes_variation is 0 the start and end will
    not variate in this case:
    start: 7:30
    end: 15:30
    */
    "minutes_variation": 10,
    /* If a day we have already sign the work and we
    save it again, we should delete the saved worked or not 
    */
    "resave": false,
    /* List of breaks to take, following the same
    structure of start and end of work
    */
    "breaks": [
      {
        "start": "10:00",
        "end": "10:30",
        "minutes_variation": 30
      }
    ]
  }
}
```

## Automatically sign for today
1. You just need to login through the method
`FactorialClient.load_from_settings` or through the
constructor.

2. Call the method `client.worked_day` passing by
parameter the day to sign, by default is today. The
following code will sign for today, according to
the settings file.

```python
from factorial.factorialclient import FactorialClient
from factorial.exceptions import AuthenticationTokenNotFound, ApiError, UserNotLoggedIn


if __name__ == '__main__':
    try:
        client = FactorialClient.load_from_settings()
        client.worked_day()
    except AuthenticationTokenNotFound as err:
        print(f"Can't retrieve the login token: {err}")
    except UserNotLoggedIn as err:
        print(err)
    except ApiError as err:
        print(f"Api error: {err}")
```