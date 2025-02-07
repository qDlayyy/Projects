from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

router.register(r'admin/plants', views.AdminPlantsViewSet, basename='admin-plants')
router.register(r'admin/tips', views.AdminTips, basename='admin-tips')
router.register(r'diary', views.DiaryViewSet, basename='diary')
router.register(r'gallery', views.GalleryView, basename='gallery')

urlpatterns = [
    path('', include(router.urls)),
    path('registration/', views.user_register_view, name='user-registration'),
    path('registration/<str:token>/', views.user_confirmation_view, name='user-confirmation'),
    path('plants/', views.all_plants_view, name='plants'),
    path('plants/<int:pk>/', views.retrive_plant_view, name='retrive-plant'),
]