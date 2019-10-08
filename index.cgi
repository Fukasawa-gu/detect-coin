#!/home/medalmarket/.pyenv/versions/3.4.2-flask/bin/python

import cgitb 
cgitb.enable()

from wsgiref.handlers import CGIHandler
from app import app 
CGIHandler().run(app)
