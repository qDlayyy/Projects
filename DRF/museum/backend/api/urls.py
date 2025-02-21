from django.urls import path
from . import views

urlpatterns = [
    path('registration/', views.user_registration_view, name='registration'),
    path('registration/<str:token>/', views.user_confirmation_view, name='confirmation'),
    path('museums/', views.museum_list_view, name='museums-list'),
    path('museums/<int:pk>/', views.museum_retrive_view, name='museums-detail'),
    path('authors/', views.authors_list_view, name='authors-list'),
    path('authors/<int:pk>/', views.authors_retrive_view, name='authors-detail'),
    path('exhibits/', views.exhibits_list_view, name='exhibits-list'),
    path('exhibits/<int:pk>/', views.exhibits_retrive_view, name='exhibits-detail')
]