import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://elizabeth:12345678@{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)
        self.question1 = {"question": "What is the capital city of Cameroon?",
                          "answer": "Yaounde", "category": 3, "difficulty": 1}
        self.question2 = {"question": "What is the capital city of Cameroon?", "category": 3, "difficulty": 1}
        self.question3 = {"searchTerm": "soccer"}
        self.quiz = {"previous_questions": [2, 4], "quiz_category": {"id": 5, "name": "Entertainment"}}

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_create_question(self):
        res = self.client().post("/questions", json=self.question1)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_create_question_failed(self):
        res = self.client().post("/questions", json=self.question2)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["message"], "Bad request")
        self.assertEqual(data["success"], False)

    def test_search(self):
        res = self.client().post("/questions", json=self.question3)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))
        self.assertEqual(data["success"], True)

    def test_get_questions(self):
        res = self.client().get("/questions?page=1")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["categories"]))
        self.assertTrue(len(data["questions"]))
        self.assertEqual(data["success"], True)

    def test_404_beyond_valid_page(self):
        res = self.client().get("/questions?page=540")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["message"], "Resource not found")
        self.assertEqual(data["success"], False)

    def test_delete_question(self):
        question_id = 17
        res = self.client().delete(f"/questions/{question_id}")
        data = json.loads(res.data)
        question = Question.query.filter(Question.id == question_id).first()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["deleted"], question_id)
        self.assertEqual(question, None)
        self.assertEqual(data["success"], True)

    def test_delete_question_not_found(self):
        res = self.client().delete("/questions/205")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["message"], "Resource not found")
        self.assertEqual(data["success"], False)

    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data["categories"]))
        self.assertEqual(data["success"], True)

    def test_get_category_questions(self):
        category_id = 4
        category = Category.query.get(category_id)
        res = self.client().get(f"/categories/{category_id}/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["currentCategory"], category.type)
        self.assertTrue(len(data["questions"]))
        self.assertTrue(data["total_questions"])
        self.assertEqual(data["success"], True)

    def test_category_not_found(self):
        category_id = 65
        res = self.client().get(f"/categories/{category_id}/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["message"], "Resource not found")
        self.assertEqual(data["success"], False)

    def test_get_quiz(self):
        res = self.client().post("/quizzes", json=self.quiz)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["question"]["id"], 6)
        self.assertTrue(data["question"])
        self.assertEqual(data["success"], True)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
