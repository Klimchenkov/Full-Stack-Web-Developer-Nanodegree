import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)
 
db_drop_and_create_all()

# ROUTES
'''
    GET /drinks endpoint
        it is a public endpoint
        it contains only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks', methods =['GET'])
def get_drinks():
    try:
        drinks = Drink.query.all()
        return jsonify({"success":True, "drinks": [drink.short() for drink in drinks]}), 200
    except:
        abort (404)

'''
    GET /drinks-detail endpoint
        it requires the 'get:drinks-detail' permission
        it contains the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks-detail', methods =['GET'])
@requires_auth(permission='get:drinks-detail')
def get_drinks_detail(payload):
    try:
        drinks = Drink.query.all()
        return jsonify({"success":True, "drinks": [drink.long() for drink in drinks]}), 200
    except:
        abort (404)

'''
    POST /drinks endpoint
        it creates a new row in the drinks table
        it requires the 'post:drinks' permission
        it contains the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth(permission='post:drinks')
def post_a_drink(payload):
    body = request.get_json()
    title = body.get('title', None)
    recipe = body.get('recipe', None)

    try:
        if title and recipe:
            drink = Drink(title = title, recipe = json.dumps(recipe))
            drink.insert()
            return jsonify({
                "success": True,
                "drinks": [drink.long()]
            }), 200
        else:
            abort(422)
    except Exception as e:
        print(e)
        abort(422)

'''
    PATCH /drinks/<id> endpoint
        where <id> is the existing model id
        it responds with a 404 error if <id> is not found
        it updates the corresponding row for <id>
        it requires the 'patch:drinks' permission
        it contains the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth(permission='patch:drinks')
def change_recipe(payload, drink_id):
    drink = Drink.query.get_or_404(drink_id)
    body = request.get_json()
    title = body.get('title', None)
    recipe = body.get('recipe', None)
    try:
        if title:
            drink.title = title
        if recipe:
            drink.recipe = json.dumps(recipe)

        drink.update()
        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        }), 200
    except Exception as e:
        print(e)
        abort(422)




'''
    DELETE /drinks/<id> endpoint
        where <id> is the existing model id
        it responds with a 404 error if <id> is not found
        it deletes the corresponding row for <id>
        it requires the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<int:drink_id>', methods =['DELETE'])
@requires_auth(permission='delete:drinks')
def delete_the_drink(payload, drink_id):
    drink = Drink.query.get_or_404(drink_id)
    try:
        drink.delete()
        return jsonify({
            'success': True,
            "delete": drink_id
        }), 200
    except Exception as e:
        print(e)
        abort(422)

# Error Handling

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



'''
error handler for AuthError
''' 

@app.errorhandler(AuthError)
def authorization_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response 


if __name__ == "__main__":
    app.debug = True
    app.run()
