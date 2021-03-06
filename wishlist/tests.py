from blue import app
import unittest
import json

# Constants

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

    #Ensure that about page was set up correctly
    def test_index(self):
        tester = app.test_client(self)
        tester.post(
            '/login',
            data=dict(email="Manny@hdsalkfjal",password="12345678"),
            follow_redirects=True)
        response = tester.get('/about', content_type='html/text')
        self.assertEqual(response.status_code, 200)
    
    #Test about page is loading
    def test_index_page(self):
        tester = app.test_client(self)
        tester.post(
            '/login',
            data=dict(email="Manny@hdsalkfjal",password="12345678"),
            follow_redirects=True)
        response = tester.get('/about', content_type='html/text')
        self.assertTrue(b'Tired of forgetting book recommendations?' in response.data)
    
    #Ensure that My Books page was set up correctly
    def test_index(self):
        tester = app.test_client(self)
        tester.post(
            '/login',
            data=dict(email="Manny@hdsalkfjal",password="12345678"),
            follow_redirects=True)
        response = tester.get('/list', content_type='html/text')
        self.assertEqual(response.status_code, 200)
    
    #Test My Books page is loading
    def test_index_page(self):
        tester = app.test_client(self)
        tester.post(
            '/login',
            data=dict(email="Manny@hdsalkfjal",password="12345678"),
            follow_redirects=True)
        response = tester.get('/list', content_type='html/text')
        self.assertTrue(b'Books' in response.data)

############################## API TEST ########################################
    #Ensure login behaives correctly
    def test_check_login(self):
        tester = app.test_client(self)
        response = tester.post(
            'user/check_login',
            data=json.dumps(dict(email="Manny@hdsalkfjal",password_candidate="12345678")),
            follow_redirects=True,content_type='application/json')
        self.assertEqual(response.content_type, 'application/json')

    #Ensure that we can retrive all books
    def test_all_book_status(self):
        tester = app.test_client(self)
        response = tester.get('/book?id=2')
        self.assertEqual(response.content_type, 'text/html; charset=utf-8')

    #Ensure that we can retrive all books     
    def test_all_books(self):
        tester = app.test_client(self)
        response = tester.get('/book?id=2', follow_redirects=True)
        self.assertIn(b'"author": "Unknown"', response.data)

    #Ensure that we can retrive one book
    def test_book_status(self):
        tester = app.test_client(self)
        response = tester.get('/book/2')
        self.assertEqual(response.content_type, 'application/json')

   #Ensure that we can retrive one book
    def test_book(self):
        tester = app.test_client(self)
        response = tester.get('/book/2')
        self.assertIn(b'"title": "Scarlet Letter"', response.data)

    #Ensure that we can update a book
    def test_update_book_status(self):
        tester = app.test_client(self)
        tester.put(
            '/book/14',
            data=json.dumps(dict(isbn="7926410343", title="Dubmo 2", author="Steven spils", date="1998")),
            follow_redirects=True, content_type='application/json')
        response = tester.get('/book/14')
        self.assertEqual(response.content_type, 'application/json')

    #Ensure that we can update a book    
    def test_update_book(self):
        tester = app.test_client(self)
        tester.put(
            '/book/14',
            data=json.dumps(dict(isbn="7926410434", title="Dubmo 2", author="Steven spils", date="1998")),
            follow_redirects=True, content_type='application/json')
        response = tester.get('/book/14')
        self.assertIn(b'"title": "Dubmo 2"', response.data)

    # #Ensure that we can delete a book
    # def test_delete_book_status(self):
    #     tester = app.test_client(self)
    #     response = tester.delete('/book/6')
    #     self.assertEqual(response.content_type, 'application/json')

    # #Ensure that we can delete a book    
    # def test_delete_book(self):
    #     tester = app.test_client(self)
    #     response = tester.delete('/book/6', follow_redirects=True)
    #     self.assertIn(b'"author": "Potter"', response.data)

    #Ensure that we can create a book
    def test_create_book_status(self):
        tester = app.test_client(self)
        tester.post('/book', 
            data=json.dumps(dict(isbn="019374692", title="NEW BOOK", author="Steven spils", date="1998", userId="3")),
            follow_redirects=True, content_type='application/json')
        response = tester.get('/book/15', follow_redirects=True)
        self.assertEqual(response.content_type, 'application/json')

    #Ensure that we can create a book    
    def test_create_book(self):
        tester = app.test_client(self)
        tester.post('/book', 
            data=json.dumps(dict(isbn="019374692", title="NEW BOOK", author="Steven spils", date="1998", userId="3")),
            follow_redirects=True, content_type='application/json')
        response = tester.get('/book/15', follow_redirects=True)
        self.assertIn(b'"author": "Steven spils"', response.data)

    # #Ensure that we can create a user
    # def test_create_user_status(self):
    #     tester = app.test_client(self)
    #     response = tester.get('/book')
    #     self.assertEqual(response.content_type, 'application/json')

    # #Ensure that we can create a user    
    # def test_create_user(self):
    #     tester = app.test_client(self)
    #     response = tester.get('/book', follow_redirects=True)
    #     self.assertIn(b'"author": "Potter"', response.data)

if __name__ == '__main__':
    unittest.main()