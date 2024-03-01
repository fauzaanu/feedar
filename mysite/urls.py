"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin, sitemaps
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include

from django.contrib.sitemaps import Sitemap
from django.utils import timezone

from home.models import Word


class RadheefSitemap(Sitemap):
    changefreq = "daily"

    def items(self):
        # last 50 words
        return Word.objects.filter(
            word__isnull=False
        ).order_by("-id")[:10000]

    def location(self, obj):
        return f"/explore/{obj.word}"


urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("pwa.urls")),
    path('', include('home.urls')),
    path('about/', include('about.urls')),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": {"radheef": RadheefSitemap()}},
        name="django.contrib.sitemaps.views.sitemap",
    )
]
