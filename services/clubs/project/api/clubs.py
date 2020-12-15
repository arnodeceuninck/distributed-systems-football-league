from flask import Blueprint, jsonify, request, render_template
from project.api.models import Club, Team
from project import db
from sqlalchemy import exc

clubs_blueprint = Blueprint('clubs', __name__, template_folder='./templates')


@clubs_blueprint.route('/clubs/ping', methods=['GET'])
def pint_pong():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })

@clubs_blueprint.route('/clubs', methods=['POST'])
def add_club():
    post_data = request.get_json()
    response_object = {
        'status': 'fail',
        'message': 'Invalid payload.'
    }
    if not post_data:
        return jsonify(response_object), 400
    stam_number = post_data.get("stam_number")
    name = post_data.get("name")
    address = post_data.get("address")
    zip = post_data.get("zip")
    city = post_data.get("city")
    website = post_data.get("website")
    try:
        club = Club.query.filter_by(stam_number=stam_number).first()
        if not club:
            club = Club(stam_number=stam_number, name=name, address=address, zip=zip, city=city, website=website)
            db.session.add(club)
            db.session.commit()
            response_object = {
                'status': 'success',
                'message': f'{club.stam_number} was added!'
            }
            return jsonify(response_object), 201
        else:
            response_object['message'] = 'Sorry. That stam number already exists.'
            return jsonify(response_object), 400
    except exc.IntegrityError as e:
        db.session.rollback()
        return jsonify(response_object), 400


@clubs_blueprint.route('/clubs/<club_id>', methods=['GET'])
def get_single_club(club_id):
    response_object = {
        'status': 'fail',
        'message': 'club does not exist'
    }
    try:
        club = Club.query.get(club_id)
        if not club:
            return jsonify(response_object), 404
        else:
            response_object = {
                'status': 'success',
                'data': club.to_json()
            }
            return jsonify(response_object), 200
    except (ValueError, exc.DataError):
        return jsonify(response_object), 404

@clubs_blueprint.route('/clubs/<club_id>/teams', methods=['GET'])
def get_teams_from_club(club_id):
    response_object = {
        'status': 'fail',
        'message': 'club does not exist'
    }
    try:
        club = Club.query.get(club_id)
        if not club:
            return jsonify(response_object), 404
        else:
            response_object = {
                'status': 'success',
                'data': {'teams': [club.to_json() for club in club.teams]}
            }
            return jsonify(response_object), 200
    except (ValueError, exc.DataError):
        return jsonify(response_object), 404


@clubs_blueprint.route('/clubs', methods=['GET'])
def get_all_clubs():
    """Get all clubs"""
    response_object = {
        'status': 'success',
        'data': {'clubs': [club.to_json() for club in Club.query.all()]}
    }
    return jsonify(response_object), 200


