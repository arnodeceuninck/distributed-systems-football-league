from flask import Blueprint, jsonify, request, render_template
#from project.api.models import User
from project import db
from sqlalchemy import exc
from project.api.models import Referee

referees_blueprint = Blueprint('referees', __name__, template_folder='./templates')


@referees_blueprint.route('/referees/ping', methods=['GET'])
def pint_pong():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })


@referees_blueprint.route('/referees', methods=['POST'])
def add_referee():
    post_data = request.form
    response_object = {
        'status': 'fail',
        'message': 'Invalid payload.'
    }
    if not post_data:
        return jsonify(response_object), 400
    firstname = post_data.get("firstname")
    lastname = post_data.get("lastname")
    address = post_data.get("address")
    zip = post_data.get("zip")
    city = post_data.get("city")
    phone = post_data.get("phone")
    email = post_data.get("email")
    birthday = post_data.get("birthday")
    try:
        referee = Referee(firstname=firstname, lastname=lastname, address=address, zip=zip, city=city, phone=phone, email=email, birthday=birthday)
        db.session.add(referee)
        db.session.commit()
        response_object = {
            'status': 'success',
            'message': f'{referee.firstname} {referee.lastname} was added!'
        }
        return jsonify(response_object), 201
    except exc.IntegrityError as e:
        db.session.rollback()
        return jsonify(response_object), 400


@referees_blueprint.route('/referees/<referee_id>', methods=['GET'])
def get_single_referee(referee_id):
    response_object = {
        'status': 'fail',
        'message': 'Referee does not exist'
    }
    try:
        referee = Referee.query.get(referee_id)
        if not referee:
            return jsonify(response_object), 404
        else:
            response_object = {
                'status': 'success',
                'data': referee.to_json()
            }
            return jsonify(response_object), 200
    except (ValueError, exc.DataError):
        return jsonify(response_object), 404

@referees_blueprint.route('/referees', methods=['GET'])
def get_all_referees():
    """Get all referees"""
    response_object = {
        'status': 'success',
        'data': {'referees': [referee.to_json() for referee in Referee.query.all()]}
    }
    return jsonify(response_object), 200


@referees_blueprint.route('/referees/<obj_id>', methods=['PUT'])
def update_obj(obj_id):
    response_object = {
        'status': 'fail',
        'message': 'Object does not exist'
    }
    try:
        obj = Referee.query.get(obj_id)
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


@referees_blueprint.route('/referees/<obj_id>', methods=['DELETE'])
def delete_obj(obj_id):
    response_object = {
        'status': 'fail',
        'message': 'Object does not exist'
    }
    try:
        Referee.query.filter_by(id=obj_id).delete()
        db.session.commit()
        response_object = {
            'status': 'success'
        }
        return jsonify(response_object), 200
    except (ValueError, exc.DataError):
        return jsonify(response_object), 404
