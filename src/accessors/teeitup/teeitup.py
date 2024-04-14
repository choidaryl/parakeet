# import requests
# import json
# from bs4 import BeautifulSoup
# import os

# from constants import TEEITUP_HEADER

# import pprint


# class TeeitupClient:
#     def __init__(self):
#         # public
#         self.session = requests.Session()
#         self.courses = json.load(open("teeitup_courses.json")) #  get rid of this. This shouldn't be here

#         # private
#         self._course_details = {
#             "course":           None,
#             "course_id":        None,
#             "booking_class":    None,
#             "schedule_id":      None,
#         }
        
#         self._auth_details = {
#             "username":         None,
#             "password":         None,
#             "api_key":          "no_limits",
#             "person_id":        None,
#             "auth_token":       None
#         }

#     @property
#     def course_details(self): return self._course_details
#     def has_course_details(self): return all(value is not None for value in self._course_details.values())
#     def update_course_details(self, **kwargs): self._course_details.update(kwargs)

#     @property
#     def auth_details(self): return self._auth_details
#     def has_auth_details(Self): return all(value is not None for value in self._auth_details.values())
#     def update_auth_details(self, **kwargs): self._auth_details.update(kwargs)

#     # Session get
#     def get(self, url:      str,
#                   headers:  dict = None) -> dict:
#         return self.session.get(url, headers=headers)

#     # Session post
#     def post(self, url:     str,
#                    headers: dict,
#                    data:    dict) -> dict:
#         return self.session.post(url, headers=headers, data=data)

#     # Login
#     def login(self, course:     str,
#                     username:   str,
#                     password:   str) -> int:
#         try:
#             # foreup.json - lock into one course
#             course_details = self.courses.get(course)

#             self.update_course_details(course=course,
#                                        course_id=course_details.get("course_id"),
#                                        booking_class=course_details.get("booking_classes")[0])
#             self.update_auth_details(username=username, password=password)

#             endpoint = "https://foreupsoftware.com/index.php/api/booking/users/login"

#             data = {
#                 "username":             username,
#                 "password":	            password,
#                 "booking_class_id":     self.course_details.get("booking_class"),
#                 "api_key":              self.course_details.get("api_key"),
#                 "course_id":            self.course_details.get("course_id")
#             }
#             header = {**FOREUP_HEADER, "Referer": f"https://foreupsoftware.com/index.php/booking/{self.course_details.get('course_id')}"}

#             response = self.post(endpoint, headers=header,data=data)

#             if response.status_code == 200:
#                 self.update_auth_details(person_id=response.json().get("person_id"))
#                 self.update_auth_details(auth_token=response.json().get("jwt"))

#                 return 1
#             else:
#                 return 0

#         except requests.exceptions.ConnectionError:
#             print("Failed to connect to the website.")
#         except Exception as e:
#             print(f"An error occurred: {e}")


#     def get_tee_times(self, date:   str,
#                             course: str) -> list:

#         course_details = self.courses.get(course)
#         schedule_id, booking_class = course_details.get("schedule_id"), course_details.get("booking_classes")[0]
#         self.update_course_details(schedule_id=schedule_id)

#         endpoint = f"https://foreupsoftware.com/index.php/api/booking/times?time=all&date={date}&holes=all&players=0&booking_class={booking_class}&schedule_id={schedule_id}&schedule_ids[]={schedule_id}&specials_only=0&api_key=no_limits"
#         try:
#             response = self.get(endpoint)

#             return response.json()
#         except requests.exceptions.ConnectionError:
#             print(f"Failed to get Tee Times. date={date}. booking_class={booking_class}. schedule_id={schedule_id}")
#         except Exception as e:
#             print(f"An error occurred: {e}")
    
#     def book_resy(self):
#         pass

#     def __repr__(self):
#         return f"ForeupClient(course_details={self.course_details}, auth_details={self.auth_details}"



# foreup = ForeupClient()
# course = input("course: ")
# email = input("email: ")
# password = input("password: ")
# resp = foreup.login(course, email, password)
# print(f"login={resp}")

# date = input("date: ")
# teetimes = foreup.get_tee_times(date, course)
# pprint.pp(teetimes)