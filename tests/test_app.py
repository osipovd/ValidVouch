import unittest
from app import app, db, User, Business
from flask import url_for

class BasicTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///test_db'
        app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
        cls.client = app.test_client()
        with app.app_context():
            db.create_all()

    @classmethod
    def tearDownClass(cls):
        with app.app_context():
            db.drop_all()

    def setUp(self):
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

        with self.app_context:
            db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def register_user(self):
        return self.client.post('/signup', data=dict(
            first_name='Test',
            last_name='User',
            dob='1990-01-01',
            address='123 Test St',
            city='Test City',
            state='TS',
            zip='12345',
            phone_number='1234567890',
            email='testuser@example.com',
            password='password',
            confirm_password='password',
            admin_code='Riddles9278!'
        ), follow_redirects=True)

    def login_user(self):
        return self.client.post('/login', data=dict(
            email='testuser@example.com',
            password='password'
        ), follow_redirects=True)

    def test_user_registration(self):
        response = self.register_user()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Account created successfully!', response.data)
        user = User.query.filter_by(email='testuser@example.com').first()
        self.assertIsNotNone(user)
        self.assertTrue(user.check_password('password'))

    def test_user_login(self):
        self.register_user()
        response = self.login_user()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You have been logged in!', response.data)

    def test_business_registration(self):
        self.register_user()
        self.login_user()

        response = self.client.post('/register-business', data=dict(
            business_name='Test Business',
            business_category='Restaurant',
            business_address='123 Business St',
            business_city='Business City',
            business_state='BC',
            business_zip='54321',
            business_description='A test business',
            business_phone='1234567890',
            business_website='http://testbusiness.com',
            time_zone='UTC'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Business registered successfully!', response.data)
        business = Business.query.filter_by(business_name='Test Business').first()
        self.assertIsNotNone(business)

    def test_edit_profile(self):
        self.register_user()
        self.login_user()

        response = self.client.post('/edit-profile', data=dict(
            first_name='Updated',
            last_name='User',
            dob='1990-01-01',
            address='123 Updated St',
            city='Updated City',
            state='UT',
            zip='67890',
            phone_number='0987654321',
            email='updateduser@example.com',
            new_password='newpassword',
            confirm_password='newpassword'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Your profile has been updated.', response.data)
        user = User.query.filter_by(email='updateduser@example.com').first()
        self.assertIsNotNone(user)
        self.assertTrue(user.check_password('newpassword'))

if __name__ == "__main__":
    unittest.main()





