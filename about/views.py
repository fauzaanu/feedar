import os

from django.shortcuts import render

from mysite.settings.base import BASE_DIR


# Create your views here.
def about(request):
    trello_link = "https://trello.com/b/iIeOs87c/radheefu-project"
    github_link = "https://github.com/fauzaanu/feedar"

    strings_dir = os.path.join(BASE_DIR, "about", "strings")

    about = str()
    with open(os.path.join(strings_dir, "about.txt"), "r",encoding='utf-8') as f:
        about = f.read()

    heading = str()
    with open(os.path.join(strings_dir, "heading.txt"), "r",encoding='utf-8') as f:
        heading = f.read()

    sub_heading = str()
    with open(os.path.join(strings_dir, "subheading.txt"), "r",encoding='utf-8') as f:
        sub_heading = f.read()

    content = []
    with open(os.path.join(strings_dir, "content.txt"), "r",encoding='utf-8') as f:
        content = f.read()
        content = content.split("\n")

    context = {
        "trello_link": trello_link,
        "github_link": github_link,
        "about": about,
        "heading": heading,
        "sub_heading": sub_heading,
        "content": content,
    }

    return render(request, 'about/about.html', context)
