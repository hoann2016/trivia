import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

ITEMS_PER_PAGE = 10
def pagination(page_number,items):
    maximum_page = int(len(items)/ITEMS_PER_PAGE) + 1
    if page_number > maximum_page:
        return []
    from_index = (page_number - 1) *  ITEMS_PER_PAGE
    to_index = from_index + ITEMS_PER_PAGE
    return list(map(lambda item:item.format(), items[from_index: to_index]))

def get_category_dict(categories):
    categories_type = {}
    for category in categories:
        categories_type[category.id] = category.type
    return categories_type;
    
def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={'/': {'origins': '*'}})
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Headers","Content-Type,Authorization,true")
        response.headers.add("Access-Control-Allow-Methods", "GET,POST,DELETE,OPTION,PUT")
        return response
    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route("/categories")
    def get_categories():
        page = request.args.get('page', 1, type=int)
        categories = Category.query.order_by(Category.type).all()
        if len(categories) == 0:
            abort(404)
        return jsonify({
            "success": True,
            "categories": get_category_dict(categories)
        })
            

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions')
    def get_questions():        
        questions = Question.query.order_by(Question.id).all()
        categories = Category.query.order_by(Category.type).all()        
        page_number = request.args.get('page', 1, type = int)        
        question_result = pagination(page_number, questions)
        
        if len(question_result) == 0:
            abort(404)
        
        
        categories_type = get_category_dict(categories)
        return jsonify({
            'questions': question_result,
            'total_questions': len(questions),
            'success': True,
            'categories': categories_type
        })
        
    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route("/questions/<int:question_id>", methods = ["DELETE"])
    def delete_question_by_id(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).first()
            if question is None:
                abort(404)
            question.delete()
            return jsonify({
                "success":True,
                "deleted": question_id
            })            
            
        except:
            abort(422)
    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route("/questions", methods = ["POST"])
    def add_question():
        body = request.get_json()
        req_props = ["question","answer","difficulty","category"];
        
        if len(list(map(lambda x: x in body,req_props))) != len(req_props):
            abort(422)
        
        try:
            question = Question(question = body["question"],
                                answer = body["answer"], 
                                difficulty =  body["difficulty"], 
                                category = body["category"]
                               )
            question.insert()
            return jsonify({
                "success": True,
                "created":question.id
            })
        except Exception  as err:            
            abort(422)
      
            
    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route("/questions/search", methods = ["POST"])
    def search_question():
        body = request.get_json()
        if "searchTerm" in body and body["searchTerm"] != "":
            searchTerm = body["searchTerm"]
            found_items = Question.query.filter(Question.question.ilike('%' + searchTerm + '%')).all()
            questions = list(map(lambda item: item.format(), found_items))
            return jsonify({
                "success": True, 
                "questions": questions,
                "total_questions": len(questions)
            })
        abort(404)
    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route("/categories/<int:category_id>/questions", methods = ["GET"])
    def get_question_by_category_id(category_id):
        try:
            questions = Question.query.filter(Question.category == str(category_id)).all()
            questions_result = list(map(lambda item: item.format(), questions))
            return jsonify({
                "success": True, 
                "questions": questions_result,
                "total_questions": len(questions_result),
                "current_category": category_id
            })
        except:
            abort(404)
    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route("/quizzes", methods = ["POST"])
    def play_quizzes():
        try:
            body = request.get_json()
            
            if not(("previous_questions" in body) and ("quiz_category" in body)):
                abort(422)
                
            category = body["quiz_category"]
            previous_questions = body["previous_questions"]
            questions = []
            
            if category["type"] == "click":
                questions = Question.query.filter(Question.id.notin_(previous_questions)).all()
            else:
                questions = Question.query.filter_by(category = category["id"]).filter(Question.id.notin_(previous_questions)).all()
                
            total_question_result = len(questions)
            question_result = None
            
            if total_question_result > 0:
                random_number = random.randrange(0, total_question_result)
                question_result = list(map(lambda item: item.format(), questions))[random_number]
                
            return jsonify({
                "success": True,
                "question": question_result
            })
                
        except Exception as err:
            print('errors ',err)
            abort(422)
    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error_code):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "resource not found"
        }), 404
    
    @app.errorhandler(422)
    def unable_process(error_code):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unable process"
        }), 422
    
    return app
