import os
import dotenv
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

    return todo_items


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
