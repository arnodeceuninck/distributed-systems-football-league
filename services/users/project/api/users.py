from flask import Blueprint, jsonify, request, render_template
from project.api.models import User
from project import db
from sqlalchemy import exc

users_blueprint = Blueprint('users', __name__, template_folder='./templates')

@users_blueprint.route('/users/ping', methods=['GET'])
def ping_pong():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })

@users_blueprint.route('/users', methods=['POST'])
def add_user():
    post_data = request.form
    response_object = {
        'status': 'fail',
        'message': 'Invalid payload.'
    }
    if not post_data:
        return jsonify(response_object), 400
    username = post_data.get('username')
    password = post_data.get('password')
    team_id = post_data.get('team_id')
    type = post_data.get('type')
    try:
        user = User.query.filter_by(username=username).first()
        if not user:
            db.session.add(User(username=username, password=password, team_id=team_id, type=type))
            db.session.commit()
            response_object = {
                'status': 'success',
                'message': f'{username} was added!'
            }
            return jsonify(response_object), 201
        else:
            response_object['message'] = 'Sorry. That username already exists.'
            return jsonify(response_object), 400
    except exc.IntegrityError as e:
        db.session.rollback()
        return jsonify(response_object), 400


@users_blueprint.route('/users/<user_id>', methods=['GET'])
def get_single_user(user_id):
    response_object = {
        'status': 'fail',
        'message': 'User does not exist'
    }
    try:
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return jsonify(response_object), 404
        else:
            response_object = {
                'status': 'success',
                'data': user.to_json()
            }
            return jsonify(response_object), 200
    except (ValueError, exc.DataError):
        return jsonify(response_object), 404

@users_blueprint.route('/users/authenticate', methods=['POST'])
def authenticate():
    post_data = request.form
    response_object = {
        'status': 'fail',
        'message': 'Invalid payload.'
    }
    if not post_data:
        return jsonify(response_object), 400
    username = post_data.get('username')
    password = post_data.get('password')
    try:
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify(response_object), 404
        else:
            if user.password == password:
                response_object = {
                    'status': 'success',
                    'data': user.to_json()
                }
                return jsonify(response_object), 200
            else:
                return jsonify("Wrong password"), 400
    except (ValueError, exc.DataError) as e:
        raise e
        return jsonify(response_object), 404

@users_blueprint.route('/users', methods=['GET'])
def get_all_users():
    """Get all users"""
    response_object = {
        'status': 'success',
        'data': {'users': [user.to_json() for user in User.query.all()]}
    }
    return jsonify(response_object), 200

# @users_blueprint.route('/', methods=['GET'])
# def index():
#     if request.method == 'POST':
#         username = request.form['username']
#         email = request.form['email']
#         db.session.add(User(username=username, email=email))
#         db.session.commit()
#     users = User.query.all()
#     return render_template('index.html', users=users)

@users_blueprint.route('/users/<obj_id>', methods=['PUT'])
def update_obj(obj_id):
    response_object = {
        'status': 'fail',
        'message': 'Object does not exist'
    }
    try:
        obj = User.query.get(obj_id)
        if not obj:
            return jsonify(response_object), 404
        else:
            obj.update(request.form)
            db.session.commit()
            response_object = {
                'status': 'success'
            }
            return jsonify(response_object), 200
    except (ValueError, exc.DataError):
        return jsonify(response_object), 404


@users_blueprint.route('/users/<obj_id>', methods=['DELETE'])
def delete_obj(obj_id):
    response_object = {
        'status': 'fail',
        'message': 'Object does not exist'
    }
    try:
        User.query.filter_by(id=obj_id).delete()
        db.session.commit()
        response_object = {
            'status': 'success'
        }
        return jsonify(response_object), 200
    except (ValueError, exc.DataError):
        return jsonify(response_object), 404
