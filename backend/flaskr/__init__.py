import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [questions.format() for questions in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    @app.route("/questions", methods=["POST"])
    def create_question():
        body = request.get_json()
        keyword = body.get("searchTerm", None)
        if keyword is not None:
            selection = Question.query.filter(Question.question.ilike(f"%{keyword}%")).all()
            questions = paginate_questions(request, selection)
            return jsonify({
                "success": True,
                "questions": questions,
                "total_questions": len(selection)
            })
        try:
            question = body["question"]
            answer = body["answer"]
            category = body["category"]
            difficulty = body["difficulty"]
            new_question = Question(question=question, answer=answer, category=category,
                                    difficulty=difficulty)
            new_question.insert()
            return jsonify({"success": True})
        except KeyError:
            abort(400)
        except:
            abort(422)

    @app.route("/questions")
    def questions():
        selection = Question.query.all()
        questions = paginate_questions(request, selection)
        if len(questions) == 0:
            abort(404)
        return jsonify(
            {
                "success": True,
                "categories": {category.id: category.type for category in Category.query.all()},
                "questions": questions,
                "total_questions": len(selection)
            }
        )

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        question = Question.query.filter(Question.id == question_id).one_or_none()
        if question is None:
            abort(404)
        try:
            question.delete()
            return jsonify(
                {
                    "success": True,
                    "deleted": question_id
                }
            )
        except:
            abort(422)

    @app.route("/categories")
    def get_categories():
        categories = Category.query.all()
        categories = {category.id: category.type for category in categories}
        return jsonify({
            "success": True,
            "categories": categories
        })

    @app.route("/categories/<int:category_id>/questions")
    def get_category_questions(category_id):
        category = Category.query.filter(Category.id == category_id).one_or_none()
        if category is None:
            abort(404)
        selection = Question.query.filter(Question.category == category_id).all()
        questions = paginate_questions(request, selection)
        return jsonify({
            "success": True,
            "questions": questions,
            "total_questions": len(selection),
            "currentCategory": category.type
        })

    @app.route("/quizzes", methods=["POST"])
    def quiz():
        try:
            json_body = request.get_json()
            previous_questions = json_body["previous_questions"]
            category_id = int(json_body["quiz_category"]["id"])
            if category_id > 0:
                question = Question.query.filter(Question.category == category_id) \
                    .filter(Question.id.not_in(previous_questions)).first()
            else:
                question = Question.query.filter(Question.id.not_in(previous_questions)).first()
            if question is None:
                return jsonify({
                    "success": True
                })
            return jsonify({
                "success": True,
                "question": question.format()
            })
        except KeyError:
            abort(400)
        except Exception as e:
            print(e)
            abort(422)

    @app.errorhandler(400)
    def bad_request(error):
        return (
            jsonify({"success": False, "error": 400, "message": "Bad request"}),
            400,
        )

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "Resource not found"}),
            404,
        )

    @app.errorhandler(405)
    def method_not_allowed(error):
        return (
            jsonify({"success": False, "error": 405, "message": "Method not allowed"}),
            405
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "Unprocessable"}),
            422,
        )

    return app
