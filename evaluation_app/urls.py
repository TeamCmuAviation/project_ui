from django.urls import path
from .views import LoginView, EvaluationInterfaceView, TaskListView, random_task

urlpatterns = [
    path('', LoginView.as_view(), name='login'),
    path('tasks/', TaskListView.as_view(), name='task_list'),
    path('evaluate/<str:uid>/', EvaluationInterfaceView.as_view(), name='evaluate'),
    path('random/', random_task, name='random_task'),
]
