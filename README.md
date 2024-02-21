## DRP

Django + Redis + Postgres

A very vanilla way to build with django, using django and django templates as much as possible.

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/AcACbH?referralCode=NC4Tt6)

### Tailwindcss

- The `jstoolchain` folder includes a tailwindcss setup
- You should run `npm i` to install the dependencies
- There is also a `.xml` file for PyCharm users to make it a `File Watcher`
- The `tailwind.config.js` file is configured to search for `html` and `py` files
- `.py` files because forms.py could have tailwindcss classes due to the user of `crispy-forms` with `crispy-tailwind`

### Icon Library

- The project template directory includes a folder called `icons` which contains lucide icons (https://lucide.dev/)
- The idea is to use django template tag of include and add the icons to the templates
- Example: `{% include 'icons/arrow-right.svg' %}`

### Toasts

- Toasts from https://github.com/talsu/vanilla-toast are included by default
- any view that sends a context with the keys present on `mysite/templates/toast/toast_body.html` will display a toast
- Eg: toast_message, toast_error, toast_success
- For example: After some action is complete a session variable can be set and the view can be redirected to the main
  page that would display the toast. This page should also delete the session variable so that it can never repeat.

### Role of Redis

- Redis is used as a cache firstly
- Secondly, it is used to run huey tasks
- Thirdly, it is used as a session store
- Compared to running redis on upstash, railway so far seems to be much better. (Needs more testing with multiple
  projects to be sure)

### Huey

> Initially we used celery however switching to huey ran the tasks reliably and saved around 1.5GB of RAM on the server
> which would be a better starting point initially as cost could be a factor.

- Huey is used as a task queue (same as celery, but more lightweight)
- It is configured to use Redis as a broker and a result store
- The Huey settings are on the production settings file
- The `tasks.py` file is used to define tasks (similar to celery's tasks.py file)
- The decorator `@huey.task` and `@huey.periodic_task` are used to define tasks

### Static and Media Files

- We use whitenoise to serve static files
- There is no setting for media files, but cloudinary settings are present as comments in the production settings file

### Important Notes

- Don't commit `.env` file, settings will read from railway environment variables
- To create a superuser install railway cli and run `railway run python manage.py createsuperuser`
- Split into apps as much as possible
- project templates and static folders are inside the project folder rather than outside

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/AcACbH?referralCode=NC4Tt6)