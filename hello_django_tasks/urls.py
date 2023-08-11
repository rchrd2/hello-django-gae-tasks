from django.urls import path, reverse
from django.views import View
from django.http import HttpResponse

from google.cloud import tasks_v2
from google.protobuf import timestamp_pb2

import datetime
import json

# TODO(developer): Get these from settings.py / ENV
PROJECT = 'hello-tasks-395419'
QUEUE = 'my-queue'
LOCATION = 'us-west1'

def create_task(url, payload={}):
    """
    Create a task for a given queue with an arbitrary payload.

    payload (dict): The payload of the task.
    """
    client = tasks_v2.CloudTasksClient()
    parent = client.queue_path(PROJECT, LOCATION, QUEUE)
    task = {
        "app_engine_http_request": {
            "http_method": "POST",
            "relative_uri": url,
            "headers": {
                "Content-type": "application/json"
            },
            "body": json.dumps(payload).encode()
        }
    }
    response = client.create_task(parent=parent, task=task)
    print(f"Created task {response.name}")
    return response

class CreateTaskView(View):
    def get(self, request):
        create_task(reverse("example_task_handler"), payload={"message": "Hello World"})
        return HttpResponse('Task created')


class ExampleTaskHandlerView(View):
    def post(self, request):
        payload = json.loads(request.body)
        print(f"Received task with payload: {payload}")
        return HttpResponse('Task created')


urlpatterns = [
    path('create_task/', CreateTaskView.as_view(), name='create_task'),
    path('example_task_handler/', ExampleTaskHandlerView.as_view(), name='example_task_handler'),
]
