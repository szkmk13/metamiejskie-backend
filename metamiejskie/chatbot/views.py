import groq
from django.conf import settings
from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from metamiejskie.chatbot.groq_utils import GroqClient
from metamiejskie.chatbot.models import Chat
from metamiejskie.chatbot.serializers import ChatSerializer, ChatListSerializer, ChatAskSerializer


@extend_schema(tags=["chatbot WORK IN PROGRESS"])
class ChatBotViewSet(
    # mixins.CreateModelMixin, mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return ChatListSerializer
        if self.action in ["ask", "talk"]:
            return ChatAskSerializer

        return ChatSerializer

    def get_queryset(self):
        return Chat.objects.filter(user=self.request.user)  # type: ignore[misc]

    @action(detail=False, methods=["POST"])
    def talk(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        chat_messages = serializer.validated_data["message"]
        client = GroqClient()
        response = client.get_completion(chat_messages)
        chat_messages.append({"role": "assistant", "content": response})
        return Response(chat_messages)

    # @action(detail=True, methods=["POST"])
    # def talk(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     message = serializer.validated_data["message"]
    #     chat = self.get_object()
    #     chat_messages = chat.context
    #     chat_messages.append({"role": "user", "content": message})
    #     client = GroqClient()
    #     response = client.get_completion(chat_messages)
    #     chat_messages.append({"role": "assistant", "content": response})
    #     chat.context = chat_messages
    #     chat.save(update_fields=["context"])
    #     return Response(response)
