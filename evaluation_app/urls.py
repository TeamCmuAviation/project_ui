from django.urls import path
from .views import (
    LoginView, 
    EvaluationInterfaceView, 
    TaskListView, 
    random_task, 
    DashboardView, 
    logout_view, 
    dashboard_chart_data, 
    dashboard_category_data, 
    dashboard_geo_data, 
    dashboard_location_bar_data, 
    dashboard_table_data, 
    dashboard_operator_data,
    dashboard_phase_data
)

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('dashboard/api/chart-data/', dashboard_chart_data, name='dashboard_chart_data'),
    path('dashboard/api/category-data/', dashboard_category_data, name='dashboard_category_data'),
    path('dashboard/api/geo-data/', dashboard_geo_data, name='dashboard_geo_data'),
    path('dashboard/api/location-bar-data/', dashboard_location_bar_data, name='dashboard_location_bar_data'),
    path('dashboard/api/table-data/', dashboard_table_data, name='dashboard_table_data'),
    path('dashboard/api/operator-data/', dashboard_operator_data, name='dashboard_operator_data'),
    path('dashboard/api/phase-data/', dashboard_phase_data, name='dashboard_phase_data'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('tasks/', TaskListView.as_view(), name='task_list'),
    path('evaluate/<str:uid>/', EvaluationInterfaceView.as_view(), name='evaluate'),
    path('random/', random_task, name='random_task'),
]
