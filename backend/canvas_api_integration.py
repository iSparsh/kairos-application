import requests
import dotenv
import os

dotenv.load_dotenv()
CANVAS_API_KEY = os.getenv("CANVAS_API_KEY")
CANVAS_BASE_URL = "https://canvas.wisc.edu/api/v1"

print(CANVAS_API_KEY)


def fetching_todo_items():
    endpoint = f"{CANVAS_BASE_URL}/users/self/todo"

    headers = {
        "Authorization": f"Bearer {CANVAS_API_KEY}"
    }

    # Make the GET request
    response = requests.get(endpoint, headers=headers)

    # Check the response status
    if response.status_code == 200:
        # Parse the JSON response
        todo_items = response.json()
        # for item in todo_items:
        #     print(f"Title: {item['title']}")
        #     print(f"Type: {item['type']}")
        #     print(f"Due Date: {item.get('due_at', 'No due date')}")
        #     print(f"Course: {item['context_name']}")
        #     print("-" * 40)
        for todo in todo_items:
            print("-"*20)
            print(f"Course: {todo['context_name']}")
            print(f"Title: {todo['assignment'].get("name")}")
            print(f"Course URL: {todo['html_url']}")
            print("-"*20)
    else:
        print(f"Failed to fetch To-Do items: {response.status_code}")
        print("Error:", response.text)


fetching_todo_items()
