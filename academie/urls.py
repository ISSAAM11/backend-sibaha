from django.urls import path
from . import views

urlpatterns = [
    path('academy/', views.AcademyListView.as_view()),
    path('academy/<int:pk>/', views.AcademyDetailView.as_view()),
    path('my-academies/', views.MyAcademyListCreateView.as_view()),
    path('my-academies/<int:pk>/', views.MyAcademyUpdateView.as_view()),
    path('my-academies/<int:pk>/pools/', views.MyAcademyPoolCreateView.as_view()),
    path('my-academies/<int:pk>/pools/<int:pool_pk>/', views.MyAcademyPoolDetailView.as_view()),
    path('pool/', views.PoolListView.as_view()),
    path('pool/<int:pk>/', views.PoolDetailView.as_view()),
]
