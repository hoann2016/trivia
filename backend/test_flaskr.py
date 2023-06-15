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
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            "student", "student", "localhost:5432", self.database_name
        )
        setup_db(self.app, self.database_path)

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

    def test_get_category(self):
        response = self.client().get("/categories")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(len(data["categories"]) >= 0, True)

    def test_category_not_found(self):
        response = self.client().get("/categories/100")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_get_questions_pagination(self):
        response = self.client().get("/questions")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["total_questions"] >= 0, True)
        self.assertEqual(len(data["categories"]) >= 0, True)

    def test_get_question_with_invalid_page(self):
        response = self.client().get("/questions?page=99")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)

    def test_delete_question(self):
        new_question = Question(
            question="new question?", answer="new answer.", difficulty=1, category=1
        )
        new_question.insert()
        new_id_inserted = new_question.id

        response = self.client().delete(f"/questions/{new_id_inserted}")

        data = json.loads(response.data)
        question_inserted = Question.query.filter(
            Question.id == new_id_inserted
        ).first()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["deleted"], new_id_inserted)
        self.assertEqual(question_inserted, None)

    def test_delete_none_existing_question(self):
        new_question = Question(
            question="new question?", answer="new answer.", difficulty=1, category=1
        )
        new_question.insert()
        none_existing_question_id = new_question.id + 1

        response = self.client().delete(f"/questions/{none_existing_question_id}")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unable process")

    def test_add_new_question(self):
        new_question = {
            "question": "new question ?",
            "answer": "new answer.",
            "difficulty": 1,
            "category": 1,
        }

        response = self.client().post("/questions", json=new_question)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["created"] >= 0, True)

    def test_add_question_mising_properties(self):
        new_question = {
            "question": "new question ?",
            "answer": "new answer.",
            "category": 1,
        }

        response = self.client().post("/questions", json=new_question)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unable process")

    def test_search_question(self):
        search_obj = {"searchTerm": "e"}
        response = self.client().post("/questions/search", json=search_obj)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(len(data["questions"]) >= 0, True)
        self.assertEqual(data["total_questions"] >= 0, True)

    def test_search_not_found(self):
        search_obj = {"searchTerm": ""}
        response = self.client().post("/questions/search", json=search_obj)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_get_questions_by_category(self):
        response = self.client().get("/categories/1/questions")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(len(data["questions"]) >= 0, True)
        self.assertEqual(data["total_questions"] >= 0, True)
        self.assertEqual(data["current_category"] == 1, True)

    def test_404_get_item_by_category(self):
        response = self.client().get("/categories/abc/questions")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_quiz(self):
        quiz_obj = {
            "previous_questions": [],
            "quiz_category": {"type": "Entertainment", "id": 5},
        }

        response = self.client().post("/quizzes", json=quiz_obj)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_404_quizz(self):
        quiz_obj = {"previous_questions": []}

        response = self.client().post("/quizzes", json=quiz_obj)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data["success"], False)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
