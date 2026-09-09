from django.urls import path

from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.report_list, name='report_list'),
    path('report/', views.report_create, name='report_create'),
    path(
        '<int:pk>/progress/add/',
        views.progress_create,
        name='progress_create',
    ),
    path(
        'progress/<int:pk>/edit/',
        views.progress_edit,
        name='progress_edit',
    ),
    path(
        'progress/<int:pk>/delete/',
        views.progress_delete,
        name='progress_delete',
    ),
    path('<int:pk>/edit/', views.report_edit, name='report_edit'),
    path('<int:pk>/delete/', views.report_delete, name='report_delete'),
    path('<int:pk>/', views.report_detail, name='report_detail'),
]