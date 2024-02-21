from django.urls import path, include

from home import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search_english, name='search_english'),
    path('explore/<str:word>/', views.explore_word, name='explore_word'),
]