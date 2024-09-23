from django.urls import path
from .views import negotiate

urlpatterns = [
    path('chatbot/negotiate/', negotiate, name='negotiate'),
]
