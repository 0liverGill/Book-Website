import os
import unittest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app import app, db, models
from app.models import User, Genre, Book

class TestCase(unittest.TestCase):
	def setUp(self):
		app.config.from_object('config')
		app.config['TESTING'] = True
		app.config['WTF_CSRF_ENABLED'] = False
		#the basedir lines could be added like the original db
		app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
		self.app = app.test_client()
		db.create_all()
		pass


	def tearDown(self):
		db.session.remove()
		db.drop_all()

	def testUser(self):
		user = User(userName='testUser1',password = '123four')
		db.session.add(user)
	try:
		
		db.session.commit()
	except:
		db.session.rollback()
		print("error adding to database")

	
	def signUp(self,userName,password):
		return self.app.post('/signUp',
		data = dict(userName=userName, password=password),follow_redirects=True)
	def changePass(self,userName,oldPassword,newPassword):
		return self.app.post('/changePassword',
		data = dict(userName=userName, oldPassword=oldPassword,newPassword=newPassword),follow_redirects=True)
	def logIn(self,userName,password):
		return self.app.post('/login',
		data = dict(userName=userName, password=password),follow_redirects=True)

	def newBook(self,bookName,bookRating,bookNotes,dateFinished):
		return self.app.post('/newbook',
		data = dict(bookName=bookName, bookRating=bookRating,bookNotes=bookNotes,dateFinished=dateFinished),follow_redirects=True)

	def newGenre(self,genreName,genreDescription):
		return self.app.post('/newgenre',
		data = dict(genreName=genreName, genreDescription=genreDescription),follow_redirects=False)



    #test that certain webpages are restricted if not logged in
	def test_restricted(self):
		response = self.app.get('/viewbooks',
		follow_redirects=True)
		self.assertEqual(response.status_code, 401)

    #the next two test that the login and sign up pages are available always
	def test_login(self):
		response = self.app.get('/login',
		follow_redirects=True)
		self.assertEqual(response.status_code, 200)

	def test_signup(self):
		response = self.app.get('/signUp',
		follow_redirects=True)
		self.assertEqual(response.status_code, 200)

	



	def test_correctSignUp(self):
				
		login = self.signUp('testUser1','123four')
		#checks the database has been updated with the new user
		self.assertEqual(User.query.first().userName, 'testUser1')
		self.assertEqual(User.query.first().password, '123four')
	#tests sign up but with special characters, since users like to put in special characters for passwords	
	def test_correctSignUpBoundary(self):
			
		login = self.signUp('-1','%$£"^&*(l %^()')
	
		self.assertEqual(User.query.first().userName, '-1')
		self.assertEqual(User.query.first().password, '%$£"^&*(l %^()')

	def test_correctChangePass(self):
		
		user = User(userName='testUser1',password = '123four')
		db.session.add(user)

		try:
			db.session.commit()
		except:
			db.session.rollback()
			print("error adding to database")
		changepass = self.changePass('testUser1','123four','passwordNew')
		#checks the database has been updated with the new user
		self.assertEqual(User.query.first().userName, 'testUser1')
		self.assertEqual(User.query.first().password, 'passwordNew')
	def test_incorrectChangePass(self):
		
		user = User(userName='testUser1',password = '123four')
		db.session.add(user)

		try:
			db.session.commit()
		except:
			db.session.rollback()
			print("error adding to database")
		changepass = self.changePass('testUser1','123fourandmore','passwordNew')
		self.assertNotEqual(User.query.first().password, 'passwordNew')
	#tests correct and incorrect log in
	def test_correctLogin(self):
		
		user = User(userName='testUser1',password = '123four')
		db.session.add(user)

		try:
			db.session.commit()
		except:
			db.session.rollback()
			print("error adding to database")

		
		login = self.logIn('testUser1','123four')

		#checks they can access previousley forbidden pages
		self.assertEqual(login.status_code, 200)
		response = self.app.get('/newbook',
		follow_redirects=True)
		self.assertEqual(response.status_code, 200)
		#checks the logged in message comes through
		self.assertIn(b'logged in',login.data)

	#checks for unuathurized user, boundry case where password is correct but username isnt
	def test_incorrectLogin(self):
		
		user = User(userName='testUser1',password = '123four')
		db.session.add(user)
		try:
			db.session.commit()
		except:
			db.session.rollback()
			print("error adding to database")

		login = self.logIn('testUser2','123four')
		#self.assertEqual(login.status_code, 400)
		self.assertNotIn(b'logged in',login.data)
	

	#tests a new book can be created, boundary case with a large number
	def test_correctNewBook(self):
		
		user = User(userName='testUser1',password = '123four')
		db.session.add(user)
		try:
			db.session.commit()
		except:
			db.session.rollback()
			print("error adding to database")

		login = self.logIn('testUser1','123four')
		#self.assertEqual(login.status_code, 400)
		newbook = self.newBook('book1','999999999','It was Good','2022-12-07')
		
		self.assertIn(b'New Book Created',newbook.data)
		self.assertEqual(Book.query.first().bookName, 'book1')
		self.assertEqual(Book.query.first().bookRating, 999999999)
	#checks if the form can be input if there are empty required fields
	def test_incorrectNewBook(self):
		
		user = User(userName='testUser1',password = '123four')
		db.session.add(user)
		try:
			db.session.commit()
		except:
			db.session.rollback()
			print("error adding to database")

		login = self.logIn('testUser1','123four')
		#self.assertEqual(login.status_code, 400)
		newbook = self.newBook('book2','7','','2022-12-07')
		self.assertEqual(newbook.status_code, 200)
		self.assertNotIn(b'New Book Created',newbook.data)

	#checks a new genre can be submitted and added to database
	def test_correctNewGenre(self):
			
			user = User(userName='testUser1',password = '123four')
			db.session.add(user)
			try:
				db.session.commit()
			except:
				db.session.rollback()
				print("error adding to database")

			login = self.logIn('testUser1','123four')
			#self.assertEqual(login.status_code, 400)
			newgenre = self.newGenre('fantasy','speculative fiction involving magic')
			self.assertEqual(Genre.query.first().genreName, 'fantasy')
	#tests that a genre cannot be made if missing fields
	def test_incorrectNewGenre(self):
			
			user = User(userName='testUser1',password = '123four')
			db.session.add(user)
			try:
				db.session.commit()
			except:
				db.session.rollback()
				print("error adding to database")

			login = self.logIn('testUser1','123four')
			#self.assertEqual(login.status_code, 400)
			newgenre = self.newGenre('','speculative fiction involving magic')
			self.assertEqual(Genre.query.all(), [])
	#checks the database can be queried for book info
	def test_bookquery(self):
		user = User(userName='testUser3',password = '123')
		genre1 = Genre(genreName="genre1",genreDescription="no1")
		genre2 = Genre(genreName="genre2",genreDescription="no2")
		
		
	
		db.session.add(user)
		db.session.add(genre1)
		db.session.add(genre2)
		try:
			db.session.commit()
		except:
			db.session.rollback()
	
		
		
		book1 = Book(bookName = "testBook01",bookRating="103",bookNotes="it was not very good")#,dateFinished = '2019-10-10')
		book2 = Book(bookName = "testBook02",bookRating="103",bookNotes="it was very good")#,dateFinished = '2019-10-11')
		book1.bookReader = User.query.filter_by(userName='testUser3').first().userName
		book2.bookReader = User.query.filter_by(userName='testUser3').first().userName
		book1.genres.append(Genre.query.filter_by(genreName='genre1').first())
		book1.genres.append(Genre.query.filter_by(genreName='genre2').first())
		book2.genres.append(Genre.query.filter_by(genreName='genre2').first())
		db.session.add(book1)
		db.session.add(book2)
		
		db.session.commit()
		
		bookArray = Book.query.filter_by(bookReader=user.userName).all()
		self.assertEqual(bookArray[0].bookName, 'testBook01')
		self.assertEqual(bookArray[0].bookRating, 103)
		self.assertEqual(str(bookArray[0].genres), '[<Genre genre1>, <Genre genre2>]')
		
		self.assertEqual(bookArray[1].bookName, 'testBook02')
		self.assertEqual(bookArray[1].bookNotes, 'it was very good')
		self.assertEqual(str(bookArray[1].genres), '[<Genre genre2>]')

	#checks the database can be queried for genre info
	def test_genrequery(self):
		user = User(userName='testUser3',password = '123')
		genre1 = Genre(genreName="genre1",genreDescription="no1")
		genre2 = Genre(genreName="genre2",genreDescription="no2")
		
		
	
		db.session.add(user)
		db.session.add(genre1)
		db.session.add(genre2)
		try:
			db.session.commit()
		except:
			db.session.rollback()
	
		
		
		book1 = Book(bookName = "testBook01",bookRating="103",bookNotes="it was not very good")
		book2 = Book(bookName = "testBook02",bookRating="103",bookNotes="it was very good")
		book1.bookReader = User.query.filter_by(userName='testUser3').first().userName
		book2.bookReader = User.query.filter_by(userName='testUser3').first().userName
		book1.genres.append(Genre.query.filter_by(genreName='genre1').first())
		book1.genres.append(Genre.query.filter_by(genreName='genre2').first())
		book2.genres.append(Genre.query.filter_by(genreName='genre2').first())
		db.session.add(book1)
		db.session.commit()
		db.session.add(book2)
		db.session.commit()
		
		
		genreArray = Genre.query.all()	
		self.assertEqual(genreArray[0].genreName, 'genre1')
		self.assertEqual(genreArray[0].genreDescription, 'no1')
		self.assertEqual(str(genreArray[0].books), '[<Book testBook01>]')
		
		self.assertEqual(genreArray[1].genreName, 'genre2')
		self.assertEqual(genreArray[1].genreDescription, 'no2')
		self.assertEqual(str(genreArray[1].books), '[<Book testBook01>, <Book testBook02>]')













if __name__ == '__main__':
	unittest.main()
