import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(selection, request):
  page = request.args.get("page", 1, type=int)
  start = (page-1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE
  current_questions = selection[start:end]
  return [question.format() for question in current_questions]

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)

  cors = CORS(app, resources={r"*": {"origins": "*"}}, support_credentials=True)

  @app.after_request
  def after_request(response):
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization,true")
    response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,PATCH,DELETE,OPTIONS")
    return response
  

  '''

  An endpoint to handle GET requests
  for all available categories.

  '''

  @app.route("/categories", methods=['GET'])
  def available_categories():
    try:
      categories=Category.query.order_by(Category.id).all()
      return jsonify({'success': True, 'categories': {category.id:category.type for category in categories}})
    except Exception as e:
      print(e)

  
  '''

  Handling GET request for questions, including pagination (as questions per page). Returns An object 
  with 10 paginated questions, total questions, object including all categories, and current category string.

  '''

  @app.route('/questions', methods=['GET'])
  def get_questions():
    try:
      questions = Question.query.order_by(Question.id).all()
      categories = Category.query.order_by(Category.id).all()
      current_questions = paginate_questions(questions, request)
      
      if len(current_questions) == 0:
        abort(404)

      return jsonify({
        'success': True,
        'questions': current_questions,
        'total_questions': len(questions),
        'categories': {category.id: category.type for category in categories},
        'current_category': None
      })
    except Exception as e:
      print(e)
   

    
  '''
  
  This endpoint  DELETE question using a question ID. 

  When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

  @app.route('/questions/<int:question_id>', methods=["DELETE"])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()
      
      if question is None:
        abort(404)

      question.delete()

      return jsonify ({
        'success': True,
        "deleted": question_id
      }), 200
    except Exception as e:
      abort(422)
      print(e)



  '''
  
  This is endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  

  '''

  @app.route('/questions', methods=['POST'])
  def add_question():
    body = request.get_json()
    question=body.get('question', None)
    answer=body.get('answer', None)

    try:
      if question and answer:
        question = Question(question=question, answer=answer, difficulty=body.get('difficulty', None), category=body.get('category', None))
        question.insert()
        return jsonify({'success': True})
      else:
        abort(422)

    except: 
      abort(422)


  '''
   
  This endpoint gets questions based on a search term. 
  It returns any questions for whom the search term 
  is a substring of the question. 

  Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 

  '''

  @app.route('/questions/search', methods=['POST'])
  def search_question():
    
    body = request.get_json()

    search_term = body.get("searchTerm", None)

    try:

      if search_term:
        questions = Question.query.order_by(Question.id).filter(Question.question.ilike("%{}%".format(search_term))).all()
        return jsonify({
          'success': True,
          'questions': [question.format() for question in questions],
          'total_questions': len(questions),
          'current_category': None,
        })

    except: 
      abort(422)

  '''

  This is a GET endpoint to get questions based on category. 

  In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 

  '''

  @app.route('/categories/<int:category_id>/questions', methods=["GET"])
  def questions_by_category(category_id):
    
    try:
      category_questions = Question.query.filter(Question.category == category_id).all()
      current_category = Category.query.filter(Category.id == category_id).one_or_none()
      return jsonify({
        'questions': [question.format() for question in category_questions],
        'total_questions': len(category_questions),
        'current_category': current_category.type,
        'success': True
      }), 200
    except:
      abort(404)


  '''
  This is a POST endpoint to get questions to play the quiz. 
  This endpoint takes category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def quiz_question():
    data = request.json
    prev_questions = data['previous_questions']
    current_category = data['quiz_category']['id']
    possible_ids = []

    try:
      if current_category == 0:
        questions = Question.query.all()
      else:
        questions= Question.query.filter(Question.category == current_category).all()
     

      for question in questions:
        if question.id not in prev_questions:
          possible_ids.append(question.id)
      

      if len(possible_ids) == 0:
        question = False
      else:
        choice = random.choice(possible_ids)
        question = Question.query.filter(Question.id == choice).one_or_none().format()
      
      return jsonify({'question': question,
                      'success': True  
                      }), 200

    except:
      abort(405)

  '''

  Here are error handlers for all expected errors 
  including 404 and 422. 

  '''

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False,
      "error": 400,
      "message": "Bad Request",
      "additional_information": error.description
    }), 400
    
  @app.errorhandler(404)
  def resource_not_found(error):
    return jsonify({
      "success": False,
      "error": 404,
      "message": "Resource Not Found",
      "additional_information": error.description
    }), 404

  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
      "success": False,
      "error": 405,
      "message": "Method Not Allowed",
      "additional_information": error.description
    }), 405

  @app.errorhandler(422)
  def unprocessable_entity(error):
    return jsonify({
      "success": False,
      "error": 422,
      "message": "Unprocessable Entity",
      "additional_information": error.description
    }), 422

  @app.errorhandler(500)
  def internal_server_error(error):
    return jsonify({
      "success": False,
      "error": 500,
      "message": "Internal Server Error",
      "additional_information": error.description
    }), 500


  return app

    