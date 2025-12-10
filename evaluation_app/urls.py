from django.urls import path
from .views import LoginView, EvaluationInterfaceView, TaskListView, random_task, DashboardView, logout_view, dashboard_chart_data

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('dashboard/api/chart-data/', dashboard_chart_data, name='dashboard_chart_data'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('tasks/', TaskListView.as_view(), name='task_list'),
    path('evaluate/<str:uid>/', EvaluationInterfaceView.as_view(), name='evaluate'),
    path('random/', random_task, name='random_task'),
]
