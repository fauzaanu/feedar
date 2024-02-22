from django.http import HttpResponse
from django.shortcuts import render

from mysite.settings.base import PROJECT_DIR

PWA_SERVICE_WORKER_PATH = PROJECT_DIR + "pwa/static/serviceworker.js"
PWA_MANIFEST_PATH = PROJECT_DIR + "pwa/static/app.webmanifest"


def service_worker(request):
    response = HttpResponse(
        open(PWA_SERVICE_WORKER_PATH).read(), content_type="application/javascript"
    )
    return response


def manifest(request):
    response = HttpResponse(
        open(PWA_MANIFEST_PATH).read(), content_type="application/javascript"
    )
    return response


def offline(request):
    return render(request, "pwa/offline.html")