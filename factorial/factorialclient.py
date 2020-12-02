import hashlib
import logging
import logging.config
import os
import pickle
import random
from datetime import date
from http import client as http_client

import requests
from bs4 import BeautifulSoup

from constants import BASE_PROJECT, LOGGER
from factorial.exceptions import AuthenticationTokenNotFound, UserNotLoggedIn, ApiError
from factorial.loader.credentials.abstract_credentials import AbstractCredentials
from factorial.loader.work.abstract_work import AbstractWork


class FactorialClient:
    # Folder to save the session's cookie
    SESSIONS_FOLDER = os.path.join(BASE_PROJECT, "sessions")

    # Endpoints
    BASE_NAME = "https://api.factorialhr.com/"
    # Url to be able to login (post: username, password) and logout (delete) on the api
    SESSION_URL = '{}sessions'.format(BASE_NAME)
    # Url to show the form to get the authentication token (get)
    LOGIN_PAGE_URL = '{}users/sign_in'.format(BASE_NAME)
    # Url to get the user info (get)
    USER_INFO_URL = '{}accesses'.format(BASE_NAME)
    # Get employee (get)
    EMPLOYEE_URL = '{}employees'.format(BASE_NAME)
    # Get period (get)
    PERIODS_URL = '{}attendance/periods'.format(BASE_NAME)
    # Shift days (get, post, patch, delete)
    SHIFT_URL = '{}attendance/shifts'.format(BASE_NAME)
    # Calendar (get)
    CALENDAR_URL = '{}attendance/calendar'.format(BASE_NAME)

    def __init__(self, email, password, cookie_file=None):
        """Factorial client to automatically sign up the work
        :param email: (required) string, email to login on Factorial
        :param password: (required) string, password to login on Factorial
        :param cookie_file: (optional) string, file to save the cookies
        """
        self.email = email
        self.password = password
        self.current_user = {}
        self.mates = []
        self.session = requests.Session()
        # Be able to save the cookies on a file specified, or save each user on a different email for multi account
        self.cookie_file = cookie_file or hashlib.sha512(email.encode('utf-8')).hexdigest()
        cookie_path = os.path.join(self.SESSIONS_FOLDER, self.cookie_file)
        if os.path.exists(cookie_path):
            with open(cookie_path, "rb") as file:
                # TODO: Watch out the expiration of the cookie
                LOGGER.info('Getting the session from cookies files')
                self.session.cookies.update(pickle.load(file))

    def login(self):
        """Login on the factorial web

        :return: boolean if is logged in
        """
        try:
            self.load_user_data()
            # Try to load the user info using the cookie, if can't login again using the username and password
            LOGGER.info('Already logged in, re-login is not needed')
            return True
        except UserNotLoggedIn:
            payload = {
                'utf8': '✓',
                'authenticity_token': self.generate_new_token(),
                'user[email]': self.email,
                'user[password]': self.password,
                'user[remember_me]': "0",
                'commit': 'Iniciar sesión'
            }

            response = self.session.post(url=self.SESSION_URL, data=payload)
            loggedin = response.status_code == http_client.CREATED
            if loggedin:
                LOGGER.info('Login successfully')
                # Load user data
                self.load_user_data()
                # Save the cookies if is logged in
                if not os.path.exists(self.SESSIONS_FOLDER):
                    os.mkdir(self.SESSIONS_FOLDER)
                with open(os.path.join(self.SESSIONS_FOLDER, self.cookie_file), "wb") as file:
                    pickle.dump(self.session.cookies, file)
                    LOGGER.info('Sessions saved')
            return loggedin

    @staticmethod
    def generate_new_token():
        """Generate new token to be able to login"""
        response = requests.get(url=FactorialClient.LOGIN_PAGE_URL)
        soup = BeautifulSoup(response.text, 'html.parser')
        auth_token = soup.find('input', attrs={'name': 'authenticity_token'})
        token_value = auth_token.get('value')
        if not token_value:
            raise AuthenticationTokenNotFound()
        return token_value

    @staticmethod
    def load_from_settings(credentials_loader: AbstractCredentials):
        """Login from the settings if the session still valid from the saved cookies, otherwise ask for the password

        :param credentials_loader: AbstractFactorialLoader load email and password from abstract class
        :return: FactorialClient
        """
        factorial_client = FactorialClient(email=credentials_loader.get_email(),
                                           password=credentials_loader.get_password())
        if not factorial_client.login():
            # Session valid with the current cookie
            raise ApiError('Cannot login with the given credentials')
        return factorial_client

    @staticmethod
    def split_time(time):
        """Split time to hour and minutes

        :param time: string time 7:30
        :return: tuple(hours, minutes)
        """
        return (int(t) for t in time.split(':'))

    @staticmethod
    def convert_to_minutes(hours, minutes):
        """Convert time to minutes

        :param hours: int
        :param minutes: int
        :return: int
        """
        return hours * 60 + minutes

    @staticmethod
    def convert_to_time(minutes):
        """Convert minutes to time

        :param minutes: int
        :return: tuple(hours, minutes)
        """
        converted_hours = int(minutes / 60)
        converted_minutes = int(minutes - converted_hours * 60)
        return converted_hours, converted_minutes

    @staticmethod
    def get_total_minutes_period(start_hours, start_minutes, end_hours, end_minutes):
        """Get total minutes for a period

        :param start_hours: int hours
        :param start_minutes: int minutes
        :param end_hours: int hours
        :param end_minutes: int minutes
        :return: total minutes
        """
        start_minutes = FactorialClient.convert_to_minutes(start_hours, start_minutes)
        end_minutes = FactorialClient.convert_to_minutes(end_hours, end_minutes)
        return end_minutes - start_minutes

    @staticmethod
    def get_random_number(start, end):
        """Get random number between two numbers, both included

        Eg:
        start = -10
        end = 10
        1 * (10 - -10) + -10 = 10
        0 * (10 - -10) + -10 = -10

        :param start: int start
        :param end: int end
        :return: int random number between start and end
        """
        return random.random() * (end - start) + start

    @staticmethod
    def random_time(hours, minutes, minutes_variation):
        """Variation between minutes

        :param hours: int current hour
        :param minutes: int current minutes
        :param minutes_variation: int minutes to variate
        :return: tuple (hours, minutes)
        """
        # Minutes variation of 10 will be a random between -10 and 10
        random_minutes_variation = FactorialClient.get_random_number(start=-minutes_variation, end=minutes_variation)
        # Pass hours and minutes to all minutes
        total_minutes = FactorialClient.convert_to_minutes(hours, minutes)
        # Remove or add the minutes variation
        variated_minutes = total_minutes + random_minutes_variation
        # Pass to hours and minutes
        return FactorialClient.convert_to_time(variated_minutes)

    def check_status_code(self, status_code, status_code_error, message=None):
        """Check if the call of the endpoint is correct

        :param status_code: HttpStatus
        :param status_code_error: HttpStatus
        :param message: string
        """
        if status_code == http_client.UNAUTHORIZED:
            raise UserNotLoggedIn()
        elif status_code != status_code_error:
            raise ApiError(message)

    def generate_period(self, start, end, minutes_variation):
        """Generate a period with a random variation

        :param start: string time
        :param end: string time
        :param minutes_variation: int minutes to variate
        :return: tuple (start_hours, start_minutes, end_hours, end_minutes)
        """
        start_hours, start_minutes = self.split_time(start)
        end_hours, end_minutes = self.split_time(end)
        total_minutes = self.get_total_minutes_period(start_hours, start_minutes, end_hours, end_minutes)
        start_sign_hour, start_sign_minutes = FactorialClient.random_time(start_hours, start_minutes, minutes_variation)
        end_sign_hour, end_sign_minutes = self.convert_to_time(
            self.convert_to_minutes(start_sign_hour, start_sign_minutes) + total_minutes
        )
        return start_sign_hour, start_sign_minutes, end_sign_hour, end_sign_minutes

    def add_breaks_to_period(self, start_sign_hour, start_sign_minutes, end_sign_hour, end_sign_minutes, breaks):
        """Add breaks for a period

        :return list of periods, tuple(start_hour, start_minute, end_hour, end_minute)
        """
        periods = []
        start_hour = start_sign_hour
        start_minute = start_sign_minutes
        for _break in sorted(breaks, key=lambda current_break: self.convert_to_minutes(current_break['start_hour'],
                                                                                       current_break['start_minute']),
                             reverse=False):
            break_start_hour = _break.get('start_hour')
            break_start_minute = _break.get('start_minute')
            break_end_hour = _break.get('end_hour')
            break_end_minute = _break.get('end_minute')
            periods.append({
                'start_hour': start_hour,
                'start_minute': start_minute,
                'end_hour': break_start_hour,
                'end_minute': break_start_minute
            })
            start_hour = break_end_hour
            start_minute = break_end_minute

        # End period
        periods.append({
            'start_hour': start_hour,
            'start_minute': start_minute,
            'end_hour': end_sign_hour,
            'end_minute': end_sign_minutes
        })
        return periods

    def generate_worked_periods(self, start_work, end_work, work_minutes_variation, breaks):
        """Generate worked periods with breaks

        :param start_work: string time
        :param end_work: string time
        :param work_minutes_variation: int minutes to variate
        :param breaks: list WorkBreak
        :return: list of periods
        """
        start_sign_hour, start_sign_minutes, end_sign_hour, end_sign_minutes = self.generate_period(start_work,
                                                                                                    end_work,
                                                                                                    work_minutes_variation
                                                                                                    )
        breaks_with_variation = []
        for _break in breaks:
            start_break_hour, start_break_minutes, end_break_hour, end_break_minutes = self.generate_period(
                start=_break.get_start_hour(),
                end=_break.get_end_hour(),
                minutes_variation=_break.get_minutes_variation()
            )
            breaks_with_variation.append({
                'start_hour': start_break_hour,
                'start_minute': start_break_minutes,
                'end_hour': end_break_hour,
                'end_minute': end_break_minutes
            })
        return self.add_breaks_to_period(start_sign_hour, start_sign_minutes, end_sign_hour, end_sign_minutes,
                                         breaks_with_variation)

    def worked_day(self, work_loader: AbstractWork, day=date.today()):
        """Mark today as worked day

        :param work_loader: AbstractCredentialLoader load the working hours
        :param day: date to save the worked day, by default is today
        """
        already_work = self.get_day(year=day.year, month=day.month, day=day.day)
        if already_work:
            if work_loader.get_resave():
                for worked_period in already_work:
                    self.delete_worked_period(worked_period.get('id'))
            else:
                LOGGER.info('Day already sign')
                return

        add_worked_period_kwargs = {
            'year': day.year,
            'month': day.month,
            'day': day.day,
            # Dynamic over loop fields
            'start_hour': 0,
            'start_minute': 0,
            'end_hour': 0,
            'end_minute': 0
        }
        worked_periods = self.generate_worked_periods(
            work_loader.get_start_hour(),
            work_loader.get_end_hour(),
            work_loader.get_minutes_variation(),
            work_loader.get_breaks()
        )
        for worked_period in worked_periods:
            start_hour = worked_period.get('start_hour')
            start_minute = worked_period.get('start_minute')
            end_hour = worked_period.get('end_hour')
            end_minute = worked_period.get('end_minute')
            add_worked_period_kwargs.update({
                'start_hour': start_hour,
                'start_minute': start_minute,
                'end_hour': end_hour,
                'end_minute': end_minute,
            })
            if self.add_worked_period(**add_worked_period_kwargs):
                LOGGER.info('Saved worked period for the day {0:s} between {1:02d}:{2:02d} - {3:02d}:{4:02d}'.format(
                    day.isoformat(),
                    start_hour, start_minute,
                    end_hour, end_minute))

    def logout(self):
        """Logout invalidating that session, invalidating the cookie _factorial_session

        :return: bool
        """
        response = self.session.delete(url=self.SESSION_URL)
        logout_correcty = response.status_code == http_client.NO_CONTENT
        LOGGER.info('Logout successfully {}'.format(logout_correcty))
        self.session = requests.Session()
        path_file = os.path.join(self.SESSIONS_FOLDER, self.cookie_file)
        if os.path.exists(path_file):
            os.remove(path_file)
            logging.info('Logout: Removed cookies file')
        self.mates.clear()
        self.current_user = {}
        return logout_correcty

    def load_employees(self):
        """Load employees info

        Example:
        [
            {
                'access_id'
                'birthday_on'
                'hired_on'
                'job_title'
                'id',
                'manager_id'
                'supervised_by_current'
                'terminated_on'
                'is_terminating'
                'timeoff_policy_id'
                'timeoff_manager_id'
                'timeoff_supervised_by_current'
                'location_id'
                'employee_group_id'
                'payroll_hiring_id'
                'is_eligible_for_payroll'
             }
        ]
        """
        LOGGER.info("Loading employees")
        employee_response = self.session.get(self.EMPLOYEE_URL)
        self.check_status_code(employee_response.status_code, http_client.OK)
        employee_json = employee_response.json()
        for employee in employee_json:
            # Update the user info that match the self.mates[n].id with employee.access_id
            for mate in self.mates:
                if mate.get('id') == employee.get('access_id'):
                    mate.update(employee)

            if self.current_user.get('id') == employee.get('access_id'):
                self.current_user.update(employee)

    def load_user_data(self):
        """Load info about your user
        Example:
        ```
        [
          {
            "id": <integer>,
            "user_id": <integer>,
            "company_id": <integer>,
            "invited": true,
            "invited_on": "YYYY-MM-DD",
            "role": "basic",
            "current": true/false,
            "calendar_token": null,
            "first_name": "sss",
            "last_name": "sss",
            "email": "sss@sss",
            "unconfirmed_email": null,
            "joined": true/false,
            "locale": "xx",
            "avatar": null,
            "tos": true
          },
          ...
        ]
        ```
        """
        self.mates.clear()
        self.current_user = {}
        response = self.session.get(url=self.USER_INFO_URL)
        self.check_status_code(response.status_code, http_client.OK)
        json_response = response.json()
        for user in json_response:
            current_user = user
            if current_user.get('current', False):
                self.current_user = current_user
            else:
                self.mates.append(current_user)

        self.load_employees()

    def get_period(self, year, month):
        """Get the info a period

        Example:
        [
          {
            "id": Period id<integer>,
            "employee_id": Employee id<integer>,
            "year": Year<integer>,
            "month": Month<integer>,
            "state": Status<string>,
            "estimated_minutes": Estimated minutes<integer>,
            "worked_minutes": Worked minuted<integer>,
            "distribution": Worked minutes each day Array<integer>[
              450,
              450,
              465,
              0,
              0,
              0,
              0,
              450,
              440,
              452,
              450,
              455,
              0,
              0,
              470,
              450,
              457,
              450,
              450,
              0,
              0,
              450,
              450,
              450,
              465,
              465,
              0,
              0,
              460,
              0,
              0
            ],
            "estimated_hours_in_cents": Hours in cents<integer>,
            "worked_hours_in_cents": Worked hours in cents<integer>,
            "distribution_in_cents": Cents earned each day Array<integer>[
              750,
              750,
              775,
              0,
              0,
              0,
              0,
              750,
              733,
              753,
              750,
              758,
              0,
              0,
              783,
              750,
              761,
              750,
              750,
              0,
              0,
              750,
              750,
              750,
              775,
              775,
              0,
              0,
              766,
              0,
              0
            ]
          }
        ]
        :param year: integer
        :param month: integer
        :return: dictionary
        """
        params = {
            'year': year,
            'month': month,
            'employee_id': self.current_user.get('id', '')
        }

        response = self.session.get(url=self.PERIODS_URL, params=params)
        self.check_status_code(response.status_code, http_client.OK)
        return response.json()

    def get_shift(self, year, month):
        """Get the current calendar with its worked days

        :param year: integer
        :param month: integer
        :return dictionary
        """
        period = self.get_period(year=year, month=month)
        current_period = period[0]
        period_id = current_period['id']
        params = {
            'period_id': period_id
        }
        response = self.session.get(self.SHIFT_URL, params=params)
        self.check_status_code(response.status_code, http_client.OK)
        return response.json()

    def get_day(self, year, month, day):
        """Get a specific worked day

        :param year: integer
        :param month: integer
        :param day: integer
        :return: dictionary
        """
        calendar = self.get_shift(year=year, month=month)
        worked_hours = []
        # return next(day_it for day_it in calendar if day_it['day'] == day)
        for day_it in calendar:
            if day_it.get('day') == day:
                worked_hours.append(day_it)
        return worked_hours

    def get_calendar(self, year, month, **kwargs):
        """Get all the laborable and left days

        :param year: int
        :param month: int
        :return: list of dictionary
        """
        params = {
            'id': self.current_user.get('id'),
            'year': year,
            'month': month
        }
        response = self.session.get(self.CALENDAR_URL, params=params)
        self.check_status_code(response.status_code, http_client.OK)
        response = response.json()
        for param, value in kwargs.items():
            response = [day for day in response if day.get(param) == value]
        return response

    def add_worked_period(self, year, month, day, start_hour, start_minute, end_hour, end_minute):
        """Add the period as worked

        Example to create a worked period for the day 2019-07-31 from 7:30 to 15:30
        - year 2019
        - month 7
        - day 31
        - start_hour 7
        - start_minute 30
        - end_hour 15
        - end_minute 30
        :param year: integer
        :param month: integer
        :param day: integer
        :param start_hour: integer
        :param start_minute: integer
        :param end_hour: integer
        :param end_minute: integer
        :return bool: correctly saved
        """
        # Check if are vacations
        calendar = self.get_calendar(year=year, month=month, is_leave=True)
        formatted_date = f'{year:04d}-{month:02d}-{day:02d}'
        for calendar_day in calendar:
            if calendar_day.get('date') == formatted_date:
                LOGGER.info(f"Can't sign today {formatted_date}, because are vacations")
                return False
        period = self.get_period(year=year, month=month)
        current_period = period[0]
        period_id = current_period['id']
        payload = {
            'clock_in': f'{start_hour}:{start_minute}',
            'clock_out': f'{end_hour}:{end_minute}',
            'day': day,
            'period_id': period_id
        }
        response = self.session.post(self.SHIFT_URL, data=payload)
        self.check_status_code(response.status_code, http_client.CREATED)
        return True

    def delete_worked_period(self, shift_id):
        """Delete a worked period

        :param shift_id: integer
        """
        url = f'{self.SHIFT_URL}/{shift_id}'
        response = self.session.delete(url)
        self.check_status_code(response.status_code, http_client.NO_CONTENT)

    def modify_worked_period(self, shift_id, period_id, start_hour, start_minute, end_hour, end_minute):
        """Modify the clock in and clock out of a specific day

        :param shift_id: integer
        :param period_id: integer
        :param start_hour: integer
        :param start_minute: integer
        :param end_hour: integer
        :param end_minute: integer
        """
        url = f'{self.SHIFT_URL}/{shift_id}'
        payload = {
            'clock_in': f"{start_hour}:{start_minute}",
            'clock_out': f"{end_hour}:{end_minute}",
            'period_id': period_id,
        }
        response = self.session.patch(url, data=payload)
        self.check_status_code(response.status_code, http_client.OK)

    def add_observation(self, shift_id, observation=None):
        """Add observation for a day

        :param shift_id: integer
        :param observation: string
        """
        url = f'{self.SHIFT_URL}/{shift_id}'
        payload = {
            'observations': observation
        }

        response = self.session.patch(url=url, data=payload)
        self.check_status_code(response.status_code, http_client.OK)
