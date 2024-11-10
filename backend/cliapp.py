from functions import *

# This app is a basic interface for creating an interface to interact with the backend
print("Welcome to the CLI inerface")

# input("Press any button to continue to authentication")

# service = google_authenticate()

# print("AUTHENTICATED")

# created_event = service.events().quickAdd(
#     calendarId='primary',
#     text='Appointment at Somewhere on June 3rd 10am-10:25am').execute()

# print(created_event['id'])

print(get_all_user_courses())
print(get_course_name_by_id("417606"))
