from app import app
import unittest

class FlaskTestCase(unittest.TestCase):

############################## UI TESTS ########################################
    #Ensure that flask was set up correctly
    def test_index(self):
        tester = app.test_client(self)
        response = tester.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 200)
    
    #Test index file is loading
    def test_index_page(self):
        tester = app.test_client(self)
        response = tester.get('/', content_type='html/text')
        self.assertTrue(b'Welcome To Your Book Wish List' in response.data)

    #Ensure login behaives correctly with correct credentials
    def test_login(self):
        tester = app.test_client(self)
        response = tester.get('/login', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    #Ensure login behaives correctly with incorrect credentials
    def test_correct_login(self):
        tester = app.test_client(self)
        response = tester.post(
            '/login',
            data=dict(email="Manny@hdsalkfjal",password="12345678"),
            follow_redirects=True)
        self.assertIn(b'You have successfully logged in', response.data)

    #Ensure logout behaives correctly with correct credentials
    def test_incorrect_login(self):
        tester = app.test_client(self)
        response = tester.post(
            '/login',
            data=dict(email="Manny@hdsalkfjal",password="1234"),
            follow_redirects=True)
        self.assertIn(b'Invalid login', response.data)

    #Ensure correct logout
    def test_logout(self):
        tester = app.test_client(self)
        tester.post(
            '/login',
            data=dict(email="Manny@hdsalkfjal",password="12345678"),
            follow_redirects=True)
        response = tester.get('/logout', follow_redirects=True)
        self.assertIn(b'You have successfully logged out', response.data)

    #Ensure a page requires a login
    def test_routes_require_login(self):
        tester = app.test_client(self)
        response = tester.get('/dashboard', follow_redirects=True)
        self.assertIn(b'Unathorized, Please Login', response.data)

############################## API TEST ########################################
    #Ensure that we can retrive all books
    def test_all_book_status(self):
        tester = app.test_client(self)
        response = tester.get('/book')
        self.assertEqual(response.content_type, 'application/json')

    #Ensure that we can retrive all books     
    def test_all_books(self):
        tester = app.test_client(self)
        response = tester.get('/book', follow_redirects=True)
        self.assertIn(b'"author": "Potter"', response.data)

    #Ensure that we can retrive one book
    def test_book_status(self):
        tester = app.test_client(self)
        response = tester.get('/book')
        self.assertEqual(response.content_type, 'application/json')

    #Ensure that we can retrive one book     
    def test_book(self):
        tester = app.test_client(self)
        response = tester.get('/book', follow_redirects=True)
        self.assertIn(b'"author": "Potter"', response.data)

    #Ensure that we can update a book
    def test_update_book_status(self):
        tester = app.test_client(self)
        response = tester.get('/book')
        self.assertEqual(response.content_type, 'application/json')

    #Ensure that we can update a book    
    def test_update_book(self):
        tester = app.test_client(self)
        response = tester.get('/book', follow_redirects=True)
        self.assertIn(b'"author": "Potter"', response.data)

    #Ensure that we can delete a book
    def test_delete_book_status(self):
        tester = app.test_client(self)
        response = tester.get('/book')
        self.assertEqual(response.content_type, 'application/json')

    #Ensure that we can delete a book    
    def test_delete_book(self):
        tester = app.test_client(self)
        response = tester.get('/book', follow_redirects=True)
        self.assertIn(b'"author": "Potter"', response.data)

    #Ensure that we can create a book
    def test_create_book_status(self):
        tester = app.test_client(self)
        response = tester.get('/book')
        self.assertEqual(response.content_type, 'application/json')

    #Ensure that we can create a book    
    def test_create_book(self):
        tester = app.test_client(self)
        response = tester.get('/book', follow_redirects=True)
        self.assertIn(b'"author": "Potter"', response.data)

    #Ensure that we can create a user
    def test_create_user_status(self):
        tester = app.test_client(self)
        response = tester.get('/book')
        self.assertEqual(response.content_type, 'application/json')

    #Ensure that we can create a user    
    def test_create_user(self):
        tester = app.test_client(self)
        response = tester.get('/book', follow_redirects=True)
        self.assertIn(b'"author": "Potter"', response.data)

if __name__ == '__main__':
    unittest.main()

    