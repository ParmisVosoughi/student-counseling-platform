from django.urls import path
from .views import SupervisorDashboardView,AdvisorDashboardView,AdminDashboardView,StudentSummaryView,AdvisorSummaryView
urlpatterns=[path('supervisor/',SupervisorDashboardView.as_view()),path('advisor/',AdvisorDashboardView.as_view()),path('admin/',AdminDashboardView.as_view()),path('student/<int:pk>/summary/',StudentSummaryView.as_view()),path('advisor/<int:pk>/summary/',AdvisorSummaryView.as_view())]
