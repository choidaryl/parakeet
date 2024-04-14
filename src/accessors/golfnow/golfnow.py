import requests, json, pytz
from datetime import datetime

import pprint

from constants import GOLFNOW_HEADER


class GolfnowClient:
    def __init__(self):
        # public
        self.session = requests.Session()
        # self.courses = json.load(open("golfnow_courses.json")) #  get rid of this. This shouldn't be here

        # private
        self._course_details = {
            "course":       None,
            "facility_id":  None,
            "address":      None,
            "city":         None,
            "state":        None,
            "minRate":      None
        }
        
        # self._auth_details = {
        #     "username":         None,
        #     "password":         None,
        #     "api_key":          "no_limits",
        #     "person_id":        None,
        #     "auth_token":       None
        # }

    @property
    def course_details(self): return self._course_details
    def has_course_details(self): return all(value is not None for value in self._course_details.values())
    def update_course_details(self, **kwargs): self._course_details.update(kwargs)

    # @property
    # def auth_details(self): return self._auth_details
    # def has_auth_details(Self): return all(value is not None for value in self._auth_details.values())
    # def update_auth_details(self, **kwargs): self._auth_details.update(kwargs)

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
    # def login(self, course:     str,
    #                 username:   str,
    #                 password:   str) -> int:
    #     try:
    #         # lock into one course from golfnow_courses.json
    #         course_details = self.courses.get(course)

    #         self.update_course_details(course=course,
    #                                    course_id=course_details.get("course_id"),
    #                                    booking_class=course_details.get("booking_classes")[0])
    #         self.update_auth_details(username=username, password=password)

    #         endpoint = "https://foreupsoftware.com/index.php/api/booking/users/login"

    #         data = {
    #             "username":             username,
    #             "password":	            password,
    #             "booking_class_id":     self.course_details.get("booking_class"),
    #             "api_key":              self.course_details.get("api_key"),
    #             "course_id":            self.course_details.get("course_id")
    #         }
    #         header = {**FOREUP_HEADER, "Referer": f"https://foreupsoftware.com/index.php/booking/{self.course_details.get('course_id')}"}

    #         response = self.post(endpoint, headers=header,data=data)

    #         if response.status_code == 200:
    #             self.update_auth_details(person_id=response.json().get("person_id"))
    #             self.update_auth_details(auth_token=response.json().get("jwt"))

    #             return 1
    #         else:
    #             return 0

    #     except requests.exceptions.ConnectionError:
    #         print("Failed to connect to the website.")
    #     except Exception as e:
    #         print(f"An error occurred: {e}")


    def get_tee_times(self,
                      date:         str,
                      facilityID:   int) -> dict:

        endpoint = f"https://www.golfnow.com/api/tee-times/tee-time-results"

        data = {
            "BestDealsOnly": False,
            "CurrentClientDate": datetime.now(pytz.utc),
            "Date": date,
            "ExcludeFeaturedFacilities": True,
            "FacilityId": facilityID,
            # "Holes": "3",
            # "Latitude":	"28.5383",
            # "Longitude":	"-81.3792",
            # "PageNumber":	0,
            # "PageSize":	30,
            # "Players":	"0",
            # "PriceMax":	"10000",
            # "PriceMin":	"0",
            # "PromotedCampaignsOnly": False,
            # "Radius":	25,
            # "RateType":	"all",
            "SearchType":	1,
            # "SortBy":	"Date",
            # "SortByRollup":	"Date.MinDate",
            # "SortDirection":	0,
            # "TeeTimeCount":	20,
            # "TimeMax":	"42",
            # "TimeMin":	"10",
            # "TimePeriod":	"3",
            "View":	"Grouping"
        }

        try:
            response = self.post(endpoint,headers=GOLFNOW_HEADER,data=data)
            if response.status_code == 200:
                self._course_details = {
                    "course":       None,
                    "facility_id":  None,
                    "address":      None,
                    "city":         None,
                    "state":        None,
                    "minRate":      None
                }
                teeTimes = response.json().get("ttResults").get("teeTimes")
                facility = teeTimes[0].get("facility")

                course = facility.get("name")
                facility_id = facility.get("facilityId")
                address = facility.get("address").get("line1")
                city = facility.get("address").get("city")
                state = facility.get("address").get("stateProvince")
                minRate = facility.get("minRateFormatted")

                self.update_course_details(
                    course=course,
                    facility_id=facility_id,
                    address=address,
                    city=city,
                    state=state,
                    minRate=minRate)
            return response.json()
        except requests.exceptions.ConnectionError:
            print(f"Failed to get Tee Times. date={date}. booking_class={booking_class}. schedule_id={schedule_id}")
        except Exception as e:
            print(f"An error occurred: {e}")
    
    def book_resy(self):
        pass

    def __repr__(self):
        return f"GolfnowClient(course_details={self.course_details}, auth_details={self.auth_details}"


client = GolfnowClient()
resp = client.get_tee_times("Mar 13 2024", 11400)
breakpoint()

