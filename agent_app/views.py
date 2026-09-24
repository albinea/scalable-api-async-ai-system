from celery.result import AsyncResult

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema

from .tasks import run_ai_inference
from .serializers import (
    ChatRequestSerializer,
    ChatResponseSerializer,
    TaskStatusSerializer,
    HealthResponseSerializer,
)


@extend_schema(
    request=ChatRequestSerializer,
    responses={
        202: ChatResponseSerializer,
        400: dict,
    },
)
@api_view(["POST"])
def chat(request):

    serializer = ChatRequestSerializer(
        data=request.data
    )

    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    user_id = serializer.validated_data["user_id"]
    message = serializer.validated_data["message"]

    task = run_ai_inference.delay(
        user_id,
        message,
    )

    return Response(
        {
            "task_id": task.id,
            "status": "PENDING",
        },
        status=status.HTTP_202_ACCEPTED,
    )


@extend_schema(
    responses=TaskStatusSerializer,
)
@api_view(["GET"])
def task_status(request, task_id):

    task = AsyncResult(task_id)

    response = {
        "task_id": task_id,
        "status": task.status,
    }

    if task.successful():
        response["result"] = task.result

    elif task.failed():
        response["error"] = str(task.result)

    return Response(response)


@extend_schema(
    responses=HealthResponseSerializer,
)
@api_view(["GET"])
def health(request):

    return Response(
        {
            "status": "healthy",
            "service": "react-agent",
        }
    )