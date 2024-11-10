import json
from dateutil import parser
import os
import dotenv
import pytz
import requests
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']
# Base URL to access Canvas API
CANVAS_BASE_URL = "https://canvas.wisc.edu/api/v1"


def google_authenticate():
    """Handles user authentication and returns a Google Calendar service object with full calendar access."""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentia ls available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        # Return the authenticated service
        service = build("calendar", "v3", credentials=creds)
        return service
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None


def load_canvas_apikey():
    """Loads the canvas API keys. Returns the api key"""
    dotenv.load_dotenv()

    canvas_api_key = os.getenv("CANVAS_API_KEY")

    return canvas_api_key


def get_all_user_courses():
    """Gets the User's Canvas courses by ID. Returns a list of course IDs"""
    api_key = load_canvas_apikey()
    endpoint = f"{CANVAS_BASE_URL}/users/self/courses"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    course_ids = []
    while endpoint:
        response = requests.get(endpoint, headers=headers)

        if response.status_code == 200:
            courses = response.json()
            course_ids.extend([course['id'] for course in courses])

            # Check for pagination
            if 'next' in response.links:
                endpoint = response.links['next']['url']
            else:
                endpoint = None
        else:
            print(f"Error: {response.status_code}, {response.text}")
            return None

    return course_ids


def get_all_todo_assignments():
    """Get all assignments in Canvas ToDo List. Returns a list of all todo assignment objects (json)"""
    api_key = load_canvas_apikey()
    endpoint = f"{CANVAS_BASE_URL}/users/self/todo"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    todo_items = []
    while endpoint:
        response = requests.get(endpoint, headers=headers)

        if response.status_code == 200:
            todo_items.extend(response.json())

            # Check for pagination
            if 'next' in response.links:
                endpoint = response.links['next']['url']
            else:
                endpoint = None
        else:
            print(f"Error: {response.status_code}, {response.text}")
            return None

    todo_dict = {"assignments": todo_items}
    return json.dumps(todo_dict)


def get_course_name_by_id(id):
    """Get canvas course name when an id is passed. Returns a string"""
    api_key = load_canvas_apikey()
    endpoint = f"{CANVAS_BASE_URL}/courses/{id}"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    response = requests.get(endpoint, headers=headers)

    if response.status_code == 200:
        course = response.json()
        return course['name']
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None


def get_assignment_deadline(course_id, assignment_id):
    """Get assignment object's deadline. Gets the course id and assignment id and returns the assignment deadline."""
    api_key = load_canvas_apikey()
    endpoint = f"{
        CANVAS_BASE_URL}/courses/{course_id}/assignments/{assignment_id}"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    response = requests.get(endpoint, headers=headers)

    if response.status_code == 200:
        assignment = response.json()
        return assignment['due_at']
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None


def find_free_time_slots(events, start_time, end_time):
    """
    Identifies free time slots between the current events.

    Args:
    - events: List of Google Calendar events.
    - start_time: The time from which scheduling can start (usually "now").
    - end_time: The assignment due date.

    Returns:
    - A list of free time slots (each slot is a tuple of start and end datetime).
    """
    free_slots = []

    # Sort events by their start time
    events = sorted(events, key=lambda x: parser.parse(x['start']['dateTime']))

    # Start from the current time
    current_time = start_time

    for event in events:
        event_start = parser.parse(event['start']['dateTime'])
        event_end = parser.parse(event['end']['dateTime'])

        # Check if there is a gap between the current time and the next event
        if current_time < event_start:
            free_slots.append((current_time, event_start))

        # Move current_time forward to the end of this event
        current_time = max(current_time, event_end)

    # If there is free time after the last event but before the end time
    if current_time < end_time:
        free_slots.append((current_time, end_time))

    return free_slots


def split_into_time_blocks(total_hours, free_slots, splittable):
    """
    Splits the required time into appropriate blocks based on free time slots and whether it's splittable.

    Args:
    - total_hours: The total number of hours the user needs to complete the assignment.
    - free_slots: List of free time slots (each slot is a tuple of start and end datetime).
    - splittable: Boolean indicating if the task can be split into 1-hour blocks.

    Returns:
    - A list of scheduled blocks (each block is a tuple of start and end datetime).
    """
    scheduled_blocks = []
    remaining_hours = total_hours

    for free_start, free_end in free_slots:
        free_time = (free_end - free_start).total_seconds() / \
            3600  # Convert to hours

        if remaining_hours <= 0:
            break

        if splittable:
            while free_time >= 1 and remaining_hours > 0:
                block_start = free_start
                block_end = block_start + datetime.timedelta(hours=1)
                scheduled_blocks.append((block_start, block_end))
                remaining_hours -= 1
                free_start = block_end
                free_time -= 1
        else:
            if free_time >= remaining_hours:
                # Schedule the entire task
                block_start = free_start
                block_end = block_start + \
                    datetime.timedelta(hours=remaining_hours)
                scheduled_blocks.append((block_start, block_end))
                remaining_hours = 0
            else:
                # Skip current free block as it is too short to do anything
                continue

    return scheduled_blocks


def schedule_assignment(service, assignment_json, time_required, splittable):
    """
    Schedules time to complete an assignment in the user's Google Calendar.

    Args:
    - service: The authenticated Google Calendar service object.
    - assignment_json: The assignment data from Canvas (as JSON) containing due date and other info.
    - time_required: The total number of hours the assignment is estimated to take.
    - splittable: Boolean indicating if the assignment can be split into smaller 1-hour blocks.

    Returns:
    - List of scheduled time blocks.
    """
    # Get the assignment details
    assignment_name = assignment_json['assignment']['name']
    due_date = assignment_json['assignment']['due_at']  # ISO 8601 date string
    due_datetime = parser.parse(due_date).astimezone(
        pytz.UTC)  # Convert to UTC datetime

    # Get the current time (ensure it's in UTC format)
    now = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)

    # Debug: Check the formatting of the times
    print(f"Current time (now): {now.isoformat()}Z")
    print(f"Assignment due time: {due_datetime.isoformat()}Z")

    # Get events from Google Calendar between now and the assignment's due date
    try:
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now.isoformat(),  # UTC time, no 'Z' needed as it's already in UTC
            timeMax=due_datetime.isoformat(),
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])
        print(f"Fetched {len(events)} events.")

    except HttpError as error:
        print(f"An error occurred: {error}")
        return None

    # Find free time slots
    free_slots = find_free_time_slots(events, now, due_datetime)

    # Split the time required into blocks based on free time slots
    scheduled_blocks = split_into_time_blocks(
        time_required, free_slots, splittable)

    # Add the scheduled blocks to Google Calendar
    for block_start, block_end in scheduled_blocks:
        event = {
            'summary': f'Work on {assignment_name}',
            'description': f'Time to work on {assignment_name}',
            'start': {
                'dateTime': block_start.isoformat(),
                'timeZone': 'America/Chicago',
            },
            'end': {
                'dateTime': block_end.isoformat(),
                'timeZone': 'America/Chicago',
            },
            'reminders': {
                'useDefault': True,
            },
        }
        try:
            service.events().insert(calendarId='primary', body=event).execute()
            print(f"Scheduled block: {block_start} to {block_end}")
        except HttpError as error:
            print(f"An error occurred while adding event: {error}")

    return scheduled_blocks
