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
    path('academy/<int:pk>/reviews/', views.AcademyReviewListCreateView.as_view()),
    path('my-academies/<int:pk>/invitations/', views.AcademyInvitationListCreateView.as_view()),
    path('academy/<int:pk>/subscribe/', views.SubscribeView.as_view()),
    path('my-subscriptions/', views.MySubscriptionsView.as_view()),
    path('my-academies/<int:pk>/clients/', views.AcademyClientListView.as_view()),
    path('my-academies/<int:pk>/clients/<int:subscription_pk>/', views.AcademyClientDetailView.as_view()),
    path('my-invitations/', views.MyInvitationListView.as_view()),
    path('my-invitations/<int:pk>/', views.MyInvitationDetailView.as_view()),
    path('my-courses/', views.MyCoursesView.as_view()),
    path('my-academies/<int:pk>/courses/', views.AcademyCourseListCreateView.as_view()),
    path('my-academies/<int:pk>/courses/<int:course_pk>/', views.AcademyCourseDetailView.as_view()),
    path('courses/<int:pk>/enroll/', views.CourseEnrollView.as_view()),
    path('my-enrollments/', views.MyEnrollmentsView.as_view()),
    path('my-enrollments/<int:pk>/', views.DeleteEnrollmentView.as_view()),
]
