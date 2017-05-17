**Gizmo - a Small project to test out Authy 2FA**
----------

Application to test out Regular authentication and Twilio Authy (SoftToken/OneTouch)

Built with:

 - **Django**
 - **authy-python**
 - **jQuery** (Mainly for Semantic UI functionality and some AJAX Requests)
 - **Semantic UI** (For fast front end prototyping)

Hosted on [heroku](https://gizmoapp.herokuapp.com).

----------

### Overview:

#### User Stories:

 Create a simple sign-up form and add validation:

 - Validate and sanitise inputs

 - Use any secure password hashing

 - Create user table to store user credentials

Create user sign-in form and add validation:

- Validate and sanitise inputs

- Match password using the secure hash

Add Two-factor Authentication to the sign-in using Authy (https://www.twilio.com/authy):

- Authentication via SoftToken from Authy App

- Authentication using Authy OneTouch

#### Code

For all user authentications **accounts app** was created. 

**Simple user sign up and sign in**

For the first two user cases (simple sign up and sign in) default Django authentication system was used. The code is available on **"localdev_standart_django_auth"** branch. 
For authentication, Django provides certain [views](https://docs.djangoproject.com/en/1.11/topics/auth/default/#all-authentication-views) and templates for this views, which can be overridden. Template overrides for this views were created in account app. Django also provides the forms for Login, Register, Password Reset/Change actions. User passwords use [PBKDF2](https://docs.djangoproject.com/en/1.11/topics/auth/passwords/#password-management-in-django) by default
in Django.

**Authentication via SoftToken**

For authy integration, [**authy-python**](https://github.com/authy/authy-python) was used.

For authy authentication, application also needs to capture user phone number (with country code). In order to keep the default User model simple, separate Profile model was created, which has OneToOne Relationship with User. Profile model stores authy id, country code and the phone number of the user. To capture this data, additional ModelForm was created from Profile Model and used in registration template. All fields on registration page were marked as mandatory and are validated. In case the validation fails, error messages are raised accordingly. Once the data passes the validation, user email, country code and phone number is sent to authy to create a new user. If user gets created successfully then a local user is created as well. Also User profile is created to store user provided data and returned authy_id. 

LoginView tests if user selected softtoken/sms or onetouch. Before proceeding with authy call, provided username and password is validated and checked against the existing user database. Depending on the result of this process, error messages get raised accordingly. After successful validation, LoginView checks which option of authy authentication was selected. For softtoken/sms a request is sent to authy API to send a token/sms to the user with given authy_id. After that user is redirected to **verify-sms** page. Also, authy_id is saved to sessions for later use. Once user enters the verification token, api call is sent to Authy to check the verification token for the given user with authy_id. If api call returns with success, user is logged in and redirected to the dashboard page. If not, error messages are raised to inform the user accordingly.

**Authentication via OneTouch**

LoginView first tests if user has a enabled device with Authy app, by sending a request to authy API. if user doesn't have enabled device with Authy app installed, then authentication falls back to sms/softtoken. If user has Authy app, then authy_id and uuid (returned back from API call) are saved in session and user gets redirected to **verify-onetouch** page. This page uses AJAX to test if user approved/denied the Authy request on the device. To verify the Authy approval, **authy_check** view was created. It sends a GET request to authy API and checks if the returned response has appropriate status message. Three actions are made depending on the returned status message:

 - status == "denied" - Alert box alerts the user that Request was denied and user gets redirerted to Login Page.
 - status == "pending" - AJAX call receives "pending" as a response and after short period of time sends a new AJAX call. AJAX calls are sent using setTimeout, until "denied" or "approved" is returned as a response. 
 - status == "approved" - User gets logged in by authy_check view and then user is redirected to dashboard page.

 **Logout**

 Logout flushes all the caches and logs out the user and redirects to Log out page. It uses the Django default authentication system. Overriden logout template is created inside account app.

----------

#### Local Tests and Heroku demo:

For Authy OneTouch/SoftToken tests, **Authy Chrome App** was used. 

**For Local Setup:**

- Install requirements from requirements/local.txt
 - whitenoise can be uninstalled if it's not required (it's recommended for heroku). Also, clear up wsgi.py to avoid any issues:
```
import os

from django.core.wsgi import get_wsgi_application

#Remove this
from whitenoise.django import DjangoWhiteNoise

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gizmo.settings")

application = get_wsgi_application()

#Remove this
application = DjangoWhiteNoise(application)
```
- Create a secrets.json file(rename secrets.json.example) and fill in the required keys and values.

- To test emails, **python -m smtpd -n -c DebuggingServer localhost:1025** can be run on a separate console. Port and host definitions are set in local.py.

**For Production Setup:**

Production:

 - setup the python runtime in runtime.txt
 - **requirements.txt** takes care of production requirement installs. 
 - Create env variables in Heroku for variables listed in settings/production.py: EMAIL_USER, EMAIL_PASS, SECRET_KEY, DATABASE_URL, ADMIN_USER, ADMIN_EMAIL.
 - Set DJANGO_SETTINGS_MODULE variable on heroku to gizmo.settings.production
 - add production url to ALLOWED_HOSTS.
 - Set ADMINS emails.
 - Install postgresql - **heroku addons:create heroku-postgresql:hobby-dev**
 - After pushing the code to heroku, use
    - **heroku run python gizmo/manage.py migrate --settings=gizmo.settings.production** to create the migrations
    - **heroku run python gizmo/manage.py createsuperuser --settings=gizmo.settings.production** to create new admin user
    - For error logs, use **heroku logs**. Emails to admins will be sent if any errors occur. Also, if emails aren't sent, DEBUG setting can be turned on (don't forget to disable it after debugging).
    - For SMTP Yandex mail was used. 

For admin url, check urls.py file. 

For [heroku demo](https://gizmoapp.herokuapp.com) app uses free Authy plan, so there will be a daily limitation for SMSs. 

#### Tests:
 - account/tests - for Business Logic tests on Django. External api requests for authy-python were mocked.

#### Front End Prototyping

UX/UI wasn't the main concern for this project, so for the fast frontend prototyping [Semantic UI](https://semantic-ui.com) framework was used. This framework also requires [jQuery](http://jquery.com), so that's why jQuery was also used to make the AJAX requests. All the external css and js files are called from [cdnjs.com](https://cdnjs.com). 

----------

#### Overall Results and Docs
All user cases were achieved. The App was built on Windows OS and demo app is hosted on Heroku(with free tier option). Authy-python library was a great help. The PyPi version didn't support python 3, so it was installed from Github. I had some issues with Django Debug Toolbar while creating the tests. That's why a separate settings file for tests was created in settings folder.
Further code refactoring can be made to reduce the repetitive code. Also, CSS can be rewritten to avoid big CSS file of Semantic UI. For js part, jQuery can be replaced with ZeptoJS or with native JavaScript ES6 (for AJAX calls fetch api or axios can be used)

The app was created thanks to this literature:

 - [Django Documentation](https://docs.djangoproject.com/en/1.11/topics/forms/modelforms/)
 - [Authy Documentation on Twilio](https://www.twilio.com/docs/api/authy)
 - [Authy Documentation on Authy website](http://docs.authy.com/api_docs.html)
 - [TWO-FACTOR AUTHENTICATION WITH AUTHY, PYTHON AND FLASK](https://www.twilio.com/docs/tutorials/two-factor-authentication-python-flask#send-the-onetouch-request)
 - [TWO-FACTOR AUTHENTICATION WITH AUTHY, PHP AND LARAVEL](https://www.twilio.com/docs/tutorials/two-factor-authentication-php-laravel)