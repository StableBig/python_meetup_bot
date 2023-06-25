import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'python_meetup.settings')
django.setup()

from python_meetupbot.dispatcher import run_pooling

if __name__ == "__main__":
    run_pooling()
