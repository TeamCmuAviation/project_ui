from django.urls import path
from .views import LoginView, EvaluationInterfaceView, TaskListView

urlpatterns = [
    path('', LoginView.as_view(), name='login'),
    path('tasks/', TaskListView.as_view(), name='task_list'),
    path('evaluate/<str:uid>/', EvaluationInterfaceView.as_view(), name='evaluate'),
]
