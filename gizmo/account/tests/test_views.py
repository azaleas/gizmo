from unittest.mock import patch, MagicMock

from django.test import TestCase
from django.contrib.auth.models import User

from account.models import Profile

class DashboardViewTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username = "testuser",
            email = "test@test.com",
            password = "testuser"
        )
        self.profile = Profile.objects.create(
            user = self.user,
            country_code = "+971",
            phone_number = "581234567",
            authy_id = "12345"
        )

    # HELPER FUNCTIONS
    def forced_login(self):
        user = User.objects.get(username="testuser")
        self.client.force_login(user)

    def test_dashboard_not_logged_in(self):
        """
        Test that dashboard redirects to loging if not logged in
        """
        request = self.client.get('/')
        self.assertEqual(request.status_code, 302)
        self.assertEqual(request.url, "/login/?next=/")

    def test_dashboard_logged_in(self):
        """
        Test that dashboard returns proper status code and template 
        when logged in
        """
        self.forced_login()
        request = self.client.get('/')
        self.assertEqual(request.status_code, 200)
        self.assertTemplateUsed(request, 'account/dashboard.html')

    def test_login_with_token_redirect_to_verify_sms(self):
        """
        Test that user is redirected to verify-sms
        """
        with patch('account.views.client.users.request_sms') as mock_request_sms:
            request = self.client.post('/login/', {
                    'username': 'testuser',
                    'password': 'testuser',
                    'select_auth': 'token',
                })
            self.assertEqual(request.status_code, 302)
            self.assertEqual(request.url, "/verify-sms")

    def test_verify_sms(self):
        """
        Test that user logs in when proper token is sent
        """

        session = self.client.session
        session['user_auth_id'] = '12345'
        session.save()

        with patch('account.views.client.tokens.verify') as mock_request_token_verify:
            request = self.client.post('/verify-sms/',{
                    'sms_password': 12345,
                    'user_auth_id': '12345'
                })
            self.assertEqual(request.status_code, 302)
            self.assertEqual(request.url, "/")

            request_main = self.client.get('/')
            self.assertEqual(request_main.status_code, 200)
            self.assertContains(request_main, "Hola, testuser.")

    def test_login_with_onetouch_redirect_to_verify_onetouch(self):
        """
        Test that user is redirected to verify-onetouch when onetouch is enabled
        """
        with patch('account.views.requests') as mock_requests:
            mock_requests.post.return_value = mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"approval_request": {"uuid": "12345"}}
            request = self.client.post('/login/', {
                    'username': 'testuser',
                    'password': 'testuser',
                    'select_auth': 'onetouch',
                })
            self.assertEqual(request.status_code, 302)
            self.assertEqual(request.url, "/verify-onetouch")

    def test_authy_check(self):
        """
        Test that 'approved' message is sent to AJAX request
        when onetouch request is approved
        """

        session = self.client.session
        session['uuid'] = '12345'
        session['user_auth_id'] = '12345'
        session.save()

        with patch('account.views.requests') as mock_requests:
            mock_requests.get.return_value = mock_response = MagicMock()
            mock_response.status_code = 200
            json = {
                "approval_request": {
                    "uuid": "12345",
                    "_authy_id": "12345",
                    "status": "approved" 
                },
            }
            mock_response.json.return_value = json
            request = self.client.get('/authy-check/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            self.assertEqual(request.status_code, 200)
            self.assertEqual(request.content, b"approved")

    def test_register(self):
        """
        Test register view
        """

        with patch('account.views.client.users.create') as mock_requests:
            mock_requests.return_value.id = "12345"
            request = self.client.post('/register/',{
                    'username': 'testuser1',
                    'email': 'testuser1@testuser1.com',
                    'password': 'test12345',
                    'password2': 'test12345',
                    'country_code': '1',
                    'phone_number': '12345675',
                })
            user = User.objects.latest('id')
            self.assertEqual(request.status_code, 200)
            self.assertEqual(user.username, "testuser1")