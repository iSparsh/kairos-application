from functions import *

# This app is a basic interface for creating an interface to interact with the backend
print("Welcome to the CLI inerface")

input("Press any button to continue to authentication")

service = google_authenticate()

print("AUTHENTICATED")

# created_event = service.events().quickAdd(
#     calendarId='primary',
#     text='Appointment at Somewhere on June 3rd 10am-10:25am').execute()

# print(created_event['id'])

test_ass = get_all_todo_assignments()

# if service:
#     blocks = schedule_assignment(service, test_ass, 2, False)
#     print("DONE SCHEDULING IN GOOGLE CALENDAR")
#     print(blocks)

# else:
#     print("Error in getting the service variable.")

print(test_ass)
