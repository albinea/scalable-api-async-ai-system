from rest_framework import serializers


class ChatRequestSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    message = serializers.CharField()


class ChatResponseSerializer(serializers.Serializer):
    task_id = serializers.CharField()
    status = serializers.CharField()


class TaskStatusSerializer(serializers.Serializer):
    task_id = serializers.CharField()
    status = serializers.CharField()
    result = serializers.JSONField(required=False, allow_null=True)
    error = serializers.CharField(required=False, allow_null=True)


class HealthResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
    service = serializers.CharField()