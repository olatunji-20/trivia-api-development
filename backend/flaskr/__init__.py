import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_quests(request, selection):
    page = request.args.get("page", 1, type=int)
    begin = (page - 1) * QUESTIONS_PER_PAGE
    end = begin + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[begin:end]

    return current_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: DONE Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={r"/api/*": {"origins":"*"}})

    """
    @TODO: DONE Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
        response.headers.add("Access-Control-Allow-Methods", "GET, PATCH, POST, DELETE, OPTIONS")
        return response

    """
    @TODO: DONE
    Create an endpoint to handle GET requests
    for all available categories.
    """

    @app.route("/categories", methods=["GET"])
    def get_categories():


        categories = Category.query.order_by(Category.id).all()

        if len(categories) == 0:
            abort(404)

        return jsonify({
            "success": True,
            "categories": {item.id: item.type for item in categories}
        })


    """
    @TODO:DONE
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.route("/questions", methods=["GET"])
    def get_questions():
                
        categories = Category.query.order_by(Category.id).all()
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_quests(request, selection)

        try:
            if len(selection) == 0:
                abort(404)

            return jsonify({
                "success": True,
                "questions": current_questions,
                "total_questions": len(selection),
                "categories": {item.id: item.type for item in categories},
                "current_category": "all"
            })

        except:
            abort(404)

    """
    @TODO:DONE
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):

        try:
            question = Question.query.filter(Question.id == question_id)

            question.delete()

            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_quests(request, selection)

            return jsonify({
                "success": True,
                "deleted": question_id,
                "remaining_questions": current_questions,
                "total_questions": len(selection)
            })
        
        except:
            abort(405)


    """
    @TODO: CHECK
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    @app.route("/questions", methods=["POST"])
    def create_question():

        body = request.get_json()

        try:
            new_question = request.get("question", None)
            new_answer = request.get("answer", None)
            new_category = request.get("category", None)
            new_difficulty = request.get("difficulty", None)

            question = Question(question=new_question, answer=new_answer, category=new_category, 
            difficulty=new_difficulty)
            
            question.insert()

            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_quests(request, selection)

            return jsonify({
                "success": True,
                "created": question.id,
                "all_questions": current_questions,
                "total_questions": len(selection)
            })

        except:
            abort(422)


    """
    @TODO: CHECK
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    @app.route("/questions/search", methods=["POST"])
    def search_question(search):

        body = request.get_json()

        search = body.get("search", None)

        try:
            # search_item = request.args.get("search")
            results = Question.query.order_by(Question.id).filter(Question.question.ilike("%{}%".format(search)))

            found_questions = paginate_quests(request, results)


            return jsonify({
                "success": True,
                "questions": found_questions,
                "total_questions": len(results)       
            })

        except:
            abort(400)



    """
    @TODO:DONE
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    @app.route("/categories/<int:category_id>/questions", methods=["GET"])
    def get_question_category(category_id):

        selection = Question.query.filter(Question.category == category_id).all()
        category_questions = paginate_quests(request, selection)

        try:
            return jsonify({
                "success": True,
                "questions": category_questions,
                "total_questions": len(selection),
                "current_category": category_id
            })

        except:
            abort(404)

    """
    @TODO: CHECK
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    CCCCCCCCCCCC
    """ 

    @app.route("/quizzes", methods=["POST"])
    def get_quiz_questions():

        try:
            body = request.get_json()

            new_category = body.get('quiz_category')
            past_questions = body.get('previous_questions')

            category_id = new_category['id']

            if category_id == 0:
                questions = Question.query.filter(Question.id.notin_(past_questions), 
                Question.category == category_id).all()

            else:
                questions = Question.query.filter(Question.id.notin_(past_questions), 
                Question.category == category_id).all()

            question = None
            if(questions):
                question = random.choice(questions)

            return jsonify({
                'success': True,
                'question': question.format()
            })

        except:
            abort(422)

    """
    @TODO:DONE
    Create error handlers for all expected errors
    including 404 and 422.
    """

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "BAD REQUEST"
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "RESOURCE NOT FOUND"
        }), 404

    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "METHOD NOT ALLOWED"
        }), 405

    @app.errorhandler(422)
    def unprocessed(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "CANT BE PROCESSED"
        }), 422




    @app.route("/")
    def home_page():
        return "WELCOME FALANA SHERIFF OLATUNJI"



    return app

