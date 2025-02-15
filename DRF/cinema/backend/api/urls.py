from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.user_registration_view, name='registration'),
    path('confirmation/', views.user_confirmation_view, name='confirmation'),
    path('cinemas/', views.cinemas_list_view, name='cinema-list'),
    path('cinemas/<int:pk>/', views.cinema_retrive_view, name='cinema-detail'),
    path('sessions/', views.sessions_list_view, name='sessions-list'),
    path('sessions/<int:pk>/', views.session_retrive_view, name='sessions-detail'),
    path('sessions/<int:pk>/booking/', views.book_tickets_view, name='booking'),
    path('films/', views.films_list_view, name='films-list'),
    path('film/<int:pk>/', views.film_retrive_view, name='film-detail'),
    path('directors/', views.directors_list_view, name='directors-list'),
    path('directors/<int:pk>/', views.direcctor_retrive_view, name='directors-detail'),
    path('actors/', views.actors_list_view, name='actors-list'),
    path('actors/<int:pk>/', views.actor_retrive_view, name='actors-detail')
]