from .base import *  # We import everything we have previously set up on base.py
 
def get_secret(the_secret, debugging):
    """
    As a security measure, all secrets will be kept in a json file named
    secrets.json. This file will not be managed by the version control
    system, but will be available in our documentation repository or
    as an attached file. The main goal of this is that this file should
    not be viewable by no one except us or our team.
    """
    try:
        secrets_file = os.path.join(BASE_DIR, 'settings', 'secrets.json')

        secretjson = json.load(open(secrets_file))
        if debugging:
            return secretjson['local'][the_secret]
        else:
            return secretjson['production'][the_secret]
    except Exception as e:
        print("Something weird happened while retrieving a secret: {}".format(e))
        sys.exit(-1)
 
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
 
ALLOWED_HOSTS = ['.gizmoapp.com', 'localhost', '127.0.0.1', '[::1]'] 

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
 
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_secret('SECRET_KEY', DEBUG)

# Dev Email
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025

AUTHY_API_KEY = get_secret('AUTHY_API_KEY', DEBUG)
