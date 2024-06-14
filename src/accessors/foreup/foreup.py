import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime
import os

from constants import FOREUP_HEADER

import pprint


class ForeupClient:
    def __init__(self):
        # public
        self.session = requests.Session()
        self.courses = json.load(open("src/accessors/foreup/foreup_courses.json")) #  get rid of this. This shouldn't be here

        # private
        self._course_details = {
            "course":           None,           # str
            "course_id":        None,           # int
            "booking_class":    None,           # int
            "schedule_id":      None,           # int
        }
        
        self._auth_details = {
            "username":         None,           # str
            "password":         None,           # str
            "api_key":          "no_limits",    # str
            "person_id":        None,           # str
            "auth_token":       None            
        }

        self._tee_times = {}

        self._reservation_details = {
            "reservation_id":   None,           # str
            "date":             None,           # datetime.datetime
            "time":             None            # time
        }

    @property
    def course_details(self): return self._course_details
    def has_course_details(self): return all(value is not None for value in self._course_details.values())
    def update_course_details(self, **kwargs): self._course_details.update(kwargs)

    @property
    def auth_details(self): return self._auth_details
    def has_auth_details(Self): return all(value is not None for value in self._auth_details.values())
    def update_auth_details(self, **kwargs): self._auth_details.update(kwargs)

    @property
    def tee_times(self): return self._tee_times
    def has_tee_times(Self): return all(value is not None for value in self._tee_times.values())
    def update_tee_times(self, **kwargs): self._tee_times.update(kwargs)

    @property
    def reservation_details(self): return self._reservation_details
    def has_reservation_details(Self): return all(value is not None for value in self._reservation_details.values())
    def update_reservation_details(self, **kwargs): self._reservation_details.update(kwargs)

    # Session get
    def get(self, url:      str,
                  headers:  dict = None) -> dict:
        return self.session.get(url, headers=headers)

    # Session post
    def post(self, url:     str,
                   headers: dict,
                   data:    dict) -> dict:
        return self.session.post(url, headers=headers, data=data)

    # Login
    def login(self, course:     str,
                    username:   str,
                    password:   str) -> int:
        try:
            # lock into one course from foreup_courses.json
            course_details = self.courses.get(course)

            self.update_course_details(course=course,
                                       course_id=course_details.get("course_id"),
                                       booking_class=course_details.get("booking_classes")[0])
            self.update_auth_details(username=username, password=password)

            endpoint = "https://foreupsoftware.com/index.php/api/booking/users/login"

            data = {
                "username":             username,
                "password":	            password,
                "booking_class_id":     self.course_details.get("booking_class"),
                "api_key":              self.course_details.get("api_key"),
                "course_id":            self.course_details.get("course_id")
            }
            header = {**FOREUP_HEADER, "Referer": f"https://foreupsoftware.com/index.php/booking/{self.course_details.get('course_id')}"}

            response = self.post(endpoint, headers=header,data=data)

            if response.status_code == 200:
                self.update_auth_details(person_id=response.json().get("person_id"))
                self.update_auth_details(auth_token=response.json().get("jwt"))

                return 1
            else:
                return 0

        except requests.exceptions.ConnectionError:
            print("Failed to connect to the website.")
        except Exception as e:
            print(f"An error occurred: {e}")


    def get_tee_times(self, date:   str,
                            course: str):

        course_details = self.courses.get(course)
        schedule_id, booking_class = course_details.get("schedule_id"), course_details.get("booking_classes")[0]
        
        date_obj = datetime.strptime(date, "%m-%d-%Y")

        self.update_course_details(schedule_id=schedule_id)
        self.update_reservation_details(date=date_obj)

        endpoint = f"https://foreupsoftware.com/index.php/api/booking/times?time=all&date={date}&holes=all&players=0&booking_class={booking_class}&schedule_id={schedule_id}&schedule_ids[]={schedule_id}&specials_only=0&api_key=no_limits"
        try:
            response = self.get(endpoint)

            timesheet = {}
            date_str = ""
            for booking_detail in response.json():
                splice = booking_detail["time"].split(" ")
                date_str, time_str = splice[0], splice[1]
                timesheet[time_str] = booking_detail

            self.update_tee_times(times=timesheet)
        except requests.exceptions.ConnectionError:
            print(f"Failed to get Tee Times. date={date}. booking_class={booking_class}. schedule_id={schedule_id}")
        except Exception as e:
            print(f"An error occurred: {e}")
    

    def book_resy(self,
                  date:     str,
                  time:     str):
        try:
            time_str = datetime.strptime(time, "%H:%M")

            self.update_reservation_details(time=time_str)

            endpoint = "https://foreupsoftware.com/index.php/api/booking/pending_reservation"

            teetime = self.tee_times["times"].get(time)

            data={
                "time":                 date+"+"+time,
                "holes":                teetime.get("holes"),
                "players":              teetime.get("maximum_players_per_booking"),
                "carts":                False,      # TODO
                "schedule_id":          self.course_details.get("schedule_id"),
                "teesheet_side_id":     teetime.get("teesheet_side_id"),
                "course_id":            self.course_details.get("course_id"),
                "booking_class_id":     self.course_details.get("booking_class"),
                "duration":             1,          # TODO
                "foreup_discount":      teetime.get("foreup_discount"),
                "foreup_trade_discount_rate": teetime.get("foreup_trade_discount_rate"),
                "trade_min_players":    teetime.get("trade_min_players"),
                "cart_fee":             teetime.get("cart_fee"),
                "cart_fee_tax":         teetime.get("cart_fee_tax"),
                "green_fee":            teetime.get("green_fee"),
                "green_fee_tax":        teetime.get("green_fee_tax")
            }

            header = {
                **FOREUP_HEADER,
                "X-Authorization": f"Bearer {self.auth_details.get('auth_token')}",
                "X-Fu-Golfer-Location": "foreup",
                "Referer": f"https://foreupsoftware.com/index.php/booking/{self.course_details.get('course_id')}/{self.course_details.get('schedule_id')}"
            }

            response = self.session.post(endpoint,headers=header,data=data)

            breakpoint()
            return response
        except requests.exceptions.ConnectionError:
            print("Failed to connect to the website.")
        except Exception as e:
            print(f"An error occurred: {e}")


    def __repr__(self):
        return f"ForeupClient(course_details={self.course_details}, auth_details={self.auth_details}"


# login
foreup = ForeupClient()
course = input("course: ")
email = input("email: ")
password = input("password: ")
foreup.login(course, email, password)

# load tee times
date = input("date: ")
foreup.get_tee_times(date, course)
pprint.pp(foreup.tee_times)

# book tee time
time = input("time: ")
res = foreup.book_resy(date, time)

# cancel tee time
# appointments = foreup.find_appointments()
# foreup.cancel_appointment(time, date)

# reschedule tee time
