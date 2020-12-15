from flask import Blueprint, jsonify, request, render_template
#from project.api.models import User
from project import db
from sqlalchemy import exc
from project.api.models import Match

matches_blueprint = Blueprint('matches', __name__, template_folder='./templates')


@matches_blueprint.route('/matches/ping', methods=['GET'])
def pint_pong():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })


@matches_blueprint.route('/matches', methods=['POST'])
def add_match():
    post_data = request.get_json()
    response_object = {
        'status': 'fail',
        'message': 'Invalid payload.'
    }
    if not post_data:
        return jsonify(response_object), 400
    division_id = post_data.get("division_id")
    matchweek = post_data.get("matchweek")
    date = post_data.get("date")
    time = post_data.get("time")
    home = post_data.get("home")
    away = post_data.get("away")
    status_id = post_data.get("status_id")
    goals_home = post_data.get("goals_home")
    goals_away = post_data.get("goals_away")

    try:
        match = Match(division_id=division_id, matchweek=matchweek, date=date, time=time, home=home, away=away, status_id=status_id, goals_home=goals_home, goals_away=goals_away)
        db.session.add(match)
        db.session.commit()
        response_object = {
            'status': 'success',
            'message': f'{match.id} was added!'
        }
        return jsonify(response_object), 201
    except (exc.IntegrityError, TypeError) as e:
        db.session.rollback()
        return jsonify(response_object), 400


@matches_blueprint.route('/matches/<match_id>', methods=['GET'])
def get_single_match(match_id):
    response_object = {
        'status': 'fail',
        'message': 'Match does not exist'
    }
    try:
        match = Match.query.get(match_id)
        if not match:
            return jsonify(response_object), 404
        else:
            response_object = {
                'status': 'success',
                'data': match.to_json()
            }
            return jsonify(response_object), 200
    except (ValueError, exc.DataError):
        return jsonify(response_object), 404

@matches_blueprint.route('/matches', methods=['GET'])
def get_all_matches():
    """Get all matches"""
    response_object = {
        'status': 'success',
        'data': {'matches': [match.to_json() for match in Match.query.all()]}
    }
    return jsonify(response_object), 200

@matches_blueprint.route('/matches/stats/<team_1>/vs/<team2>', methods=['GET'])
def get_match_stats(team1, team2):
    # TODO: Times played together, times winner, result previous 5 matches
    response_object = {
        'status': 'success',
        'data': {'matches': [match.to_json() for match in Match.query.all()]}
    }
    return jsonify(response_object), 200

