from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('predict/', views.predict_single, name='predict_single'),
    path('bulk/', views.predict_bulk, name='predict_bulk'),
    path('history/', views.history, name='history'),
    path('api/predict/', views.api_predict, name='api_predict'),
]
