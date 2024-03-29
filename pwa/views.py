import os

from django.http import HttpResponse
from django.shortcuts import render

from mysite.settings.base import BASE_DIR

# PWA_SERVICE_WORKER_PATH = BASE_DIR + "/pwa/static/pwa/serviceworker.js"
# PWA_MANIFEST_PATH = BASE_DIR + "/pwa/static/pwa/app.webmanifest"

PWA_SERVICE_WORKER_PATH = os.path.join(BASE_DIR, "pwa", "static", "pwa", "serviceworker.js")
PWA_MANIFEST_PATH = os.path.join(BASE_DIR, "pwa", "static", "pwa", "app.webmanifest")


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


def robots(request):
    # allow everything for robots.txt
    return HttpResponse("User-agent: *\nDisallow:", content_type="text/plain")