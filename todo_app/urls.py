from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/',auth_views.LoginView.as_view(redirect_authenticated_user=True),name='login'),
    path('',auth_views.LoginView.as_view(redirect_authenticated_user=True)),
    path('logout/',auth_views.LogoutView.as_view(),name='logout'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('dashboard/<str:task_filter>/',views.dashboard,name='dashboard'),
    path('password_change/',auth_views.PasswordChangeView.as_view(),name='password_change'),
    path('password_change/done/',auth_views.PasswordChangeDoneView.as_view(),name='password_change_done'),
    path('password_reset/',auth_views.PasswordResetView.as_view(),name='password_reset'),
    path('password_reset_done/',auth_views.PasswordResetDoneView.as_view(),name='password_reset_done'),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(),name='password_reset_confirm'),
    path('reset/done/',auth_views.PasswordResetCompleteView.as_view(),name='password_reset_complete'),
    path('register/',views.register,name='register'),
    path('edit/',views.edit,name='edit'),
    path('create/',views.task_create,name='create'),
    path('detail/<int:id>/<slug:slug>/', views.task_detail, name='detail'),
    path('toggle/<int:id>', views.toggle_task, name='toggle_task'),
    path('delete_task/<int:id>',views.delete_task, name='delete'),
    path('delete_filter/<str:task_filter>/',views.delete_filter,name='delete_filter'),
    path('mail_list/',views.mail_list,name='mail_list'),
    path('edit_task/<int:pk>/',views.ItemUpdate.as_view(),name='edit_task'),
]