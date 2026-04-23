from django.urls import path
from . import views

urlpatterns = [
    path('academy/', views.academy_list),
    path('academy/<int:pk>/', views.academy_detail),
]
