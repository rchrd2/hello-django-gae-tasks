from django.urls import path, reverse
from django.views import View
from django.http import HttpResponse

from google.cloud import tasks_v2
from google.protobuf import timestamp_pb2

import datetime
import json

def create_task(project=None, queue=None, location=None, payload=None, in_seconds=None):
    client = tasks_v2.CloudTasksClient()

    # TODO(developer): Get these from settings.py / ENV
    project = 'hello-tasks-395419'
    queue = 'my-queue'
    location = 'us-west1'
    payload = 'hello' # or {'param': 'value'} for application/json
    in_seconds = None

    parent = client.queue_path(project, location, queue)

    task = {
        "app_engine_http_request": {
            "http_method": tasks_v2.HttpMethod.POST,
            "relative_uri": reverse("example_task_handler"),
        }
    }

    if payload is not None:
        if isinstance(payload, dict):
            payload = json.dumps(payload)
            task["app_engine_http_request"]["headers"] = {
                "Content-type": "application/json"
            }
        # The API expects a payload of type bytes.
        converted_payload = payload.encode()
        task["app_engine_http_request"]["body"] = converted_payload

    if in_seconds is not None:
        # Convert "seconds from now" into an rfc3339 datetime string.
        d = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(
            seconds=in_seconds
        )
        timestamp = timestamp_pb2.Timestamp()
        timestamp.FromDatetime(d)
        task["schedule_time"] = timestamp

    response = client.create_task(parent=parent, task=task)

    print(f"Created task {response.name}")
    return response

class CreateTaskView(View):
    def get(self, request):
        create_task()
        return HttpResponse('Task created')


class ExampleTaskHandlerView(View):
    def post(self, request):
        payload = request.body
        print(f"Received task with payload: {payload}")
        return HttpResponse('Task created')



urlpatterns = [
    path('create_task/', CreateTaskView.as_view(), name='create_task'),
    path('example_task_handler/', ExampleTaskHandlerView.as_view(), name='example_task_handler'),
]
