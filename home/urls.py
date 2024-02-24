from django.urls import path, include

from home import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search_english, name='search_english'),
    path('explore/<str:word>/', views.explore_word, name='explore_word'),
    # path('web/<str:word>/', views.word_usage_on_the_web, name='on_the_web'),
]

htmx_urls = [
    path('hx/<str:word>/<str:session_key>/',
         views.hx_load_web_data,
         name='hx_load_web_data'
         ),
]

urlpatterns += htmx_urls
