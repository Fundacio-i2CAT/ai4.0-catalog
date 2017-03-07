import sys
import os

sys.path.insert(0, '/home/ubuntu/catalog')
os.chdir("/home/ubuntu/catalog")

from wsgi import app as application

