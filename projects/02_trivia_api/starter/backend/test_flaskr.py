import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category
from dotenv import load_dotenv

load_dotenv()

user_name = os.environ.get('USER')
password = os.environ.get('PASSWORD')


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format(user_name, password, 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)
        self.new_question = {
                                'question':  'Heres a new question string',
                                'answer':  'Heres a new answer string',
                                'difficulty': 1,
                                'category': 3,
                            }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertGreater(len(data['categories']), 0)


    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_404_beyond_valid_page(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource Not Found')
    
    def test_search_questions(self):
        res = self.client().post("/questions/search", json={"searchTerm": "title"})
        data = json.loads(res.data)
        

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['questions'])
    
    def test_search_with_no_results(self):
        search_term = {'searchTerm': 'thiscannotbefound'}
        res = self.client().post('/questions/search', json=search_term)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 0)

    def test_add_questions(self):
        before = Question.query.count()
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)
        after = Question.query.count()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertGreater(after, before)

    def test_422_empty_question(self):
        new_question = {
            'question': '',
            'answer': '',
            'dificulty': 1,
            'category': 1
        }

        res = self.client().post('/questions', json = new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable Entity')

    def test_questions_by_category(self):
        res = self.client().get('/categories/2/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])

    def test_question_by_category_fail(self):
        res = self.client().get('categories/1000/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource Not Found')

    def test_quizzes(self):
        res = self.client().post('/quizzes', json={'previous_questions': [20], 'quiz_category': {'id': 1, 'type': 'Science'}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])


    
    def test_delete_question(self):
        res = self.client().delete('/questions/13')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 13).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 13)
        self.assertEqual(question, None)

    def test_delete_question_that_not_exist(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable Entity')
        
    
 


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()