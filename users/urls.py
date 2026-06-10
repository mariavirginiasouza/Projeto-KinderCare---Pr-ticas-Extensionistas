from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_list, name='user_list'),
    path('novo/', views.user_create, name='user_create'),
    path('<int:pk>/editar/', views.user_update, name='user_update'),
    path('<int:pk>/excluir/', views.user_delete, name='user_delete'),
    path('<int:pk>/enviar-email-senha/', views.user_send_password_email, name='user_send_password_email'),
    path('definir-senha/<uidb64>/<token>/', views.password_set, name='password_set'),
    path('esqueceu-senha/', views.forgot_password, name='forgot_password'),
]
