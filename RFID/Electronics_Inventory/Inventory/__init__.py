from flask import Flask
from .views import createApp, load_data

# create app
app = createApp()
app.jinja_env.globals.update(zip=zip)
# Load data
load_data()

from . import urls
# Setup urls
urls.set_urls()
